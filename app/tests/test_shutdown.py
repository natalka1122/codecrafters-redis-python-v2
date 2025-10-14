from asyncio import (
    CancelledError,
    Event,
    StreamReader,
    StreamWriter,
    Task,
    create_task,
    open_connection,
    wait_for,
)
from unittest.mock import AsyncMock, Mock

import pytest

from app.const import DEFAULT_PORT, LOCALHOST
from app.frontend import master_redis
from app.resp.array import Array
from app.resp.bulk_string import BulkString
from app.resp.simple_string import SimpleString
# from app.tests.conftest import RedisServerManager


# Test Classes
class TestEchoServer:
    """Test the echo server functionality"""

    @pytest.fixture
    def active_connections(self) -> set[Task[None]]:
        """Fixture providing an empty active connections set"""
        return set()

    # @pytest.fixture
    # def redis_state(self, find_free_port: Callable[[], int]) -> RedisState:
    #     """Fixture providing an empty active connections set"""
    #     redis_config = RedisConfig(port=find_free_port())
    #     return RedisState(redis_config=redis_config)

    @pytest.fixture
    def mock_writer(self) -> StreamWriter:
        """Mock StreamWriter for testing"""
        writer = Mock(spec=StreamWriter)
        writer.write = Mock()
        writer.drain = AsyncMock()
        writer.close = Mock()
        writer.wait_closed = AsyncMock()
        writer.get_extra_info = Mock(return_value=("127.0.0.1", 12345))
        return writer

    @pytest.fixture
    def mock_reader(self) -> Mock:
        """Mock StreamReader for testing"""
        reader = Mock(spec=StreamReader)
        return reader

    # @pytest.mark.asyncio
    # async def test_handle_echo_single_message(
    #     self,
    #     mock_reader: Mock,
    #     mock_writer: Mock,
    #     redis_state: RedisState,
    # ) -> None:
    #     """Test echoing a single message"""
    #     # Setup mock to return data once, then empty
    #     mock_reader.read = AsyncMock(side_effect=[Array([BulkString("PING")]).to_bytes, b""])

    #     await handle_client(mock_reader, mock_writer, redis_state=redis_state)

    #     # Verify the message was echoed back
    #     mock_writer.write.assert_called_once_with(SimpleString("PONG").to_bytes)
    #     mock_writer.drain.assert_called_once()
    #     mock_writer.close.assert_called_once()
    #     mock_writer.wait_closed.assert_called_once()

    # @pytest.mark.asyncio
    # async def test_handle_echo_multiple_messages(
    #     self, mock_reader: Mock, mock_writer: Mock, redis_state: RedisState
    # ) -> None:
    #     """Test echoing multiple messages"""
    #     messages = [
    #         Array([BulkString("PING")]).to_bytes,
    #         Array([BulkString("ECHO"), BulkString("aaa")]).to_bytes,
    #         Array([BulkString("ECHO"), BulkString("bbb")]).to_bytes,
    #         b"",
    #     ]
    #     expected_calls = (
    #         (SimpleString("PONG").to_bytes,),
    #         (BulkString("aaa").to_bytes,),
    #         (BulkString("bbb").to_bytes,),
    #     )
    #     mock_reader.read = AsyncMock(side_effect=messages)

    #     await handle_client(mock_reader, mock_writer, redis_state)

    #     # Verify all messages were echoed (excluding the empty one that ends the loop)
    #     assert mock_writer.write.call_count == 3
    #     actual_calls = [call.args for call in mock_writer.write.call_args_list]
    #     assert actual_calls == [args for args in expected_calls], (
    #         f"expected_calls = {expected_calls} actual_calls = {actual_calls}"
    #     )

    # @pytest.mark.asyncio
    # async def test_handle_echo_connection_tracking(
    #     self, mock_reader: Mock, mock_writer: Mock, redis_state: RedisState
    # ) -> None:
    #     """Test that connections are properly tracked and cleaned up"""
    #     active_connections: set[Task[None]] = set()
    #     mock_reader.read = AsyncMock(side_effect=[Array([BulkString("PING")]).to_bytes, b""])

    #     await handle_client(mock_reader, mock_writer, redis_state)

    #     # Connection should be removed after completion
    #     assert len(active_connections) == 0

    # @pytest.mark.asyncio
    # async def test_handle_echo_cancellation(
    #     self, mock_reader: Mock, mock_writer: Mock, redis_state: RedisState
    # ) -> None:
    #     """Test proper handling of cancellation"""
    #     # Mock reader to hang indefinitely, then cancel
    #     mock_reader.read = AsyncMock(side_effect=CancelledError())

    #     with pytest.raises(CancelledError):
    #         await handle_client(mock_reader, mock_writer, redis_state)

    #     # Verify cleanup still happened
    #     mock_writer.close.assert_called_once()
    #     mock_writer.wait_closed.assert_called_once()

    # # class TestWorker:
    # #     """Test the worker functionality"""

    @pytest.mark.asyncio
    async def test_worker_starts_and_stops(self) -> None:
        """Test that worker starts server and responds to shutdown"""
        shutdown_event = Event()
        started_event = Event()

        # Start worker in background
        worker_task: Task[None] = create_task(
            master_redis(
                started_event=started_event,
                shutdown_event=shutdown_event,
            )
        )
        try:
            await wait_for(started_event.wait(), timeout=5)
        except TimeoutError:
            worker_task.cancel()
            pytest.fail("Worker failed to start within timeout")

        # Signal shutdown
        shutdown_event.set()

        # Wait for worker to complete
        try:
            await wait_for(worker_task, timeout=1)
        except TimeoutError:
            worker_task.cancel()
            pytest.fail("Worker failed to stop within timeout")
        # If we reach here without hanging, the test passed

    @pytest.mark.asyncio
    async def test_worker_handles_cancellation(self) -> None:
        """Test that worker handles cancellation properly"""
        started_event = Event()
        shutdown_event = Event()

        worker_task = create_task(
            master_redis(
                started_event=started_event,
                shutdown_event=shutdown_event,
            )
        )
        try:
            await wait_for(started_event.wait(), timeout=5)
        except TimeoutError:
            worker_task.cancel()
            pytest.fail("Worker failed to start within timeout")

        # Cancel the worker
        worker_task.cancel()

        with pytest.raises(CancelledError):
            try:
                await wait_for(worker_task, timeout=1)
            except TimeoutError:
                pytest.fail("Worker failed to stop within timeout")

    @pytest.mark.asyncio
    async def test_worker_with_real_connection(self) -> None:
        """Integration test with real TCP connection"""
        started_event = Event()
        shutdown_event = Event()
        ping_bytes = Array([BulkString("PING")]).to_bytes
        pong_bytes = SimpleString("PONG").to_bytes
        master_task: Task[None] = create_task(
            master_redis(
                started_event=started_event,
                shutdown_event=shutdown_event,
            )
        )
        try:
            await wait_for(started_event.wait(), timeout=5)
        except TimeoutError:
            master_task.cancel()
            pytest.fail("Master failed to start within timeout")

        try:
            # Connect and send message
            first_reader, first_writer = await open_connection(LOCALHOST, DEFAULT_PORT)
            # Send test message
            first_writer.write(ping_bytes)
            await first_writer.drain()
            # Read response
            first_response = await first_reader.read(1024)
            assert first_response == pong_bytes

            second_reader, second_writer = await open_connection(
                LOCALHOST, DEFAULT_PORT
            )
            second_writer.write(ping_bytes)
            await second_writer.drain()
            # Read response
            second_response = await second_reader.read(1024)
            assert second_response == pong_bytes

            first_writer.close()
            await first_writer.wait_closed()

        finally:
            shutdown_event.set()
            await master_task

        assert await second_reader.read(1024) == b"", (
            "Expected empty response from closed connection"
        )
        second_writer.close()
        await second_writer.wait_closed()


