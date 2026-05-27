"""Abstract port defining the AI provider interface.

DESCRIPTION
This module declares the `AIProviderPort` abstract base class which
standardizes the methods expected from concrete AI provider adapters.

EXAMPLES
Adapters should subclass `AIProviderPort` and implement the required
methods.
"""

from abc import ABC, abstractmethod

from dotenv import load_dotenv

load_dotenv()


class AIProviderPort(ABC):
    """Abstract interface for AI provider adapters.

    DESCRIPTION
    Concrete adapters (OpenAI, Gemini, Claude) implement this interface to
    provide a uniform API to the application layer.

    METHODS
    generate_content(params: dict) -> str
        Generate text according to the provided parameters.
    close_client()
        Release or close any underlying client resources.

    EXAMPLES
    >>> class MyAdapter(AIProviderPort):
    ...     def generate_content(self, params: dict) -> str:
    ...         return 'ok'
    ...     def close_client(self):
    ...         pass
    """

    @abstractmethod
    def generate_content(self, params: dict) -> str:
        """Generate text from the provider.

        ARGS
        params: dict
            Parameters such as `model`, `prompt`, `temperature`, etc.

        RETURN
        str
            Generated text from the provider.

        EXCEPTIONS
        Providers may raise provider-specific exceptions on error.

        EXAMPLES
        >>> adapter.generate_content({'model': 'm', 'prompt': 'hi'})
        """
        pass

    @abstractmethod
    def close_client(self):
        """Close or cleanup the underlying provider client.

        RETURN
        None

        EXAMPLES
        >>> adapter.close_client()
        """
        pass
