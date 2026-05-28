"""Data transfer objects for AI requests.

DESCRIPTION
Defines the `AIRequest` pydantic model used to validate incoming
AI generation requests.

EXAMPLES
>>> AIRequest(provider='OPENAI_API', model='gpt-4', prompt='Hello')
"""


from pydantic import BaseModel, Field


class AIRequest(BaseModel):
    """Pydantic model representing an AI generation request.

    DESCRIPTION
    The model contains the provider identifier, model name and the prompt
    together with optional generation parameters.

    ARGS
    provider: str
        AI provider identifier (e.g. OPENAI_API, GEMINI_API, CLAUDE_API).
    model: str
        Model name to be used by the provider.
    prompt: str
        Text prompt for generation.
    temperature: Optional[float]
        Sampling temperature (optional).
    top_p: Optional[float]
        Nucleus sampling value (optional).
    top_k: Optional[int]
        Top-K sampling parameter (optional).
    max_tokens: Optional[int]
        Maximum number of tokens to generate (optional).

    RETURN
    AIRequest
        Returns an instance of `AIRequest` after validation by pydantic.

    EXAMPLES
    >>> AIRequest(provider='OPENAI_API', model='gpt-4', prompt='Hello')
    """

    provider: str = Field(
        ..., description="AI provider (OPENAI_API, GEMINI_API, CLAUDE_API)"
    )
    model: str = Field(..., description="Model name")
    prompt: str = Field(..., description="Prompt text")
    temperature: float | None = Field(default=None, description="Temperature")
    top_p: float | None = Field(default=None, description="Top P")
    top_k: int | None = Field(default=None, description="Top K")
    max_tokens: int | None = Field(default=None, description="Max tokens")
