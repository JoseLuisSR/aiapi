"""OpenAI provider adapter.

DESCRIPTION
Implements `AIProviderPort` for the OpenAI Python client. The adapter
creates a client from the `OPENAI_API_KEY` environment variable and
provides `generate_content` and `close_client` methods.

EXAMPLES
>>> adapter = OpenAIAdapter()
>>> adapter.generate_content({'model':'gpt-4','prompt':'Hi'})
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

from config import Config
from src.application.ports.ai_provider_port import AIProviderPort

load_dotenv()


class OpenAIAdapter(AIProviderPort):
    """Adapter for OpenAI's client library.

    ARGS
    None (reads `OPENAI_API_KEY` from environment via `Config`).

    METHODS
    generate_content(params: dict) -> str
        Create a chat completion using the configured OpenAI client and
        return the generated text.
    close_client()
        Close the underlying client connection when present.

    EXAMPLES
    >>> OpenAIAdapter().generate_content({'model':'gpt-4','prompt':'Hello'})
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get(Config.OPENAI_API_KEY),
        )

    def generate_content(self, params: dict) -> str:
        """Generate text using OpenAI chat completions.

        ARGS
        params: dict
            Parameters forwarded to OpenAI client (`model`, `prompt`, `temperature`,
            `top_p`).

        RETURN
        str
            The generated text from the response.

        EXCEPTIONS
        Exceptions from the OpenAI client are propagated.

        EXAMPLES
        >>> adapter.generate_content({'model':'gpt-4','prompt':'Hi'})
        """
        self.response = self.client.chat.completions.create(
            model=params.get("model"),
            messages=[{"role": "user", "content": params.get("prompt")}],
            temperature=params.get("temperature"),
            top_p=params.get("top_p"),
        )
        return self.response.choices[0].message.content

    def close_client(self):
        """Close the OpenAI client if applicable.

        RETURN
        None
        """
        self.client.close()