#     @pytest.mark.asyncio
#     async def test_worker_replica(
#         self, tmp_path: pathlib.Path, server_manager: RedisServerManager, find_free_port: Callable[[], int]
#     ) -> None:
#         master_name = "master"
#         replica_name = "replica"
#         ping_bytes = Array([BulkString("PING")]).to_bytes
#         pong_bytes = SimpleString("PONG").to_bytes
#         master_port: int = find_free_port()
#         await server_manager.start_server(name=master_name, port=master_port, dir_name=str(tmp_path))
#         replica_port = find_free_port()
#         await server_manager.start_server(
#             name=replica_name,
#             port=replica_port,
#             dir_name=str(tmp_path),
#             replicaof=f"{LOCALHOST} {master_port}",
#         )
#         reader, writer = None, None
#         try:
#             # Connect and send message
#             reader, writer = await open_connection(LOCALHOST, master_port)

#             # Send test message
#             test_message = ping_bytes
#             writer.write(test_message)
#             await writer.drain()

#             # Read response
#             response = await reader.read(1024)
#             assert response == pong_bytes
#             await server_manager.stop_server(replica_name)

#             # Send test message
#             test_message = ping_bytes
#             writer.write(test_message)
#             await writer.drain()

#             # Read response
#             response = await reader.read(1024)
#             assert response == pong_bytes

