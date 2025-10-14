import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.connection.connection import Connection
from app.expiring_dict import ExpiringDict
from app.redis_state import RedisState


class TestRedisState:
    """Test suite for RedisState class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.redis_state = RedisState()
        self.default_ip = "127.0.0.1"
        self.default_port = 12345
        self.is_closed_attr = 'is_closed'

    def test_initialization(self) -> None:
        """Test RedisState initialization with default and custom ExpiringDict."""
        # Test default initialization
        state = RedisState()
        assert isinstance(state.redis_variables, ExpiringDict)
        assert isinstance(state.connections, dict)
        assert len(state.connections) == 0

        # Test custom initialization
        custom_dict = ExpiringDict()
        custom_dict.set("test_key", "test_value")
        state_custom = RedisState(redis_variables=custom_dict)
        assert state_custom.redis_variables is custom_dict
        assert state_custom.redis_variables.get("test_key") == "test_value"

    @pytest.mark.asyncio
    async def test_add_connection(self) -> None:
        """Test adding new connections and duplicate handling."""
        # Test adding new connection
        connection = self._create_mock_connection()
        assert isinstance(connection, Connection)
        assert connection.peername in self.redis_state.connections
        assert len(self.redis_state.connections) == 1

        # Test duplicate connection replacement
        old_connection = connection
        old_connection.close = AsyncMock()
        
        with patch('asyncio.create_task') as mock_task:
            new_connection = self._create_mock_connection()
            mock_task.assert_called_once()
            
        assert self.redis_state.connections[new_connection.peername] is new_connection
        assert len(self.redis_state.connections) == 1

    @pytest.mark.asyncio
    async def test_purge_connection(self) -> None:
        """Test purging connections in various states."""
        # Setup connection
        connection = self._create_mock_connection()
        connection.close = AsyncMock()
        peername = connection.peername

        # Test normal purge (mock is_closed as False)
        with patch.object(connection, self.is_closed_attr, False):
            await self.redis_state.purge_connection(connection)
            assert peername not in self.redis_state.connections
            connection.close.assert_called_once()

        # Test purging already removed connection
        connection.close.reset_mock()
        with patch.object(connection, self.is_closed_attr, False):
            await self.redis_state.purge_connection(connection)
            connection.close.assert_called_once()

        # Test purging already closed connection
        connection2 = self._create_mock_connection(port=12346)
        connection2.close = AsyncMock()
        
        with patch.object(connection2, self.is_closed_attr, True):
            await self.redis_state.purge_connection(connection2)
            connection2.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_multiple_connections(self) -> None:
        """Test managing multiple connections simultaneously."""
        connections: list[Connection] = []
        for i in range(3):
            conn = self._create_mock_connection(port=12345 + i)
            conn.close = AsyncMock()
            connections.append(conn)

        assert len(self.redis_state.connections) == 3

        # Purge middle connection with mocked is_closed
        with patch.object(connections[1], self.is_closed_attr, False):
            await self.redis_state.purge_connection(connections[1])
        
        assert len(self.redis_state.connections) == 2
        assert connections[0].peername in self.redis_state.connections
        assert connections[1].peername not in self.redis_state.connections
        assert connections[2].peername in self.redis_state.connections

    def test_redis_variables_integration(self) -> None:
        """Test that redis_variables ExpiringDict works correctly."""
        self.redis_state.redis_variables.set("key1", "value1")
        self.redis_state.redis_variables.set("key2", "value2", expire_set_ms=1000)
        
        assert self.redis_state.redis_variables.get("key1") == "value1"
        assert self.redis_state.redis_variables.get("key2") == "value2"
        assert isinstance(self.redis_state.redis_variables, ExpiringDict)

    def _create_mock_connection(self, ip: str | None = None, port: int | None = None) -> Connection:
        """Helper method to create a mock connection."""
        reader = AsyncMock(spec=asyncio.StreamReader)
        writer = MagicMock(spec=asyncio.StreamWriter)
        writer.get_extra_info.return_value = (
            ip or self.default_ip,
            port or self.default_port
        )
        return self.redis_state.add_new_connection(reader, writer)