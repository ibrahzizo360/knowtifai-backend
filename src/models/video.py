from pydantic import BaseModel
from typing import Optional


class VideoRequest(BaseModel):
    video_url: str
    title: Optional[str] = None