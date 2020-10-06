import asyncio
import pytest

from health.checker import HealthChecker
from health.checker import HealthCheck


@pytest.mark.asyncio
async def test_health_checker_probes_all_checks(httpx_mock):
    results = []
    async def results_handler(url, status):
        results.append((url, status))

    url1 = "http://test1"
    url2 = "http://test2"
    url3 = "http://test3"

    period1 = 0.01
    period2 = 0.05
    period3 = 0.1

    checker = HealthChecker(results_handler, [
        HealthCheck(url=url1, period_sec=period1, patterns=["res"]),
        HealthCheck(url=url2, period_sec=period2),
        HealthCheck(url=url3, period_sec=period3),
    ])

    httpx_mock.add_response(url=url1, method="GET", data="response")
    httpx_mock.add_response(url=url2, method="GET")
    httpx_mock.add_response(url=url3, method="GET")

    try:
        checker.start()
        max_time_skew_sec = 0.01
        max_period = max(period1, period2, period3)
        await asyncio.sleep(max_period + max_time_skew_sec)
    finally:
        checker.stop()


    results_urls = {}

    assert len(results) >= 3

    for res in results:
        url = res[0]
        status = res[1]

        assert status.healthy
        results_urls[url] = True

    assert results_urls[url1]
    assert results_urls[url2]
    assert results_urls[url3]
