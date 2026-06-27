"""Data transfer objects for AI requests.

DESCRIPTION
Defines the `AIRequest` pydantic model used to validate incoming
AI generation requests. The `provider` field is typed as `AIProvider`
so that Pydantic v2 rejects unknown provider strings at parse time
and serializes the value as a lowercase string in responses.

EXAMPLES
>>> AIRequest(provider='openai_api', model='gpt-4', prompt='Hello')
"""

from pydantic import BaseModel, Field

from src.application.domain.ai_provider import AIProvider


class AIRequest(BaseModel):
    """Pydantic model representing an AI generation request.

    DESCRIPTION
    The model contains the provider identifier, model name and the prompt
    together with optional generation parameters. Two additional optional
    fields (`deployment`, `api_version`) support Azure OpenAI deployments
    and are ignored by non-Copilot providers.

    ARGS
    provider: AIProvider
        AI provider identifier (e.g. 'openai_api', 'gemini_api',
        'claude_api', 'copilot_api'). Pydantic coerces the incoming
        string into the corresponding `AIProvider` member.
    model: str
        Model name to be used by the provider. For Copilot, used as the
        deployment name when `deployment` is not provided.
    prompt: str
        Text prompt for generation.
    temperature: Optional[float]
        Sampling temperature (optional).
    top_p: Optional[float]
        Nucleus sampling value (optional).
    top_k: Optional[int]
        Top-K sampling parameter (optional). Not forwarded to Azure OpenAI.
    max_tokens: Optional[int]
        Maximum number of tokens to generate (optional).
    deployment: Optional[str]
        Azure OpenAI deployment name override (copilot_api only, optional).
        Takes precedence over `model` when resolving the deployment.
    api_version: Optional[str]
        Azure OpenAI API version override (copilot_api only, optional).
        Reserved for future per-request client construction; v1 uses the
        environment-level `COPILOT_API_VERSION`.

    RETURN
    AIRequest
        Returns an instance of `AIRequest` after validation by pydantic.

    EXAMPLES
    >>> AIRequest(provider='openai_api', model='gpt-4', prompt='Hello')
    >>> AIRequest(
    ...     provider='copilot_api',
    ...     model='gpt-4o',
    ...     prompt='Hello',
    ...     deployment='gpt-4o-prod',
    ...     api_version='2024-10-21',
    ... )
    """

    provider: AIProvider = Field(..., description="AI provider identifier")
    model: str = Field(..., description="Model name")
    prompt: str = Field(..., description="Prompt text")
    temperature: float | None = Field(default=None, description="Temperature")
    top_p: float | None = Field(default=None, description="Top P")
    top_k: int | None = Field(default=None, description="Top K")
    max_tokens: int | None = Field(default=None, description="Max tokens")
    deployment: str | None = Field(
        default=None,
        description="Azure OpenAI deployment name (copilot_api only)",
    )
    api_version: str | None = Field(
        default=None,
        description="Azure OpenAI API version (copilot_api only)",
    )
