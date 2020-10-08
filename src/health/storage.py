import asyncpg
import logging
from urllib.parse import urlparse


class PostgreSQLStore:
    "Stores health checks on a SQL database"

    def __init__(self, uri):
        self.__uri = uri
        self.__log = logging.getLogger(f"{__name__}.SQLStore")


    async def connect(self):
        self.__conn = await asyncpg.connect(self.__uri)


    async def save(self, url, health_status):
        if self.__conn is None:
            raise PostgreSQLStoreError("trying to save but not connected to db")

        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path + parsed_url.query
        timestamp = health_status.timestamp.replace(tzinfo=None)

        # TODO: FIX DEFAULT TABLE NAME
        # response_time_ms integer,
        # error_kind       error_kind,
        # error_details    text,
        try:
            await self.__conn.execute('''
                INSERT INTO spyglass_health_status_test5(
                    timestamp,
                    website,
                    path,
                    healthy,
                    status_code
                    ) VALUES($1, $2, $3, $4, $5)
            ''', timestamp, domain, path,
                health_status.healthy,
                health_status.status_code,
            )
        except asyncpg.exceptions.UniqueViolationError:
            self.__log.warning(
                f"discarding duplicated health status {url} {status}")


    async def disconnect(self):
        if self.__conn is None:
            return
        await self.__conn.close()
        self.__conn = None