#             await server_manager.start_server(
#                 name="replica",
#                 port=replica_port,
#                 dir_name=str(tmp_path),
#                 replicaof=f"{LOCALHOST} {master_port}",
#             )
#             # Send test message
#             test_message = ping_bytes
#             writer.write(test_message)
#             await writer.drain()

#             # Read response
#             response = await reader.read(1024)
#             assert response == pong_bytes
#             await server_manager.stop_server(master_name)
#             await sleep(1)
#             # Send test message
#             test_message = ping_bytes
#             writer.write(test_message)
#             await writer.drain()

#             # Read response
#             response = await reader.read(1024)
#             assert response == b""

#         finally:
#             # Close client connection
#             if writer is not None:
#                 writer.close()
#                 await writer.wait_closed()

#     @pytest.mark.asyncio
#     async def test_replica_only(
#         self, tmp_path: pathlib.Path, server_manager: RedisServerManager, find_free_port: Callable[[], int]
#     ) -> None:
#         ping_bytes = Array([BulkString("PING")]).to_bytes
#         pong_bytes = SimpleString("PONG").to_bytes
#         master_port = find_free_port()
#         replica_port = find_free_port()
#         await server_manager.start_server(
#             name="replica",
#             port=replica_port,
#             dir_name=str(tmp_path),
#             replicaof=f"{LOCALHOST} {master_port}",
#         )
#         # await sleep(100500)
#         reader, writer = None, None
#         try:
#             # Connect and send message
#             reader, writer = await open_connection(LOCALHOST, replica_port)

#             # Send test message
#             test_message = ping_bytes
#             writer.write(test_message)
#             await writer.drain()

#             # Read response
#             response = await reader.read(1024)
#             assert response == pong_bytes
#             await server_manager.stop_server("replica")
#         finally:
#             # Close client connection
#             if writer is not None:
#                 writer.close()
#                 await writer.wait_closed()


# class TestSignalHandling:
#     """Test signal handling functionality"""

#     def test_make_signal_handler(self) -> None:
#         """Test signal handler creation"""
#         shutdown_event = Event()
#         signal_handler = make_signal_handler(signal.SIGTERM, shutdown_event)

#         # Call the handler
#         signal_handler()

#         # Verify event was set
#         assert shutdown_event.is_set()

#     # # @patch("sys.platform", "linux")
#     # def test_setup_signal_handlers_unix(self) -> None:
#     #     """Test signal handler setup on Unix systems"""
#     #     loop = Mock()
#     #     shutdown_event = Event()

#     #     setup_signal_handlers(shutdown_event)

#     #     # Verify signal handlers were added to the loop
#     #     assert loop.add_signal_handler.call_count == 2

