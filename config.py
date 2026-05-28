"""Configuration constants used to read environment variables.

DESCRIPTION
Holds string keys used to fetch API keys from the environment. This keeps
literal names centralized and simpler to mock or replace in tests.

EXAMPLES
>>> os.environ.get(Config.OPENAI_API_KEY)
"""


class Config:
    """Container for environment variable names.

    ARGS
    None

    ATTRIBUTES
    OPENAI_API_KEY, GEMINI_API_KEY, CLAUDE_API_KEY: str
        Environment variable names expected to store provider API keys.

    EXAMPLES
    >>> Config.OPENAI_API_KEY
    """

    OPENAI_API_KEY = "OPENAI_API_KEY"

    GEMINI_API_KEY = "GEMINI_API_KEY"

    CLAUDE_API_KEY = "CLAUDE_API_KEY"
