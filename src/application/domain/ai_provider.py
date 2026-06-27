"""Enum of supported AI provider identifiers.

DESCRIPTION
Declares `AIProvider`, a `StrEnum` whose members map directly to the
lowercase provider identifier strings used in the REST API contract.
Consuming code (DTOs, factory) imports this enum so that the canonical
set of provider identifiers lives in a single place.

EXAMPLES
>>> AIProvider.OPENAI_API
<AIProvider.OPENAI_API: 'openai_api'>
>>> AIProvider.from_value('copilot_api')
<AIProvider.COPILOT_API: 'copilot_api'>
"""

from enum import StrEnum


class AIProvider(StrEnum):
    """Enumeration of AI provider identifiers accepted by the gateway.

    DESCRIPTION
    Each member's value is the lowercase string expected in the
    `provider` field of an `AIRequest` JSON payload. Inheriting from
    `StrEnum` ensures that Pydantic v2 serializes each member as a plain
    string and that direct string comparisons work without calling `.value`.

    ATTRIBUTES
    OPENAI_API: str
        Identifier for the OpenAI provider ("openai_api").
    CLAUDE_API: str
        Identifier for the Anthropic Claude provider ("claude_api").
    GEMINI_API: str
        Identifier for the Google Gemini provider ("gemini_api").
    COPILOT_API: str
        Identifier for the Microsoft Copilot / Azure OpenAI provider
        ("copilot_api").

    METHODS
    from_value(value: str) -> AIProvider
        Look up a member by its string value, raising a descriptive
        `ValueError` when the value is not recognized.

    EXAMPLES
    >>> AIProvider("openai_api")
    <AIProvider.OPENAI_API: 'openai_api'>
    >>> AIProvider.from_value("gemini_api")
    <AIProvider.GEMINI_API: 'gemini_api'>
    """

    OPENAI_API = "openai_api"
    CLAUDE_API = "claude_api"
    GEMINI_API = "gemini_api"
    COPILOT_API = "copilot_api"

    @classmethod
    def from_value(cls, value: str) -> "AIProvider":
        """Return the `AIProvider` member whose value matches `value`.

        ARGS
        value: str
            The provider identifier string to look up (e.g. "openai_api").

        RETURN
        AIProvider
            The matching enum member.

        EXCEPTIONS
        ValueError
            Raised when `value` does not match any known provider,
            with a message that lists all valid values.

        EXAMPLES
        >>> AIProvider.from_value("claude_api")
        <AIProvider.CLAUDE_API: 'claude_api'>
        """
        try:
            return cls(value)
        except ValueError as e:
            valid = ", ".join(f"'{m.value}'" for m in cls)
            raise ValueError(
                f"'{value}' is not a valid provider. Valid values are: {valid}."
            ) from e
