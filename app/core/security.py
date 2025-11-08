import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def _make_jwt(sub: str, expires: timedelta):
    now = datetime.now(timezone.utc)
    payload = {"sub": sub, "iat": now, "exp": now + expires}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

def create_access_token(sub: str):
    return _make_jwt(sub, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(sub: str):
    return _make_jwt(sub, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

def decode_jwt(token: str):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
