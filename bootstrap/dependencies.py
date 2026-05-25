from application.ports.ai_provider_port import AIProviderPort
from application.services.ai_service import AIService
from infrastructure.adapters.claude_adapter import ClaudeAdapter
from infrastructure.adapters.gemini_adapter import GeminiAdapter
from infrastructure.adapters.openai_adapter import OpenAIAdapter


def create_ai_provider(ai_provider_name: str) -> AIService:

    ai_provider: AIProviderPort | None = None
    match ai_provider_name:
        case "OPENAI_API":
            ai_provider = OpenAIAdapter()
        case "GEMINI_API":
            ai_provider = GeminiAdapter()
        case "CLAUDE_API":
            ai_provider = ClaudeAdapter()
        case _:
            raise ValueError(f"Unsupported LLM: {ai_provider}")

    return AIService(ai_provider)
