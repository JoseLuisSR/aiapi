from typing import Optional

from pydantic import BaseModel, Field


class LLMRequest(BaseModel):
    provider: str = Field(
        ..., description="AI provider (OPENAI_API, GEMINI_API, CLAUDE_API)"
    )
    model: str = Field(..., description="Model name")
    prompt: str = Field(..., description="Prompt text")
    temperature: Optional[float] = Field(default=None, description="Temperature")
    top_p: Optional[float] = Field(default=None, description="Top P")
    top_k: Optional[int] = Field(default=None, description="Top K")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens")
