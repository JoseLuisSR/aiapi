from abc import ABC, abstractmethod

from google import genai
from google.genai import types
from openai import OpenAI

from config import Config


class AIAPIBase(ABC):
    @abstractmethod
    def generate_content(self, params: dict) -> str:
        pass

    @abstractmethod
    def close_client(self):
        pass


class AIAPI(AIAPIBase):
    pass


class AIAPIOpenAI(AIAPI):
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.load_api_key().get(Config.OPENAI_API_KEY),
        )

    def generate_content(self, params: dict) -> str:
        self.response = self.client.responses.create(
            model=params.get("model"),
            input=params.get("prompt"),
            temperature=params.get("temperature"),
            top_p=params.get("top_p"),
        )
        return self.response.output_text

    def close_client(self):
        self.client.close


class AIAPIGemini(AIAPI):
    def __init__(self):
        self.client = genai.Client(
            api_key=Config.load_api_key().get(Config.GEMINI_API_KEY)
        )

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
        self.client.close
