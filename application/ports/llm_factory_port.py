from abc import ABC, abstractmethod

from application.ports.llm_port import LLMPort


class LLMFactoryPort(ABC):
    @abstractmethod
    def create_llm(self, llm: str) -> LLMPort:
        pass