#     #     # Check that SIGINT and SIGTERM were handled
#     #     calls = loop.add_signal_handler.call_args_list
#     #     signals_handled = [call[0][0] for call in calls]
#     #     assert signal.SIGINT in signals_handled
#     #     assert signal.SIGTERM in signals_handled

#     # @patch("sys.platform", "win32")
#     # @patch("signal.signal")
#     # def test_setup_signal_handlers_windows(self, mock_signal: Mock) -> None:
#     #     """Test signal handler setup on Windows"""
#     #     loop = Mock()
#     #     shutdown_event = Event()

#     #     setup_signal_handlers(loop, shutdown_event)

#     #     # Verify signal.signal was called for both signals on Windows
#     #     assert mock_signal.call_count == 2

#     #     # Verify loop.add_signal_handler was NOT called on Windows
#     #     loop.add_signal_handler.assert_not_called()


# @pytest.mark.asyncio
# async def test_main_shutdown_flow(find_free_port: Callable[[], int]) -> None:
#     """Test that main properly coordinates shutdown"""
#     started_event = Event()
#     shutdown_event = Event()

#     # Start main in background
#     main_task = create_task(
#         redis_app(
#             redis_config=RedisConfig(port=find_free_port()),
#             started_event=started_event,
#             shutdown_event=shutdown_event,
#         )
#     )

#     try:
#         await wait_for(started_event.wait(), timeout=5)
#     except TimeoutError:
#         pytest.fail("Worker failed to start within timeout")

#     # Signal shutdown
#     shutdown_event.set()

#     # Wait for completion
#     await main_task

#     # If we reach here, shutdown completed successfully


# @pytest.mark.asyncio
# async def test_full_server_lifecycle(find_free_port: Callable[[], int]) -> None:
#     """Test complete server startup, operation, and shutdown"""
#     started_event = Event()
#     shutdown_event = Event()

#     port = find_free_port()
#     # Start main
#     redis_config = RedisConfig(port=port)
#     main_task = create_task(
#         redis_app(started_event=started_event, shutdown_event=shutdown_event, redis_config=redis_config)
#     )
#     try:
#         await wait_for(started_event.wait(), timeout=5)
#     except TimeoutError:
#         pytest.fail("Worker failed to start within timeout")

#     # Test connection to master
#     connections: list[tuple[StreamReader, StreamWriter]] = []
#     try:
#         reader, writer = await open_connection("127.0.0.1", port)
#         connections.append((reader, writer))

#         # Send test message
#         test_msg = Array([BulkString("PING")]).to_bytes
#         writer.write(test_msg)
#         await writer.drain()

#         # Verify echo
#         response = await reader.read(1024)
#         assert response == SimpleString("PONG").to_bytes
#     finally:
#         # Close all connections
#         for _, writer in connections:
#             writer.close()
#         await gather(*(w.wait_closed() for _, w in connections))

#         # Shutdown main
#         shutdown_event.set()
#         await main_task


# # Monkeypatch signal setup to avoid OS signals
# def fake_setup_signal_handlers(loop: AbstractEventLoop, shutdown_event: Event) -> None: ...


# # Replace redis_app() with a fake coroutine that sets shutdown_event and exits
# async def fake_redis_app(
#     shutdown_event: Event,
#     started_event: Event,
#     port: int = DEFAULT_PORT,
#     dir_name: str = DEFAULT_DIR,
#     dbfilename: str = DEFAULT_DBFILENAME,
#     replicaof: str = "",
# ) -> None:
#     started_event.set()
#     shutdown_event.set()


# # def test_run_completes(monkeypatch: Mock) -> None:
# #     monkeypatch.setattr(app_main, "setup_signal_handlers", fake_setup_signal_handlers)

# #     monkeypatch.setattr(app_main, "redis_app", fake_redis_app)
# #     monkeypatch.setattr(sys, "argv", ["app"])  # <-- Remove pytest args

# #     # Call run() synchronously
# #     app_main.main()  # This should return without hanging
