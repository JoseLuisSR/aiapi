from .aiapi import AIAPI
from .claude_adapter import AIAPIClaude
from .gemini_adapter import AIAPIGemini
from .openai_adapter import AIAPIOpenAI


class AIAPIFactory:
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
            case AIAPIFactory.OPENAI_API:
                return AIAPIOpenAI()
            case AIAPIFactory.GEMINI_API:
                return AIAPIGemini()
            case AIAPIFactory.CLAUDE_API:
                return AIAPIClaude()
            case _:
                raise ValueError(f"Unsupported AI API: {aiapi}")
