import time
import pytest
from pytest_httpx import to_response

from health.probes import http_probe
from health.status import HealthErrorKind


# Tests
# - Regex matching (success/failure)
# - connection timeout
# - DNS failure

@pytest.mark.asyncio
async def test_http_probe_success_on_2XX(httpx_mock):
    url = "http://test_http_probe_success"
    for status_code in range(200,300):
        httpx_mock.add_response(url=url, method="GET", status_code=status_code)
        res = await http_probe(url)
        errmsg = f"expected success with status code {status_code}"

        assert res.healthy, errmsg
        assert res.status_code == status_code, errmsg
        assert res.error is None, errmsg
        assert res.response_time_ms > 0


@pytest.mark.asyncio
async def test_http_probe_failure_on_4XX_5XX(httpx_mock):
    url = "http://test_http_probe_failure"
    for status_code in range(400,600):
        httpx_mock.add_response(url=url, method="GET", status_code=status_code)
        res = await http_probe(url)

        assert not res.healthy, f"expected failure with status code {status_code}"
        assert res.status_code == status_code, f"expected failure with status code {status_code}"
        assert res.error.kind == HealthErrorKind.HTTP, errmsg
        assert res.response_time_ms > 0


@pytest.mark.asyncio
async def test_http_probe_has_response_time_in_ms(httpx_mock):
    response_delay_ms = 50
    response_delay_sec = response_delay_ms / 1000.0
    max_delay_ms = response_delay_ms * 2

    def delayed_response(*args, **kwargs):
        time.sleep(response_delay_sec)
        return to_response()

    url = "http://test_http_probe_has_response_time_in_ms"
    httpx_mock.add_callback(delayed_response, url=url, method="GET")
    res = await http_probe(url)

    assert res.healthy
    assert response_delay_ms <= res.response_time_ms <= max_delay_ms
    assert res.error is None, errmsg
