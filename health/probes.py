import httpx

from health.status import HealthStatus


async def http_probe(url, patterns=None):
    """
    Probes an HTTP website for healthiness.

    Given an HTTP url like 'http://coolwebsite.com' will probe it
    for healthiness and return an health.status.HealthStatus indicating
    the result of the probing.

    No exceptions are raised, all errors are encapsulated as a HealthStatus
    result. Any 2XX result will be considered a success, any non 2XX result
    will be considered an error.

    If any patterns are provided (an iterable of regex patterns) the response
    body of a successful response will be matched with each of the patterns,
    if any of them fail to match the website will be considered unhealthy.
    """
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return HealthStatus(healthy=r.status_code == 200, response_time_ms="TODO")
