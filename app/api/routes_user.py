from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.user_stats import UserStats
from app.schemas.user import UserRead
from app.schemas.user_stats import UserStatsBase

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    return user


@router.get("/me/stats", response_model=UserStatsBase)
async def me_stats(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    res = await db.execute(select(UserStats).where(UserStats.user_id == user.id))
    stats = res.scalar_one_or_none()
    if not stats:
        return {
            "user_id": user.id,
            "requests_count": 0,
            "chats_count": 0,
            "tokens_used": 0,
            "updated_at": None,
        }
    return stats
