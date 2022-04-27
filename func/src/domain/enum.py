# Standards
from enum import IntEnum


class CodeResponse(IntEnum):
    SUCCESS = 0
    INVALID_PARAMS = 10
    PARTNERS_INVALID_API_URL = 20
    PARTNERS_ERROR_ON_API_REQUEST = 21
    JWT_INVALID = 30
    DATA_NOT_FOUND = 99
    INTERNAL_SERVER_ERROR = 100
