from collections import namedtuple

HealthStatus = namedtuple('HealthStatus', ['healthy', 'response_time_ms', 'status_code'])
