from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional

class UserStatsBase(BaseModel):
    user_id: UUID4
    requests_count: int
    chats_count: int
    tokens_used: int
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
