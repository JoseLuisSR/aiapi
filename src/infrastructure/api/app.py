"""FastAPI application exposing AI generation endpoints.

DESCRIPTION
This module declares the FastAPI `app` and provides two endpoints:
`/api/v1/generate` for generation requests and `/health` for a simple
health check.

EXAMPLES
Run with `uvicorn infrastructure.api.app:app` and POST to `/api/v1/generate`.
"""

from fastapi import FastAPI, HTTPException

from src.application.domain.ai_provider import AIProvider
from src.application.dto.ai_request import AIRequest
from src.application.dto.ai_response import AIResponse
from src.application.services.ai_service import AIService
from src.bootstrap.dependencies import create_ai_provider

app = FastAPI(
    title="AIAPI",
    description=(
        "AI API Gateway for OpenAI, Gemini, Claude, "
        "and Microsoft Copilot (Azure OpenAI)"
    ),
    version="0.2.0",
)


@app.post("/api/v1/generate", response_model=AIResponse)
async def generate(request: AIRequest):
    """Handle AI generation requests and return a standardized response.

    DESCRIPTION
    Accepts an `AIRequest` payload, creates an `AIService` bound to the
    requested provider, forwards generation parameters and returns an
    `AIResponse`.

    ARGS
    request: AIRequest
        Validated request body containing provider, model and prompt.

    RETURN
    AIResponse
        Standardized response model containing result or error details.

    EXCEPTIONS
    HTTPException
        Raises 400 for unsupported providers or provider-specific value
        errors, and 500 for unexpected internal errors.

    EXAMPLES
    >>> client.post('/api/v1/generate', json={...})
    """

    ai_service: AIService | None = None
    try:
        ai_service = create_ai_provider(request.provider)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "UNSUPPORTED_PROVIDER",
                "message": f"Provider '{request.provider}' is not supported.",
                "supported": [p.value for p in AIProvider],
            },
        ) from e

    params = {
        "model": request.model,
        "prompt": request.prompt,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
        "max_tokens": request.max_tokens,
        "deployment": request.deployment,
        "api_version": request.api_version,
    }

    try:
        result = ai_service.generate_content(params)
        return AIResponse(
            success=True,
            provider=request.provider,
            model=request.model,
            result=result,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "PROVIDER_MISCONFIGURED",
                "message": str(e),
            },
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": str(e),
            },
        ) from e


@app.get("/health")
async def health_check():
    """Simple health check endpoint.

    RETURN
    dict
        A JSON-friendly dictionary with `status: ok` when the app is healthy.

    EXAMPLES
    >>> client.get('/health')
    {"status": "ok"}
    """
    return {"status": "ok"}
