from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert
from datetime import datetime
from app.models.user_stats import UserStats


async def increment_requests(db: AsyncSession, user_id, tokens_used: int = 0):
    now = datetime.utcnow()
    result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
    stats = result.scalars().first()

    if stats:
        stmt = (
            update(UserStats)
            .where(UserStats.user_id == user_id)
            .values(
                requests_count=UserStats.requests_count + 1,
                tokens_used=UserStats.tokens_used + tokens_used,
                hourly_requests=UserStats.hourly_requests + 1,
                daily_requests=UserStats.daily_requests + 1,
                weekly_requests=UserStats.weekly_requests + 1,
                monthly_requests=UserStats.monthly_requests + 1,
                hourly_tokens=UserStats.hourly_tokens + tokens_used,
                daily_tokens=UserStats.daily_tokens + tokens_used,
                weekly_tokens=UserStats.weekly_tokens + tokens_used,
                monthly_tokens=UserStats.monthly_tokens + tokens_used,
                updated_at=now,
            )
        )
        await db.execute(stmt)
    else:
        await db.execute(
            insert(UserStats).values(
                user_id=user_id,
                requests_count=1,
                tokens_used=tokens_used,
                hourly_requests=1,
                daily_requests=1,
                weekly_requests=1,
                monthly_requests=1,
                hourly_tokens=tokens_used,
                daily_tokens=tokens_used,
                weekly_tokens=tokens_used,
                monthly_tokens=tokens_used,
                updated_at=now,
            )
        )
    await db.commit()
