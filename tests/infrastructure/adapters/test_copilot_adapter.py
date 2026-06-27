import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.infrastructure.adapters.copilot_adapter import CopilotAdapter

VALID_ENV = {
    "COPILOT_API_KEY": "test-key",
    "COPILOT_API_ENDPOINT": "https://example.openai.azure.com",
    "COPILOT_API_VERSION": "2024-10-21",
    "COPILOT_DEPLOYMENT": "gpt-4o-prod",
}


class CopilotAdapterTest(unittest.TestCase):
    @patch("src.infrastructure.adapters.copilot_adapter.AzureOpenAI")
    def setUp(self, mock_azure_openai: Mock) -> None:  # noqa: PT012
        self.params: dict = {
            "model": "gpt-4o",
            "prompt": "Write a summary about Python.",
            "temperature": 0.2,
            "top_p": 0.9,
            "top_k": 20,
            "max_tokens": 256,
            "deployment": "gpt-4o-prod",
            "api_version": "2024-10-21",
        }
        with patch.dict(os.environ, VALID_ENV):
            self.adapter = CopilotAdapter()

    def tearDown(self) -> None:
        self.adapter.close_client()

    def test_generate_content_returns_expected_value(self) -> None:
        expected: str = "Python is a programming language."
        self.mock_client: Mock = Mock()
        self.adapter.client = self.mock_client  # type: ignore[assignment]
        self.mock_client.chat.completions.create.return_value.choices = [
            SimpleNamespace(message=SimpleNamespace(content=expected))
        ]

        content = self.adapter.generate_content(self.params)

        self.assertEqual(content, expected)
        call_kwargs = self.mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "gpt-4o-prod")
        self.assertEqual(
            call_kwargs["messages"],
            [{"role": "user", "content": self.params["prompt"]}],
        )
        self.assertEqual(call_kwargs["temperature"], self.params["temperature"])
        self.assertEqual(call_kwargs["top_p"], self.params["top_p"])
        self.assertEqual(call_kwargs["max_tokens"], self.params["max_tokens"])
        self.assertNotIn("top_k", call_kwargs)

    def test_generate_content_uses_model_as_deployment_fallback(self) -> None:
        self.mock_client = Mock()
        self.adapter.client = self.mock_client  # type: ignore[assignment]
        expected: str = "Fallback via model."
        self.mock_client.chat.completions.create.return_value.choices = [
            SimpleNamespace(message=SimpleNamespace(content=expected))
        ]

        params_no_deployment = dict(self.params)
        params_no_deployment["deployment"] = None

        content = self.adapter.generate_content(params_no_deployment)

        self.assertEqual(content, expected)
        call_kwargs = self.mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs["model"], self.params["model"])

    def test_generate_content_uses_env_deployment_as_last_resort(self) -> None:
        self.mock_client = Mock()
        self.adapter.client = self.mock_client  # type: ignore[assignment]
        self.adapter._default_deployment = "env-deploy"
        expected: str = "Fallback via env."
        self.mock_client.chat.completions.create.return_value.choices = [
            SimpleNamespace(message=SimpleNamespace(content=expected))
        ]

        params_no_deploy_no_model = dict(self.params)
        params_no_deploy_no_model["deployment"] = None
        params_no_deploy_no_model["model"] = None

        content = self.adapter.generate_content(params_no_deploy_no_model)

        self.assertEqual(content, expected)
        call_kwargs = self.mock_client.chat.completions.create.call_args.kwargs
        self.assertEqual(call_kwargs["model"], "env-deploy")

    def test_generate_content_raises_when_no_deployment_resolved(self) -> None:
        self.adapter._default_deployment = None
        params = dict(self.params)
        params["deployment"] = None
        params["model"] = None

        with self.assertRaises(ValueError):
            self.adapter.generate_content(params)

    def test_generate_content_skips_none_sampling_params(self) -> None:
        self.mock_client = Mock()
        self.adapter.client = self.mock_client  # type: ignore[assignment]
        self.mock_client.chat.completions.create.return_value.choices = [
            SimpleNamespace(message=SimpleNamespace(content="ok"))
        ]

        params_no_sampling = dict(self.params)
        params_no_sampling["temperature"] = None
        params_no_sampling["top_p"] = None
        params_no_sampling["max_tokens"] = None

        self.adapter.generate_content(params_no_sampling)

        call_kwargs = self.mock_client.chat.completions.create.call_args.kwargs
        self.assertIsNone(call_kwargs.get("temperature"))
        self.assertIsNone(call_kwargs.get("top_p"))
        self.assertIsNone(call_kwargs.get("max_tokens"))

    def test_generate_content_internal_server_error(self) -> None:
        self.mock_client = Mock()
        self.adapter.client = self.mock_client  # type: ignore[assignment]
        exception = Exception(
            "503 UNAVAILABLE. {'error': {'code': 503, 'status': 'UNAVAILABLE'}}"
        )
        exception.status_code = 503  # type: ignore[attr-defined]
        self.mock_client.chat.completions.create.side_effect = [exception]

        with self.assertRaises(Exception) as context:
            self.adapter.generate_content(self.params)

        self.assertEqual(context.exception.status_code, 503)  # type: ignore[attr-defined]

    def test_close_client(self) -> None:
        self.mock_client = Mock()
        self.adapter.client = self.mock_client  # type: ignore[assignment]
        self.adapter.close_client()
        self.mock_client.close.assert_called_once()

    @patch("src.infrastructure.adapters.copilot_adapter.AzureOpenAI")
    def test_init_raises_when_api_key_missing(self, _: Mock) -> None:
        env_without_key = {k: v for k, v in VALID_ENV.items() if k != "COPILOT_API_KEY"}
        with (
            patch.dict(os.environ, env_without_key, clear=True),
            self.assertRaises(ValueError),
        ):
            CopilotAdapter()

    @patch("src.infrastructure.adapters.copilot_adapter.AzureOpenAI")
    def test_init_raises_when_endpoint_missing(self, _: Mock) -> None:
        env_without_endpoint = {
            k: v for k, v in VALID_ENV.items() if k != "COPILOT_API_ENDPOINT"
        }
        with (
            patch.dict(os.environ, env_without_endpoint, clear=True),
            self.assertRaises(ValueError),
        ):
            CopilotAdapter()

    @patch("src.infrastructure.adapters.copilot_adapter.AzureOpenAI")
    def test_init_raises_when_api_version_missing(self, _: Mock) -> None:
        env_without_version = {
            k: v for k, v in VALID_ENV.items() if k != "COPILOT_API_VERSION"
        }
        with (
            patch.dict(os.environ, env_without_version, clear=True),
            self.assertRaises(ValueError),
        ):
            CopilotAdapter()

    @patch("src.infrastructure.adapters.copilot_adapter.AzureOpenAI")
    def test_error_message_contains_no_secret_values(self, _: Mock) -> None:
        credential_value = "super-credential-xyz"
        endpoint_value = "https://my-private.openai.azure.com"
        env_missing_version = {
            "COPILOT_API_KEY": credential_value,
            "COPILOT_API_ENDPOINT": endpoint_value,
        }
        with (
            patch.dict(os.environ, env_missing_version, clear=True),
            self.assertRaises(ValueError) as context,
        ):
            CopilotAdapter()

        error_message = str(context.exception)
        self.assertNotIn(credential_value, error_message)
        self.assertNotIn(endpoint_value, error_message)
