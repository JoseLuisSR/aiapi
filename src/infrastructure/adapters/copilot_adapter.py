"""Microsoft Copilot / Azure OpenAI provider adapter.

DESCRIPTION
Implements `AIProviderPort` for the Azure OpenAI service using the
`AzureOpenAI` client from the `openai` SDK. The adapter reads four
environment variables at construction time: `COPILOT_API_KEY`,
`COPILOT_API_ENDPOINT`, `COPILOT_API_VERSION`, and optionally
`COPILOT_DEPLOYMENT` (used as the default deployment when the request
does not specify one explicitly).

Deployment name resolution follows this precedence order (high to low):
  1. `params["deployment"]` — per-request override.
  2. `params["model"]`      — model field used as deployment name.
  3. env `COPILOT_DEPLOYMENT` — environment-level default.

EXAMPLES
>>> adapter = CopilotAdapter()
>>> adapter.generate_content({'model': 'gpt-4o', 'prompt': 'Hello'})
"""

import os

from dotenv import load_dotenv
from openai import AzureOpenAI

from config import Config
from src.application.ports.ai_provider_port import AIProviderPort

load_dotenv()


class CopilotAdapter(AIProviderPort):
    """Adapter for Microsoft Copilot via Azure OpenAI Service.

    DESCRIPTION
    Wraps the `AzureOpenAI` client and implements `AIProviderPort`.
    The client is constructed once in `__init__` using the environment-level
    `COPILOT_API_VERSION`; per-request `api_version` overrides are accepted
    in the request contract but deferred to v2 (would require per-call client
    re-construction).

    ARGS
    None — all configuration is read from environment variables via `Config`.

    METHODS
    generate_content(params: dict) -> str
        Resolve the deployment, build sampling parameters (excluding
        `top_k`), call Azure OpenAI chat completions, and return the
        generated text.
    close_client()
        Close the underlying `AzureOpenAI` HTTP client.

    EXAMPLES
    >>> adapter = CopilotAdapter()
    >>> adapter.generate_content({
    ...     'model': 'gpt-4o',
    ...     'prompt': 'Summarize Python.',
    ...     'deployment': 'gpt-4o-prod',
    ... })
    """

    def __init__(self) -> None:
        api_key = os.environ.get(Config.COPILOT_API_KEY)
        azure_endpoint = os.environ.get(Config.COPILOT_API_ENDPOINT)
        api_version = os.environ.get(Config.COPILOT_API_VERSION)
        self._default_deployment = os.environ.get(Config.COPILOT_DEPLOYMENT)

        if not api_key or not azure_endpoint or not api_version:
            raise ValueError(
                "Copilot provider is not configured. "
                "Required environment variables are missing: "
                "COPILOT_API_KEY, COPILOT_API_ENDPOINT, COPILOT_API_VERSION."
            )

        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
        )

    def _resolve_deployment(self, params: dict) -> str:
        """Determine the Azure OpenAI deployment name from `params`.

        DESCRIPTION
        Applies the three-level precedence rule: per-request `deployment`
        field beats `model` field, which beats the environment-level
        `COPILOT_DEPLOYMENT` default. Raises `ValueError` when none of
        the three sources yields a non-empty string.

        ARGS
        params: dict
            Generation parameters forwarded from the request. May contain
            `deployment` and/or `model` keys.

        RETURN
        str
            The resolved deployment name to pass to the Azure client.

        EXCEPTIONS
        ValueError
            Raised when no deployment can be resolved from params or
            environment configuration.

        EXAMPLES
        >>> adapter._resolve_deployment({'deployment': 'gpt-4o-prod'})
        'gpt-4o-prod'
        >>> adapter._resolve_deployment({'model': 'gpt-4o'})
        'gpt-4o'
        """
        deployment = (
            params.get("deployment") or params.get("model") or self._default_deployment
        )
        if not deployment:
            raise ValueError(
                "No Azure OpenAI deployment could be resolved. "
                "Provide 'deployment' in the request or set COPILOT_DEPLOYMENT."
            )
        return deployment

    def generate_content(self, params: dict) -> str:
        """Generate text using Azure OpenAI chat completions.

        DESCRIPTION
        Resolves the deployment name, builds a sampling-parameter dict
        (only including non-None values), and calls
        `client.chat.completions.create`. The `top_k` parameter is never
        forwarded because Azure OpenAI does not accept it.

        NOTE: The per-request `api_version` field present in `params` is
        accepted in the API contract but is NOT applied here in v1. The
        `AzureOpenAI` client is constructed once in `__init__` with the
        environment-level API version. Per-request overrides require
        re-constructing the client per call and are deferred to v2.

        ARGS
        params: dict
            Generation parameters. Recognized keys: `model`, `prompt`,
            `deployment`, `temperature`, `top_p`, `max_tokens`.
            `top_k` and `api_version` are silently ignored.

        RETURN
        str
            The generated text from the first response choice.

        EXCEPTIONS
        Any exception raised by the Azure OpenAI client is propagated.

        EXAMPLES
        >>> adapter.generate_content({'model': 'gpt-4o', 'prompt': 'Hi'})
        """
        deployment = self._resolve_deployment(params)

        sampling: dict = {}
        if params.get("temperature") is not None:
            sampling["temperature"] = params["temperature"]
        if params.get("top_p") is not None:
            sampling["top_p"] = params["top_p"]
        if params.get("max_tokens") is not None:
            sampling["max_tokens"] = params["max_tokens"]

        prompt: str = params.get("prompt") or ""

        self.response = self.client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            **sampling,
        )
        return self.response.choices[0].message.content  # type: ignore[return-value]

    def close_client(self) -> None:
        """Close the Azure OpenAI HTTP client.

        RETURN
        None

        EXAMPLES
        >>> adapter.close_client()
        """
        self.client.close()
