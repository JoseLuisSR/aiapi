from application.ports.ai_provider_factory_port import AIProviderFactoryPort
from application.ports.ai_provider_port import AIProviderPort

from .claude_adapter import ClaudeAdapter
from .gemini_adapter import GeminiAdapter
from .openai_adapter import OpenAIAdapter


class AIProviderFactoryAdapter(AIProviderFactoryPort):
    OPENAI_API = "OPENAI_API"

    GEMINI_API = "GEMINI_API"

    CLAUDE_API = "CLAUDE_API"

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_llm(self, llm: str) -> AIProviderPort:
        match llm:
            case AIProviderFactoryAdapter.OPENAI_API:
                return OpenAIAdapter()
            case AIProviderFactoryAdapter.GEMINI_API:
                return GeminiAdapter()
            case AIProviderFactoryAdapter.CLAUDE_API:
                return ClaudeAdapter()
            case _:
                raise ValueError(f"Unsupported LLM: {llm}")
