from application.ports.llm_factory_port import LLMFactoryPort
from application.ports.llm_port import LLMPort

from .claude_adapter import ClaudeAdapter
from .gemini_adapter import GeminiAdapter
from .openai_adapter import OpenAIAdapter


class LLMFactoryAdapter(LLMFactoryPort):
    OPENAI_API = "OPENAI_API"

    GEMINI_API = "GEMINI_API"

    CLAUDE_API = "CLAUDE_API"

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_llm(self, llm: str) -> LLMPort:
        match llm:
            case LLMFactoryAdapter.OPENAI_API:
                return OpenAIAdapter()
            case LLMFactoryAdapter.GEMINI_API:
                return GeminiAdapter()
            case LLMFactoryAdapter.CLAUDE_API:
                return ClaudeAdapter()
            case _:
                raise ValueError(f"Unsupported LLM: {llm}")
