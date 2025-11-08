from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_jwt
from app.schemas.auth import RegisterIn, LoginIn, TokenPair, RefreshIn

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=TokenPair, status_code=201)
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    await db.commit()
    return TokenPair(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )

@router.post("/login", response_model=TokenPair)
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.email == payload.email))
    user = res.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenPair(
        access_token=create_access_token(user.email),
        refresh_token=create_refresh_token(user.email),
    )

@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshIn, db: AsyncSession = Depends(get_db)):
    try:
        data = decode_jwt(payload.refresh_token)
        email = data.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return TokenPair(
        access_token=create_access_token(email),
        refresh_token=create_refresh_token(email),
    )
