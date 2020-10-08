import asyncpg
import logging
from urllib.parse import urlparse

from health.status import HealthErrorKind


class PostgreSQLStoreError(Exception):
    pass


class PostgreSQLStore:
    "Stores health checks on a SQL database"

    def __init__(self, uri):
        self.__uri = uri
        self.__log = logging.getLogger(f"{__name__}.SQLStore")

    async def connect(self):
        self.__conn = await asyncpg.connect(self.__uri)

    async def save(self, url, health_status):
        if self.__conn is None:
            raise PostgreSQLStoreError(
                "trying to save but not connected to db")

        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path + parsed_url.query
        timestamp = health_status.timestamp.replace(tzinfo=None)

        try:
            if health_status.error is None:
                await self.__conn.execute('''
                    INSERT INTO spyglass_health_status(
                        timestamp,
                        website,
                        path,
                        healthy,
                        status_code,
                        response_time_ms
                        ) VALUES($1, $2, $3, $4, $5, $6)
                    ''', timestamp, domain, path,
                         health_status.healthy,
                         health_status.status_code,
                         health_status.response_time_ms)
                return

            # Not the nicest way to represent list of values... Probably
            # Almost out of time at this point :-(
            error_details = ",".join(health_status.error.details)
            error_kind = error_kind_to_db_enum(health_status.error.kind)

            await self.__conn.execute('''
                INSERT INTO spyglass_health_status(
                    timestamp,
                    website,
                    path,
                    healthy,
                    status_code,
                    response_time_ms,
                    error_kind,
                    error_details
                    ) VALUES($1, $2, $3, $4, $5, $6, $7, $8)
            ''', timestamp, domain, path,
                health_status.healthy,
                health_status.status_code,
                health_status.response_time_ms,
                error_kind,
                error_details)

        except asyncpg.exceptions.UniqueViolationError:
            self.__log.warning(
                f"discarding duplicated health status {url} {health_status}")

    async def disconnect(self):
        if self.__conn is None:
            return
        await self.__conn.close()
        self.__conn = None


def error_kind_to_db_enum(kind):
    if kind == HealthErrorKind.HTTP:
        return "http"
    if kind == HealthErrorKind.REGEX:
        return "regex"
    if kind == HealthErrorKind.TIMEOUT:
        return "timeout"
    return "unknown"
