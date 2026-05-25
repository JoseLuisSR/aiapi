from fastapi import FastAPI, HTTPException

from application.dto.ai_request import AIRequest
from application.dto.ai_response import AIResponse
from infrastructure.adapters.factory_adapter import AIProviderFactoryAdapter

app = FastAPI(
    title="AIAPI",
    description="AI API Gateway for OpenAI, Gemini, and Claude",
    version="0.1.0",
)

VALID_PROVIDERS = {
    AIProviderFactoryAdapter.OPENAI_API,
    AIProviderFactoryAdapter.GEMINI_API,
    AIProviderFactoryAdapter.CLAUDE_API,
}


@app.post("/api/v1/generate", response_model=AIResponse)
async def generate(request: AIRequest):
    if request.provider not in VALID_PROVIDERS:
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

    factory = AIProviderFactoryAdapter()
    client = None
    try:
        client = factory.create_llm(request.provider)
        result = client.generate_content(params)
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
    finally:
        if client:
            try:
                client.close_client()
            except Exception:
                pass


@app.get("/health")
async def health_check():
    return {"status": "ok"}
