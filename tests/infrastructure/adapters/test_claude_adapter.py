import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from src.infrastructure.adapters.claude_adapter import ClaudeAdapter


class ClaudeAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.params: dict = {
            "model": "gpt-4o-mini",
            "prompt": "Write a summary about Python.",
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 20,
            "max_tokens": 256,
        }
        self.adapter = ClaudeAdapter()

    def tearDown(self):
        self.adapter.close_client()

    def test_generate_content_with_temperature_return_expected_value(self) -> None:
        expected: str = "Python is programming language."
        self.adapter.client = Mock()
        self.adapter.client.messages.create.return_value.content = [
            SimpleNamespace(text=expected)
        ]
        self.params["top_p"] = None
        print(self.params)
        content = self.adapter.generate_content(self.params)
        self.assertEqual(content, expected)

        self.adapter.client.messages.create.assert_called_once_with(
            max_tokens=self.params.get("max_tokens"),
            messages=[{"role": "user", "content": self.params.get("prompt")}],
            model=self.params.get("model"),
            top_k=self.params.get("top_k"),
            temperature=self.params.get("temperature"),
        )

    def test_generate_content_with_top_p_return_expected_value(self) -> None:
        expected: str = "Python is programming language."
        self.adapter.client = Mock()
        self.adapter.client.messages.create.return_value.content = [
            SimpleNamespace(text=expected)
        ]
        self.params["temperature"] = None
        print(self.params)
        content = self.adapter.generate_content(self.params)
        self.assertEqual(content, expected)

        self.adapter.client.messages.create.assert_called_once_with(
            max_tokens=self.params.get("max_tokens"),
            messages=[{"role": "user", "content": self.params.get("prompt")}],
            model=self.params.get("model"),
            top_k=self.params.get("top_k"),
            top_p=self.params.get("top_p"),
        )

    def test_close_client(self):
        self.adapter.client = Mock()
        self.adapter.close_client()
        self.adapter.client.close.assert_called_once()
