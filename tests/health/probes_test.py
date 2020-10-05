import time
import pytest
from pytest_httpx import to_response

from health.probes import http_probe
from health.status import HealthErrorKind


# Tests
# - connection timeout
# - DNS failure


@pytest.mark.asyncio
async def test_http_probe_success_on_2XX(httpx_mock):
    url = "http://test_http_probe_success"
    for status_code in range(200,300):
        httpx_mock.add_response(url=url, method="GET", status_code=status_code)
        res = await http_probe(url)
        errmsg = f"expected success with status code {status_code}"

        assert_healthy_result(res, status_code)


@pytest.mark.asyncio
async def test_http_probe_success_on_single_regex_match(httpx_mock):
    url = "http://test_http_probe_success_on_single_regex_match"
    response_body = "the response body"
    httpx_mock.add_response(url=url, method="GET", data=response_body)
    res = await http_probe(url, ["response"])

    assert_healthy_result(res)


@pytest.mark.asyncio
async def test_http_probe_success_on_multiple_regex_matches(httpx_mock):
    url = "http://test_http_probe_success_on_multiple_regex_matches"
    response_body = "the response body"
    httpx_mock.add_response(url=url, method="GET", data=response_body)
    res = await http_probe(url, ["response", "body", "the"])

    assert_healthy_result(res)


@pytest.mark.asyncio
async def test_http_probe_failure_on_single_regex_not_matching(httpx_mock):
    url = "http://test_http_probe_failure_on_single_regex_not_matching"
    response_body = "the response body"
    httpx_mock.add_response(url=url, method="GET", data=response_body)
    res = await http_probe(url, ["nomatch"])

    assert not res.healthy
    assert res.status_code == 200
    assert res.error.kind == HealthErrorKind.REGEX, errmsg
    assert len(res.error.details) == 1
    assert res.response_time_ms > 0

@pytest.mark.asyncio
async def test_http_probe_failure_on_one_of_multiple_regexes_not_matching(httpx_mock):
    url = "http://test_http_probe_failure_on_one_of_multiple_regexes_not_matching"
    response_body = "the response body"
    httpx_mock.add_response(url=url, method="GET", data=response_body)
    res = await http_probe(url, ["the", "nomatch", "body", "duh"])

    assert not res.healthy
    assert res.status_code == 200
    assert res.error.kind == HealthErrorKind.REGEX, errmsg
    assert len(res.error.details) == 2
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
        assert res.error.details == []
        assert res.response_time_ms > 0


@pytest.mark.asyncio
async def test_http_probe_has_response_time_in_ms(httpx_mock):
    response_delay_ms = 50
    response_delay_sec = response_delay_ms / 1000.0
    max_response_delay_msg = response_delay_ms + 10

    def delayed_response(*args, **kwargs):
        time.sleep(response_delay_sec)
        return to_response()

    url = "http://test_http_probe_has_response_time_in_ms"
    httpx_mock.add_callback(delayed_response, url=url, method="GET")
    res = await http_probe(url)

    assert_healthy_result(res)
    assert response_delay_ms <= res.response_time_ms <= max_response_delay_msg


def assert_healthy_result(res, status_code=200):
    assert res.healthy
    assert res.status_code == status_code
    assert res.error is None
    assert res.response_time_ms > 0
