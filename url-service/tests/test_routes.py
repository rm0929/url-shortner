import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock


with patch("redis.asyncio.from_url") as mock_redis:
    mock_redis.return_value = AsyncMock()
    from app.main import app


@pytest.mark.asyncio
async def test_health():
    """Health check must return 200 — no DB or Redis needed."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_shorten_url():
    mock_url = MagicMock()
    mock_url.short_code = "abc123"
    mock_url.original_url = "https://google.com"

    with patch("app.api.routes.get_db", return_value=AsyncMock()):
        with patch("app.api.routes.create_short_url", return_value=mock_url):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.post(
                    "/shorten", json={"url": "https://google.com"}
                )

    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert data["short_code"] == "abc123"


@pytest.mark.asyncio
async def test_redirect_found():
    with patch("app.api.routes.get_db", return_value=AsyncMock()):
        with patch("app.api.routes.resolve_url", return_value="https://google.com"):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/abc123", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["location"] == "https://google.com"


@pytest.mark.asyncio
async def test_redirect_not_found():
    with patch("app.api.routes.get_db", return_value=AsyncMock()):
        with patch("app.api.routes.resolve_url", return_value=None):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/nonexistent", follow_redirects=False)

    assert response.status_code == 404
