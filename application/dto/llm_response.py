from typing import Optional

from pydantic import BaseModel


class LLMResponse(BaseModel):
    success: bool
    provider: Optional[str] = None
    model: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
