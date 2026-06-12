import unittest
from unittest.mock import Mock

from src.application.services.ai_service import AIService


class AIServiceTest(unittest.TestCase):
    PARAMS: dict = {
        "model": "gemini-2.5-flash",
        "prompt": "Write a summary about Python.",
        "temperature": 0.2,
        "top_p": 0.9,
        "top_k": 20,
        "max_tokens": 256,
    }

    def _build_service(self) -> tuple[AIService, Mock]:
        provider = Mock()
        return AIService(provider), provider

    def test_generate_content_returns_provider_result(self) -> None:
        self.service, provider = self._build_service()
        expected: str = "Python is programming language."
        provider.generate_content.return_value = expected
        content: str = self.service.generate_content(self.PARAMS)
        self.assertEqual(expected, content)
        provider.close_client.assert_called_once()

    def test_constructor_rejects_none_provider(self) -> None:
        with self.assertRaises(ValueError):
            AIService(None)

    def test_generate_content_closes_client_on_exception(self) -> None:
        self.service, provider = self._build_service()
        provider.generate_content.side_effect = ValueError("boom")

        with self.assertRaises(ValueError):
            self.service.generate_content(self.PARAMS)

        provider.close_client.assert_called_once()
