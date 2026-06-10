"""Application service layer for AI operations.

DESCRIPTION
The service adapts an `AIProviderPort` implementation to the application's
needs, orchestrating calls and lifecycle of the provider client.

EXAMPLES
>>> service = AIService(adapter)
>>> service.generate_content({'model':'m','prompt':'hi'})
"""

from src.application.ports.ai_provider_port import AIProviderPort


class AIService:
    """Service that delegates content generation to an AI provider.

    ARGS
    ai_provider: AIProviderPort
        Concrete implementation of the provider port used to generate text.

    METHODS
    generate_content(params: dict) -> str
        Call the provider to generate text and ensure the client is closed.

    EXAMPLES
    >>> AIService(adapter).generate_content({'prompt':'Hello'})
    """

    def __init__(self, ai_provider: AIProviderPort):
        self.ai_provider = ai_provider

    def generate_content(self, params: dict) -> str:
        """Generate content using the configured AI provider.

        ARGS
        params: dict
            Parameters forwarded to the provider (model, prompt, temperature...).

        RETURN
        str
            The generated text returned by the provider.

        EXCEPTIONS
        Exceptions raised by the provider are propagated to the caller.

        EXAMPLES
        >>> service.generate_content({'model':'m','prompt':'Hi'})
        """
        response = self.ai_provider.generate_content(params)
        self.ai_provider.close_client()
        return response
