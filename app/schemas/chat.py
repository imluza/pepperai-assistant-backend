from pydantic import BaseModel, UUID4
from typing import Optional, Literal

ThinkingType = Literal["low", "medium", "high"]

class ChatRequest(BaseModel):
    prompt: str
    chat_id: Optional[UUID4] = None
    thinking: Optional[ThinkingType] = "high"


class ChatResponse(BaseModel):
    chat_id: UUID4
    stream: str


class ChatCreate(BaseModel):
    title: str

class ChatRename(BaseModel):
    new_title: str
