import httpx


class RSSFetcher:
    def __init__(self, timeout: float = 10.0) -> None:
        self._client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "micro-news-aggregator/0.1"},
        )

    async def fetch(self, url: str) -> bytes:
        response = await self._client.get(url)
        response.raise_for_status()
        return response.content

    async def close(self) -> None:
        await self._client.aclose()
