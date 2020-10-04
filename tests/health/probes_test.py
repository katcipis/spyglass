import pytest

from health.probes import http_probe

@pytest.mark.asyncio
async def test_http_probe_success():
    res = await http_probe("http://google.com")
    assert res
