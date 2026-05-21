from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

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


class GenerateRequest(BaseModel):
    provider: str = Field(
        ..., description="AI provider (OPENAI_API, GEMINI_API, CLAUDE_API)"
    )
    model: str = Field(..., description="Model name")
    prompt: str = Field(..., description="Prompt text")
    temperature: Optional[float] = Field(default=None, description="Temperature")
    top_p: Optional[float] = Field(default=None, description="Top P")
    top_k: Optional[int] = Field(default=None, description="Top K")
    max_tokens: Optional[int] = Field(default=None, description="Max tokens")


class GenerateResponse(BaseModel):
    success: bool
    provider: Optional[str] = None
    model: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None


@app.post("/api/v1/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
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
        return GenerateResponse(
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
