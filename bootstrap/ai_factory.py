from application.ports.ai_provider_port import AIProviderPort
from infrastructure.adapters.claude_adapter import ClaudeAdapter
from infrastructure.adapters.gemini_adapter import GeminiAdapter
from infrastructure.adapters.openai_adapter import OpenAIAdapter


class AIProviderFactory:
    CLAUDE_API = "CLAUDE_API"

    GEMINI_API = "GEMINI_API"

    OPENAI_API = "OPENAI_API"

    @staticmethod
    def create(provider: str) -> AIProviderPort:

        ai_provider: AIProviderPort | None = None
        match provider:
            case AIProviderFactory.CLAUDE_API:
                ai_provider = ClaudeAdapter()
            case AIProviderFactory.GEMINI_API:
                ai_provider = GeminiAdapter()
            case AIProviderFactory.OPENAI_API:
                ai_provider = OpenAIAdapter()
            case _:
                raise ValueError(f"Provider {provider} is not support.")

        return ai_provider
