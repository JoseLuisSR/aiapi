import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import Config

from .aiapi import AIAPI

load_dotenv()


class GeminiAdapter(AIAPI):
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
