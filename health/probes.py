import httpx


async def http_probe(url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        return r.status_code == 200
