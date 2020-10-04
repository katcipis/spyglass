import pytest

from health.probes import http_probe


@pytest.mark.asyncio
async def test_http_probe_success(httpx_mock):
    url = "http://test_http_probe_success"
    httpx_mock.add_response(url=url, method="GET")
    res = await http_probe(url)
    assert res
