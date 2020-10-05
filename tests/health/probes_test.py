import time
import pytest
from pytest_httpx import to_response

from health.probes import http_probe


# Tests
# - 4XX responses
# - 5XX responses
# - Regex matching (success/failure)
# - connection timeout
# - DNS failure

@pytest.mark.asyncio
async def test_http_probe_success(httpx_mock):
    url = "http://test_http_probe_success"
    httpx_mock.add_response(url=url, method="GET")
    res = await http_probe(url)
    assert res.healthy


@pytest.mark.asyncio
async def test_http_probe_success_has_response_time_in_ms(httpx_mock):
    # WHY: It is hard to avoid flaky tests when dealing with time, but I had some
    # positive experiences in the past when working with confidence
    # intervals. Also worked with mocking time in main loops (NodeJS), it can work
    # well but sometimes it gets out of hand and also results on flaky tests.
    # It could be a broken approach to mocking time (side effects of mocking
    # that persisted across tests because other third party modules also
    # depended on time), anyway I don't feel like # I have a definitive answer
    # for this, but in this case I'm going with "no time mocking".
    response_delay_ms = 50
    response_delay_sec = response_delay_ms / 1000.0
    max_delay_ms = response_delay_ms * 2

    def delayed_response(*args, **kwargs):
        time.sleep(response_delay_sec)
        return to_response()

    url = "http://test_http_probe_success_has_response_time_in_ms"
    httpx_mock.add_callback(delayed_response, url=url, method="GET")
    res = await http_probe(url)
    assert res.healthy
    assert response_delay_ms <= res.response_time_ms <= max_delay_ms
