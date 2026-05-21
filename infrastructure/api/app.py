from fastapi import FastAPI, HTTPException

from application.dto.llm_request import LLMRequest
from application.dto.llm_response import LLMResponse
from infrastructure.llm.factory_adapter import LLMFactoryAdapter

app = FastAPI(
    title="AIAPI",
    description="AI API Gateway for OpenAI, Gemini, and Claude",
    version="0.1.0",
)

VALID_PROVIDERS = {
    LLMFactoryAdapter.OPENAI_API,
    LLMFactoryAdapter.GEMINI_API,
    LLMFactoryAdapter.CLAUDE_API,
}


@app.post("/api/v1/generate", response_model=LLMResponse)
async def generate(request: LLMRequest):
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

    factory = LLMFactoryAdapter()
    client = None
    try:
        client = factory.create_llm(request.provider)
        result = client.generate_content(params)
        return LLMResponse(
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
