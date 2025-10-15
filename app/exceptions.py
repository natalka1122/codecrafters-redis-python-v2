# flake8: noqa: WPS202
class ItemNotFoundError(Exception):
    """Raised when the requested item is not found"""


class NeedMoreBytesError(Exception):
    """NeedMoreBytes"""


class ReaderClosedError(Exception):
    """Raised when trying to read from a closed reader."""


class WriterClosedError(Exception):
    """Raised when trying to write to a closed writer."""


class WrongRESPFormatError(Exception):
    """WrongRESPFormat"""


class StreamWrongIdError(Exception):
    """XaddWrongIDError"""


class StreamWrongOrderError(Exception):
    """XaddWrongIDError"""


class NoDataError(Exception):
    """NoDataError"""
