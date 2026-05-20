import os
from abc import ABC, abstractmethod

from anthropic import Anthropic
from dotenv import load_dotenv
from google import genai
from google.genai import types
from openai import OpenAI

from config import Config

load_dotenv()


class AIAPI(ABC):
    @abstractmethod
    def generate_content(self, params: dict) -> str:
        pass

    @abstractmethod
    def close_client(self):
        pass


class AIAPIOpenAI(AIAPI):
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get(Config.OPENAI_API_KEY),
        )

    def generate_content(self, params: dict) -> str:
        self.response = self.client.chat.completions.create(
            model=params.get("model"),
            messages=[{"role": "user", "content": params.get("prompt")}],
            temperature=params.get("temperature"),
            top_p=params.get("top_p"),
        )
        return self.response.choices[0].message.content

    def close_client(self):
        self.client.close()


class AIAPIGemini(AIAPI):
    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get(Config.GEMINI_API_KEY))

    def generate_content(self, params: dict) -> str:
        self.response = self.client.models.generate_content(
            model=params.get("model"),
            contents={"text": params.get("prompt")},
            config=types.GenerateContentConfig(
                temperature=params.get("temperature"),
                top_p=params.get("top_p"),
                top_k=params.get("top_k"),
            ),
        )
        return self.response.text

    def close_client(self):
        self.client.close()


class AIAPIClaude(AIAPI):
    def __init__(self):
        self.client = Anthropic(
            api_key=os.environ.get(Config.CLAUDE_API_KEY),
        )

    def generate_content(self, params: dict) -> str:
        self.response = self.client.messages.create(
            max_tokens=params.get("max_tokens"),
            messages=[{"role": "user", "content": params.get("prompt")}],
            model=params.get("model"),
            temperature=params.get("temperature"),
            # top_p=params.get("top_p"),
            top_k=params.get("top_k"),
        )
        return self.response.content[0].text

    def close_client(self):
        self.client.close()


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
