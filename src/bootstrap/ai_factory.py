"""Factory for creating AI provider adapter instances.

DESCRIPTION
Provides a simple factory to instantiate the concrete adapter implementation
for a given provider identifier.

EXAMPLES
>>> AIProviderFactory.create(AIProviderFactory.OPENAI_API)
"""

from src.application.domain.ai_provider import AIProvider
from src.application.ports.ai_provider_port import AIProviderPort
from src.infrastructure.adapters.claude_adapter import ClaudeAdapter
from src.infrastructure.adapters.copilot_adapter import CopilotAdapter
from src.infrastructure.adapters.gemini_adapter import GeminiAdapter
from src.infrastructure.adapters.openai_adapter import OpenAIAdapter


class AIProviderFactory:
    """Factory that maps provider identifiers to concrete adapters.

    ATTRIBUTES
    CLAUDE_API, GEMINI_API, OPENAI_API, COPILOT_API: str
        String constants used to select the provider implementation.
        Values match the lowercase `AIProvider` enum values (ADR-003).
    """

    CLAUDE_API = AIProvider.CLAUDE_API.value  # "claude_api"

    GEMINI_API = AIProvider.GEMINI_API.value  # "gemini_api"

    OPENAI_API = AIProvider.OPENAI_API.value  # "openai_api"

    COPILOT_API = AIProvider.COPILOT_API.value  # "copilot_api"

    @staticmethod
    def create(provider: str) -> AIProviderPort:
        """Create and return an AI provider adapter for `provider`.

        ARGS
        provider: str
            Identifier matching one of the class constants (lowercase, e.g.
            "openai_api", "claude_api", "gemini_api", "copilot_api").

        RETURN
        AIProviderPort
            An instantiated adapter implementing the port.

        EXCEPTIONS
        ValueError
            Raised when the `provider` value is not recognized.

        EXAMPLES
        >>> AIProviderFactory.create(AIProviderFactory.OPENAI_API)
        >>> AIProviderFactory.create(AIProviderFactory.COPILOT_API)
        """

        ai_provider: AIProviderPort | None = None
        match provider:
            case AIProviderFactory.CLAUDE_API:
                ai_provider = ClaudeAdapter()
            case AIProviderFactory.GEMINI_API:
                ai_provider = GeminiAdapter()
            case AIProviderFactory.OPENAI_API:
                ai_provider = OpenAIAdapter()
            case AIProviderFactory.COPILOT_API:
                ai_provider = CopilotAdapter()
            case _:
                raise ValueError(f"Provider {provider} is not supported.")

        return ai_provider
