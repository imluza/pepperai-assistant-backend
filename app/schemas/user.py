from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    id: UUID4
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserWithStats(UserBase):
    requests_count: int
    chats_count: int
    tokens_used: int
    updated_at: Optional[datetime] = None
