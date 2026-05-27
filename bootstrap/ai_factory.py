"""Factory for creating AI provider adapter instances.

DESCRIPTION
Provides a simple factory to instantiate the concrete adapter implementation
for a given provider identifier.

EXAMPLES
>>> AIProviderFactory.create(AIProviderFactory.OPENAI_API)
"""

from application.ports.ai_provider_port import AIProviderPort
from infrastructure.adapters.claude_adapter import ClaudeAdapter
from infrastructure.adapters.gemini_adapter import GeminiAdapter
from infrastructure.adapters.openai_adapter import OpenAIAdapter


class AIProviderFactory:
    """Factory that maps provider identifiers to concrete adapters.

    ATTRIBUTES
    CLAUDE_API, GEMINI_API, OPENAI_API: str
        String constants used to select the provider implementation.
    """

    CLAUDE_API = "CLAUDE_API"

    GEMINI_API = "GEMINI_API"

    OPENAI_API = "OPENAI_API"

    @staticmethod
    def create(provider: str) -> AIProviderPort:
        """Create and return an AI provider adapter for `provider`.

        ARGS
        provider: str
            Identifier matching one of the class constants.

        RETURN
        AIProviderPort
            An instantiated adapter implementing the port.

        EXCEPTIONS
        ValueError
            Raised when the `provider` value is not recognized.

        EXAMPLES
        >>> AIProviderFactory.create(AIProviderFactory.OPENAI_API)
        """

        ai_provider: AIProviderPort | None = None
        match provider:
            case AIProviderFactory.CLAUDE_API:
                ai_provider = ClaudeAdapter()
            case AIProviderFactory.GEMINI_API:
                ai_provider = GeminiAdapter()
            case AIProviderFactory.OPENAI_API:
                ai_provider = OpenAIAdapter()
            case _:
                raise ValueError(f"Provider {provider} is not support.")

        return ai_provider
