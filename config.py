"""Configuration constants used to read environment variables.

DESCRIPTION
Holds string keys used to fetch API keys and service endpoints from the
environment. This keeps literal names centralized and simpler to mock or
replace in tests.

EXAMPLES
>>> os.environ.get(Config.OPENAI_API_KEY)
>>> os.environ.get(Config.COPILOT_API_ENDPOINT)
"""


class Config:
    """Container for environment variable names.

    ARGS
    None

    ATTRIBUTES
    OPENAI_API_KEY: str
        Environment variable name for the OpenAI API key.
    GEMINI_API_KEY: str
        Environment variable name for the Google Gemini API key.
    CLAUDE_API_KEY: str
        Environment variable name for the Anthropic Claude API key.
    COPILOT_API_KEY: str
        Environment variable name for the Azure OpenAI (Copilot) API key.
    COPILOT_API_ENDPOINT: str
        Environment variable name for the Azure OpenAI resource endpoint URL.
    COPILOT_API_VERSION: str
        Environment variable name for the Azure OpenAI API version string.
    COPILOT_DEPLOYMENT: str
        Environment variable name for the default Azure OpenAI deployment name.

    EXAMPLES
    >>> Config.OPENAI_API_KEY
    >>> Config.COPILOT_API_ENDPOINT
    """

    OPENAI_API_KEY = "OPENAI_API_KEY"

    GEMINI_API_KEY = "GEMINI_API_KEY"

    CLAUDE_API_KEY = "CLAUDE_API_KEY"

    COPILOT_API_KEY = "COPILOT_API_KEY"

    COPILOT_API_ENDPOINT = "COPILOT_API_ENDPOINT"

    COPILOT_API_VERSION = "COPILOT_API_VERSION"

    COPILOT_DEPLOYMENT = "COPILOT_DEPLOYMENT"
