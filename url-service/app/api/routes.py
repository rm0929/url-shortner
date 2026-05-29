from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl

from app.core.database import get_db
from app.core.config import settings
from app.services.url_service import create_short_url, resolve_url

router = APIRouter()


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    short_url: str
    short_code: str
    original_url: str


@router.get("/health")
async def health():
    return {"status": "ok", "service": "url-service"}


@router.post("/shorten", response_model=ShortenResponse)
async def shorten_url(request: ShortenRequest, db: AsyncSession = Depends(get_db)):
    """Create a short URL."""
    url = await create_short_url(str(request.url), db)
    return ShortenResponse(
        short_url=f"{settings.BASE_URL}/{url.short_code}",
        short_code=url.short_code,
        original_url=url.original_url,
    )


@router.get("/info/{short_code}")
async def url_info(short_code: str, db: AsyncSession = Depends(get_db)):
    """Get info about a short URL without redirecting."""
    original_url = await resolve_url(short_code, db)
    if not original_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return {"short_code": short_code, "original_url": original_url}


# Wildcard MUST be last — FastAPI matches routes top to bottom.
# Any GET route added above this line is safe; anything below would be unreachable.
@router.get("/{short_code}")
async def redirect_url(short_code: str, db: AsyncSession = Depends(get_db)):
    """Resolve short code and redirect. This is the hot path — optimised with Redis."""
    original_url = await resolve_url(short_code, db)
    if not original_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=original_url, status_code=302)
