from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.core.security import decode_jwt
from sqlalchemy.ext.asyncio import AsyncSession

bearer = HTTPBearer(auto_error=False)

async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not creds:
        raise HTTPException(status_code=401, detail="No credentials")
    try:
        payload = decode_jwt(creds.credentials)
        email = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not email:
        raise HTTPException(status_code=401, detail="Missing subject")
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
