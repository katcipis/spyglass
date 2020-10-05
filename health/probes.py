import time
import httpx

from health.status import HealthStatus
from health.status import HealthError
from health.status import HealthErrorKind


async def http_probe(url, patterns=None):
    """
    Probes an HTTP website for healthiness.

    Given an HTTP url like 'http://coolwebsite.com' will probe it
    for healthiness and return an health.status.HealthStatus indicating
    the result of the probing.

    No exceptions are raised, all errors are encapsulated as a HealthStatus
    result. Any 2XX result will be considered a success, any non 2XX result
    will be considered an error.

    Some kind of errors don't have an HTTP status code, like DNS failures or connectivity
    failures (and timeouts). In these scenarios the status code will be 0.
    Only errors that are of the kind HealthErrorKind.HTTP or
    HealthErrorKind.REGEX will have meaningful HTTP status codes.

    If any regexes are provided (an iterable of regexes) the response
    body of a successful response will be matched against each of the patterns,
    if any of them fail to match the response body it will be considered an error,
    but preserving the original http status code received on the response.
    """
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        r = await client.get(url)
        response_time_ms = (time.perf_counter() - start) * 1000

        if r.status_code >= 200 and r.status_code < 300:
            return HealthStatus(
                healthy=True,
                status_code=r.status_code,
                response_time_ms=response_time_ms,
                error=None,
            )

        return HealthStatus(
            healthy=False,
            status_code=r.status_code,
            response_time_ms=response_time_ms,
            error=HealthError(kind=HealthErrorKind.HTTP),
        )

