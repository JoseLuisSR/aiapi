"""Claude provider adapter.

DESCRIPTION
Implements the `AIProviderPort` interface for Anthropic's Claude client.
The adapter reads `CLAUDE_API_KEY` from the environment and exposes
methods to generate content and close the client.

EXAMPLES
>>> ClaudeAdapter().generate_content({'model':'claude-2','prompt':'Hi'})
"""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

from application.ports.ai_provider_port import AIProviderPort
from config import Config

load_dotenv()


class ClaudeAdapter(AIProviderPort):
    """Adapter for Anthropic's Claude client.

    METHODS
    generate_content(params: dict) -> str
        Create messages on the Anthropic client and return the text.
    close_client()
        Close the Anthropic client and free resources.

    EXAMPLES
    >>> ClaudeAdapter().generate_content({'model':'claude-2','prompt':'Hello'})
    """

    def __init__(self):
        self.client = Anthropic(
            api_key=os.environ.get(Config.CLAUDE_API_KEY),
        )

    def generate_content(self, params: dict) -> str:
        """Generate content using Claude's messaging API.

        ARGS
        params: dict
            Parameters forwarded to the Anthropic client such as `model`,
            `prompt`, `temperature`, and `max_tokens`.

        RETURN
        str
            The generated text from the response.

        EXCEPTIONS
        Exceptions raised by the Anthropic client are propagated.

        EXAMPLES
        >>> adapter.generate_content({'model':'c','prompt':'Hi'})
        """
        sampling_param = {}

        if params.get("temperature") is not None:
            sampling_param["temperature"] = params.get("temperature")
        elif params.get("top_p") is not None:
            sampling_param["top_p"] = params.get("top_p")

        self.response = self.client.messages.create(
            max_tokens=params.get("max_tokens"),
            messages=[{"role": "user", "content": params.get("prompt")}],
            model=params.get("model"),
            top_k=params.get("top_k"),
            **sampling_param,
        )
        return self.response.content[0].text

    def close_client(self):
        """Close the Anthropic client.

        RETURN
        None
        """
        self.client.close()
