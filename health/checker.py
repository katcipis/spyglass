import asyncio
from collections import namedtuple
from urllib.parse import urlparse

from health.probes import http_probe


HealthCheck = namedtuple(
    'HealthCheck',
    ['url', 'period_sec', 'patterns'],
    defaults=(None,),
)


class InvalidParamsError(Exception):
    pass


class HealthChecker:
    """
    Performs regular checks for healthiness.

    Given a set of HealthCheck descriptors it will
    probe them (through HTTP) regularly.
    """

    def __init__(self, handler, checks):
        """
        Creates a new HealthChecker.

        The provided checks must be an iterable of HealthCheck, including
        all the information required to do probing for healthiness.

        The provided handler must be a coroutine (awaitable) that will
        receive the as parameters:

        - url : The url that has been probed
        - status: A health.status.HealthStatus

        The handler will be responsible for handling results for all the
        provided health check targets.
        """
        if len(checks) == 0:
            raise InvalidParamsError(
                "HealthChecker needs at least one HealthCheck defined")

        for check in checks:
            try:
                res = urlparse(check.url)
                if res.scheme == "":
                    raise InvalidParamsError(
                        f"url '{check.url}' doesn't have an scheme")
                if res.netloc == "":
                    raise InvalidParamsError(
                        f"url '{check.url}' doesn't have an domain")
            except Exception as err:
                url = check.url
                raise InvalidParamsError(
                    f"can't parse health check url '{url}', err: '{err}'")
            if check.period_sec <= 0:
                psec = check.period_sec
                raise InvalidParamsError(
                    f"period_sec must be a positive value, got: {psec}")

        self.__checks = checks
        self.__handler = handler
        self.__run = False

    def start(self):
        """
        Starts to periodically check for healthiness.

        Calling it will start multiple asynchronous tasks that
        will periodically probe HTTP endpoints and call
        a handler with the results.

        Calling start on a checker that is already started
        will be ignored.
        """
        if self.__run:
            return

        self.__run = True

        for check in self.__checks:
            asyncio.create_task(self.__probe_scheduler(check))

    def stop(self):
        """
        Stops the periodical check for healthiness.

        Calling stop on a checker that is already stopped
        will be ignored.
        """
        self.__run = False

    async def __probe_scheduler(self, check):
        while self.__run:
            await asyncio.sleep(check.period_sec)
            status = await http_probe(check.url, check.patterns)
            await self.__handler(check.url, status)
