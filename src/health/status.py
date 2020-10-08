from collections import namedtuple
from enum import IntEnum


class HealthErrorKind(IntEnum):
    UNKNOWN = 1
    HTTP = 2
    REGEX = 3
    TIMEOUT = 4


HealthError = namedtuple('HealthError', ['kind', 'details'])


HealthStatus = namedtuple('HealthStatus', [
    'timestamp',
    'healthy',
    'response_time_ms',
    'status_code',
    'error',
])
