from fastapi import FastAPI, HTTPException

from application.dto.ai_request import AIRequest
from application.dto.ai_response import AIResponse
from application.services.ai_service import AIService
from bootstrap.dependencies import create_ai_provider

app = FastAPI(
    title="AIAPI",
    description="AI API Gateway for OpenAI, Gemini, and Claude",
    version="0.1.0",
)


@app.post("/api/v1/generate", response_model=AIResponse)
async def generate(request: AIRequest):

    ai_service: AIService | None = None
    try:
        ai_service = create_ai_provider(request.provider)
    except ValueError:
        raise HTTPException(
            status_code=400, detail=f"Unsupported provider: {request.provider}"
        )

    params = {
        "model": request.model,
        "prompt": request.prompt,
        "temperature": request.temperature,
        "top_p": request.top_p,
        "top_k": request.top_k,
        "max_tokens": request.max_tokens,
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
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
