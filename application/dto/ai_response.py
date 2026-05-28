"""Data transfer objects for AI responses.

DESCRIPTION
Defines the `AIResponse` pydantic model returned by the API.

EXAMPLES
>>> AIResponse(success=True, provider='OPENAI_API', result='Hi')
"""


from pydantic import BaseModel


class AIResponse(BaseModel):
    """Pydantic model representing an AI generation response.

    DESCRIPTION
    The model is used to standardize responses from different AI providers.

    ARGS
    success: bool
        Indicates if the request succeeded.
    provider: Optional[str]
        The provider identifier used to generate the result.
    model: Optional[str]
        The model name used for the generation.
    result: Optional[str]
        The generated text result.
    error: Optional[str]
        Error message when `success` is False.

    RETURN
    AIResponse
        Returns an instance of `AIResponse` ready to be serialized by FastAPI.

    EXAMPLES
    >>> AIResponse(success=True, provider='OPENAI_API', result='Hello')
    """

    success: bool
    provider: str | None = None
    model: str | None = None
    result: str | None = None
    error: str | None = None
