from abc import ABC, abstractmethod

from dotenv import load_dotenv

load_dotenv()


class AIAPI(ABC):
    @abstractmethod
    def generate_content(self, params: dict) -> str:
        pass

    @abstractmethod
    def close_client(self):
        pass
