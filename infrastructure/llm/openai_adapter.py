import os

from dotenv import load_dotenv
from openai import OpenAI

from application.ports.llm_port import LLMPort
from config import Config

load_dotenv()


class OpenAIAdapter(LLMPort):
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
