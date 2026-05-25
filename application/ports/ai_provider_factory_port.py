from abc import ABC, abstractmethod

from application.ports.ai_provider_port import AIProviderPort


class AIProviderFactoryPort(ABC):
    @abstractmethod
    def create_llm(self, llm: str) -> AIProviderPort:
        pass
