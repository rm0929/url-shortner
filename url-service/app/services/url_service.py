import string
import random
import json
import boto3
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.url import URL
from app.core.redis import redis_client
from app.core.config import settings


def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def get_sqs_client():
    return boto3.client(
        "sqs",
        region_name=settings.AWS_DEFAULT_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_ENDPOINT_URL,
    )


async def create_short_url(original_url: str, db: AsyncSession) -> URL:
    # Generate unique short code
    short_code = generate_short_code()
    while await get_url_by_code(short_code, db):
        short_code = generate_short_code()

    url = URL(original_url=original_url, short_code=short_code)
    db.add(url)
    await db.commit()
    await db.refresh(url)

    # Cache in Redis
    await redis_client.setex(
        f"url:{short_code}",
        settings.CACHE_TTL_SECONDS,
        original_url,
    )

    return url


async def get_url_by_code(short_code: str, db: AsyncSession) -> URL | None:
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    return result.scalar_one_or_none()


async def resolve_url(short_code: str, db: AsyncSession) -> str | None:
    # 1. Check Redis cache first (fast path)
    cached = await redis_client.get(f"url:{short_code}")
    if cached:
        await publish_click_event(short_code, cache_hit=True)
        return cached

    # 2. Cache miss — hit the database
    url = await get_url_by_code(short_code, db)
    if not url:
        return None

    # 3. Repopulate cache
    await redis_client.setex(
        f"url:{short_code}",
        settings.CACHE_TTL_SECONDS,
        url.original_url,
    )

    await publish_click_event(short_code, cache_hit=False)
    return url.original_url


async def publish_click_event(short_code: str, cache_hit: bool = False):
    """Fire-and-forget: publish click to SQS for async analytics."""
    try:
        sqs = get_sqs_client()
        message = {
            "short_code": short_code,
            "timestamp": datetime.utcnow().isoformat(),
            "cache_hit": cache_hit,
        }
        sqs.send_message(
            QueueUrl=settings.SQS_QUEUE_URL,
            MessageBody=json.dumps(message),
        )
    except Exception as e:
        # Analytics failure must NEVER break redirects
        print(f"[WARN] Failed to publish click event: {e}")
