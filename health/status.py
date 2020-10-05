from collections import namedtuple
from enum import Enum

class HealthErrorKind(Enum):
    HTTP = 1
    REGEX = 2

HealthError = namedtuple('HealthError', ['kind', 'details'])

HealthStatus = namedtuple('HealthStatus', ['healthy', 'response_time_ms', 'status_code', 'error'])
