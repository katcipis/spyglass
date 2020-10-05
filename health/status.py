from collections import namedtuple
from enum import Enum


class HealthErrorKind(Enum):
    UNKNOWN = 1
    HTTP = 2
    REGEX = 3
    TIMEOUT = 4


HealthError = namedtuple('HealthError', ['kind', 'details'])


HealthStatus = namedtuple('HealthStatus', [
    'healthy',
    'response_time_ms',
    'status_code',
    'error',
])
