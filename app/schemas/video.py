from typing import List
from pydantic import BaseModel

class FrameDescription(BaseModel):
    index: int
    text: str

class VideoAnalyzeResponse(BaseModel):
    summary: str
    frames: List[FrameDescription]
