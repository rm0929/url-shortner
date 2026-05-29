import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app


@pytest.mark.asyncio
async def test_health():
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
async def test_redirect_not_found():
    with patch("app.api.routes.resolve_url", return_value=None):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/nonexistent", follow_redirects=False)

    assert response.status_code == 404
