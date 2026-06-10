import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.infrastructure.adapters.openai_adapter import OpenAIAdapter


class OpenAIAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.params: dict = {
            "model": "gpt-4o-mini",
            "prompt": "Write a summary about Python.",
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 20,
            "max_tokens": 256,
        }
        self.adapter = OpenAIAdapter()

    def test_generate_content_return_expected_data(self) -> None:
        expected: str = "Python is programming language."
        self.adapter.client = Mock()
        self.adapter.client.chat.completions.create.return_value.choices = [
            SimpleNamespace(message=SimpleNamespace(content=expected))
        ]
        content = self.adapter.generate_content(self.params)
        self.assertEqual(content, expected)
        self.adapter.client.chat.completions.create.assert_called_once_with(
            model=self.params.get("model"),
            messages=[{"role": "user", "content": self.params.get("prompt")}],
            temperature=self.params.get("temperature"),
            top_p=self.params.get("top_p"),
        )

    def test_generate_content_internal_server_error(self):
        self.adapter.client = Mock()
        exception = Exception(
            "503 UNAVAILABLE. {'error': {'code': 503, 'status': 'UNAVAILABLE'}}"
        )
        exception.status_code = 503

        self.adapter.client.chat.completions.create.side_effect = [exception]

        with self.assertRaises(Exception) as context:
            self.adapter.generate_content(self.params)

        self.assertEqual(context.exception.status_code, 503)
