from application.services.ai_service import AIService
from bootstrap.ai_factory import AIProviderFactory


def create_ai_provider(provider: str) -> AIService:

    ai_provider = AIProviderFactory.create(provider)
    return AIService(ai_provider)
