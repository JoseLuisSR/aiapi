import unittest
from unittest.mock import Mock

from google.genai import types

from src.infrastructure.adapters.gemini_adapter import GeminiAdapter


class GeminiAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.params: dict = {
            "model": "gemini-2.5-flash",
            "prompt": "Write a summary about Python.",
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 20,
            "max_tokens": 256,
        }
        self.adapter = GeminiAdapter()

    def test_generate_content_return_expected_data(self) -> None:
        expected: str = "Python is programming language."
        self.adapter.client = Mock()
        self.adapter.client.models.generate_content.return_value.text = expected
        content: str = self.adapter.generate_content(self.params)
        self.assertEqual(content, "Python is programming language.")
        self.adapter.client.models.generate_content.assert_called_once_with(
            model=self.params.get("model"),
            contents={"text": self.params.get("prompt")},
            config=types.GenerateContentConfig(
                temperature=self.params.get("temperature"),
                top_p=self.params.get("top_p"),
                top_k=self.params.get("top_k"),
            ),
        )

    def test_generate_content_internal_server_error(self):
        self.adapter.client = Mock()
        exception = Exception(
            "503 UNAVAILABLE. {'error': {'code': 503, 'status': 'UNAVAILABLE'}}"
        )
        exception.status_code = 503
        self.adapter.client.models.generate_content.side_effect = [exception]

        with self.assertRaises(Exception) as context:
            self.adapter.generate_content(self.params)

        self.assertEqual(context.exception.status_code, 503)
