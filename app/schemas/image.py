from pydantic import BaseModel

class ImageAnalyzeResponse(BaseModel):
    description: str
