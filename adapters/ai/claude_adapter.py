import os

from anthropic import Anthropic
from dotenv import load_dotenv

from config import Config

from .aiapi import AIAPI

load_dotenv()


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
