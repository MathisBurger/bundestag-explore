from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    party: Optional[str] = None


class Citation(BaseModel):
    speaker: str
    party: str
    topic: str
    text: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]