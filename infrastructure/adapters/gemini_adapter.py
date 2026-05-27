"""Gemini provider adapter.

DESCRIPTION
Implements `AIProviderPort` for Google's Gemini (genai) client. The adapter
initializes the client from `GEMINI_API_KEY` and maps application params to
the genai API.

EXAMPLES
>>> GeminiAdapter().generate_content({'model':'gemini-pro','prompt':'Hi'})
"""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from application.ports.ai_provider_port import AIProviderPort
from config import Config

load_dotenv()


class GeminiAdapter(AIProviderPort):
    """Adapter for the Google Gemini (`genai`) client.

    METHODS
    generate_content(params: dict) -> str
        Generate content using the Gemini models.
    close_client()
        Close the underlying client resources.

    EXAMPLES
    >>> GeminiAdapter().generate_content({'model':'gemini','prompt':'Hello'})
    """

    def __init__(self):
        self.client = genai.Client(api_key=os.environ.get(Config.GEMINI_API_KEY))

    def generate_content(self, params: dict) -> str:
        """Generate text using Gemini's `generate_content`.

        ARGS
        params: dict
            Mapping that must include `model` and `prompt`. Optional generation
            parameters such as `temperature`, `top_p`, and `top_k` are forwarded.

        RETURN
        str
            The generated text returned by the Gemini client.

        EXCEPTIONS
        Any exceptions from the genai client are propagated.

        EXAMPLES
        >>> adapter.generate_content({'model':'g','prompt':'Hi'})
        """
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
        """Close the Gemini client connection.

        RETURN
        None
        """
        self.client.close()
