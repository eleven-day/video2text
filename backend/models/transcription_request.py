from pydantic import BaseModel, HttpUrl
from typing import Optional

class TranscriptionSettings(BaseModel):
    use_openai_api: bool = False
    language: str = "auto"

class TranscriptionRequest(BaseModel):
    url: HttpUrl
    settings: TranscriptionSettings
