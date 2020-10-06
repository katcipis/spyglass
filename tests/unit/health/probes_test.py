import time
import pytest
import httpx
from datetime import datetime
from datetime import timezone
from datetime import timedelta

from pytest_httpx import to_response

from health.probes import http_probe
from health.status import HealthErrorKind


@pytest.mark.asyncio
async def test_http_probe_success_on_2XX(httpx_mock):
    url = "http://test_http_probe_success"
    for status_code in range(200, 300):
        httpx_mock.add_response(url=url, method="GET", status_code=status_code)
        res = await http_probe(url)

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
    assert res.error.kind == HealthErrorKind.REGEX
    assert len(res.error.details) == 1
    assert res.response_time_ms > 0

    assert_health_status_timestamp(res)


@pytest.mark.asyncio
async def test_http_probe_failure_on_multiple_regexes_not_matching(httpx_mock):
    url = "http://test_http_probe_failure_on_multiple_regexes_not_matching"
    response_body = "the response body"
    httpx_mock.add_response(url=url, method="GET", data=response_body)
    res = await http_probe(url, ["the", "nomatch", "body", "duh"])

    assert not res.healthy
    assert res.status_code == 200
    assert res.error.kind == HealthErrorKind.REGEX
    assert len(res.error.details) == 2
    assert res.response_time_ms > 0

    assert_health_status_timestamp(res)


@pytest.mark.asyncio
async def test_http_probe_failure_on_4XX_5XX(httpx_mock):
    url = "http://test_http_probe_failure"
    for status_code in range(400, 600):
        httpx_mock.add_response(url=url, method="GET", status_code=status_code)
        res = await http_probe(url)

        errmsg = f"expected failure with status code {status_code}"
        assert not res.healthy, errmsg
        assert res.status_code == status_code, errmsg
        assert res.error.kind == HealthErrorKind.HTTP, errmsg
        assert res.error.details == []
        assert res.response_time_ms > 0

        assert_health_status_timestamp(res)


@pytest.mark.asyncio
async def test_http_probe_fails_on_timeout(httpx_mock):

    def timeout_response(request, *args, **kwargs):
        raise httpx.TimeoutException("fake timeout error", request=request)

    url = "http://test_http_probe_has_response_time_in_ms"
    httpx_mock.add_callback(timeout_response, url=url, method="GET")
    res = await http_probe(url)

    assert not res.healthy
    assert res.error.kind == HealthErrorKind.TIMEOUT
    assert len(res.error.details) == 1
    assert res.response_time_ms == 0

    assert_health_status_timestamp(res)


@pytest.mark.asyncio
async def test_http_probe_fails_on_unknown_err(httpx_mock):

    def err_response(request, *args, **kwargs):
        raise Exception("fake unknow error")

    url = "http://test_http_probe_fails_on_unknown_err"
    httpx_mock.add_callback(err_response, url=url, method="GET")
    res = await http_probe(url)

    assert not res.healthy
    assert res.error.kind == HealthErrorKind.UNKNOWN
    assert len(res.error.details) == 1
    assert res.response_time_ms == 0

    assert_health_status_timestamp(res)


@pytest.mark.asyncio
async def test_http_probe_has_response_time_in_ms(httpx_mock):
    response_delay_ms = 50
    response_delay_sec = response_delay_ms / 1000.0
    max_response_delay_ms = response_delay_ms + 10

    def delayed_response(*args, **kwargs):
        time.sleep(response_delay_sec)
        return to_response()

    url = "http://test_http_probe_has_response_time_in_ms"
    httpx_mock.add_callback(delayed_response, url=url, method="GET")
    res = await http_probe(url)

    assert_healthy_result(res)
    assert response_delay_ms <= res.response_time_ms <= max_response_delay_ms


def assert_healthy_result(res, status_code=200):
    assert res.healthy
    assert res.status_code == status_code
    assert res.error is None
    assert res.response_time_ms > 0

    assert_health_status_timestamp(res)


def assert_health_status_timestamp(res):
    timestamp = res.timestamp

    assert timestamp.tzinfo is not None
    assert timestamp.tzinfo.utcoffset(timestamp) == timedelta(0)

    max_allowed_skew_ms = 10
    response_time_delta_ms = res.response_time_ms + max_allowed_skew_ms
    response_time_delta = timedelta(milliseconds=response_time_delta_ms)

    now = datetime.now(timezone.utc)
    expected_min_timestamp = now - response_time_delta
    expected_max_timestamp = now + response_time_delta

    assert expected_min_timestamp <= timestamp <= expected_max_timestamp
