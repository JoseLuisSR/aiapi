"""Dependency helpers for wiring application services.

DESCRIPTION
Small helpers used by the API layer to create service instances with the
correct provider adapter.

EXAMPLES
>>> create_ai_provider('OPENAI_API')
"""

from src.application.services.ai_service import AIService
from src.bootstrap.ai_factory import AIProviderFactory


def create_ai_provider(provider: str) -> AIService:
    """Create an `AIService` configured with a provider adapter.

    ARGS
    provider: str
        Provider identifier passed to the factory.

    RETURN
    AIService
        Service instance wired with the chosen provider adapter.

    EXCEPTIONS
    ValueError
        Propagates factory errors if the provider is unsupported.

    EXAMPLES
    >>> create_ai_provider('OPENAI_API')
    """

    ai_provider = AIProviderFactory.create(provider)
    return AIService(ai_provider)
