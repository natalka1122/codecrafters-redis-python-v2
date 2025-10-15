from enum import Enum


class CommandType(Enum):
    PING = "PING"
    ECHO = "ECHO"
    GET = "GET"
    SET = "SET"
    CONFIG_GET = "CONFIG_GET"
    REPLCONF_CAPA = "REPLCONF_CAPA"
    REPLCONF_LP = "REPLCONF_LISTENING-PORT"
    REPLCONF_GETACK = "REPLCONF_GETACK"
    PSYNC = "PSYNC"
    INFO = "INFO"
    ACK = "ACK"
    WAIT = "WAIT"
    ERROR = "ERROR"
    RPUSH = "RPUSH"
    LPUSH = "LPUSH"
    LRANGE = "LRANGE"
    LLEN = "LLEN"
    LPOP = "LPOP"
    BLPOP = "BLPOP"
    TYPE = "TYPE"
