from .aiapi import AIAPI
from .claude_adapter import ClaudeAdapter
from .gemini_adapter import GeminiAdapter
from .openai_adapter import OpenAIAdapter


class FactoryLLMAdapter:
    OPENAI_API = "OPENAI_API"

    GEMINI_API = "GEMINI_API"

    CLAUDE_API = "CLAUDE_API"

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def create_aiapi(self, aiapi: str) -> AIAPI:
        match aiapi:
            case FactoryLLMAdapter.OPENAI_API:
                return OpenAIAdapter()
            case FactoryLLMAdapter.GEMINI_API:
                return GeminiAdapter()
            case FactoryLLMAdapter.CLAUDE_API:
                return ClaudeAdapter()
            case _:
                raise ValueError(f"Unsupported AI API: {aiapi}")
