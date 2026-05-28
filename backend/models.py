from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    party: Optional[str] = None
    provider: str = "ollama"


class Citation(BaseModel):
    speaker: str
    party: str
    topic: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]