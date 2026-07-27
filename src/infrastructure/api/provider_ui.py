"""UI configuration and form-validation helpers for the web presentation layer.

DESCRIPTION
Declares `PROVIDER_UI_CONFIG`, a per-provider matrix describing which
generation parameters are relevant, their researched min/max/default/step
bounds and the help text shown to the user, plus small parsing/validation
helpers used by the HTMX form endpoints in `web.py`.

This module belongs to the presentation (driving) adapter layer: it only
shapes how the existing `AIRequest` contract is exposed as an HTML form. It
does not implement any business rule beyond "is this input within the
researched range for this provider", mirroring the server-side validation
principle (never trust client-side constraints alone).

EXAMPLES
>>> PROVIDER_UI_CONFIG["openai_api"]["temperature"]["max"]
2.0
>>> spec = PROVIDER_UI_CONFIG["openai_api"]["temperature"]
>>> parse_float("1.5", spec, "temperature", {})
1.5
"""

from src.application.domain.ai_provider import AIProvider

DEFAULT_PROVIDER = AIProvider.OPENAI_API.value

# Per-provider UI matrix. Ranges/defaults researched and documented in the
# task brief; keep this the single source of truth for both rendering
# (templates) and server-side validation (web.py).
PROVIDER_UI_CONFIG: dict[str, dict] = {
    AIProvider.OPENAI_API.value: {
        "label": "OpenAI — Chat Completions",
        "supports": ["temperature", "top_p", "max_tokens"],
        "temperature": {
            "min": 0.0,
            "max": 2.0,
            "step": 0.1,
            "default": 1.0,
            "help": "0.0 – 2.0, default 1.0. Higher values increase randomness.",
        },
        "top_p": {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "default": 1.0,
            "help": "0.0 – 1.0, default 1.0. Nucleus sampling probability mass.",
        },
        "max_tokens": {
            "min": 1,
            "max": None,
            "default": 1024,
            "required": False,
            "help": "Actual max depends on the selected model (no universal cap).",
        },
    },
    AIProvider.CLAUDE_API.value: {
        "label": "Anthropic Claude — Messages API",
        "supports": ["sampling_toggle", "top_k", "max_tokens"],
        "sampling_toggle": True,
        "sampling_default": "temperature",
        "temperature": {
            "min": 0.0,
            "max": 1.0,
            "step": 0.1,
            "default": 1.0,
            "help": "0.0 – 1.0, default 1.0.",
        },
        "top_p": {
            "min": 0.01,
            "max": 1.0,
            "step": 0.01,
            "default": 1.0,
            "help": (
                "0.0 (exclusive) – 1.0, default 1.0. 0 is not a valid value for Claude."
            ),
        },
        "top_k": {
            "min": 1,
            "max": 500,
            "step": 1,
            "default": 40,
            "optional": True,
            "help": (
                "1 – 500 (UI-bounded; Anthropic documents no hard "
                "upper bound). Optional."
            ),
        },
        "max_tokens": {
            "min": 1,
            "max": None,
            "default": 1024,
            "required": True,
            "help": (
                "Required by Anthropic. Default 1024; model-dependent upper "
                "bound (commonly up to 8192, higher on newer models)."
            ),
        },
    },
    AIProvider.GEMINI_API.value: {
        "label": "Google Gemini — GenerateContentConfig",
        "supports": ["temperature", "top_p", "top_k", "max_tokens"],
        "temperature": {
            "min": 0.0,
            "max": 2.0,
            "step": 0.1,
            "default": 1.0,
            "help": "0.0 – 2.0, default 1.0.",
        },
        "top_p": {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "default": 0.95,
            "help": "0.0 – 1.0, default 0.95.",
        },
        "top_k": {
            "min": 1,
            "max": 100,
            "step": 1,
            "default": 40,
            "help": "Typically 1 – 100, default 40.",
        },
        "max_tokens": {
            "min": 1,
            "max": None,
            "default": 2048,
            "required": False,
            "help": (
                "Maps to Gemini's max_output_tokens. Model-dependent "
                "(commonly up to 8192, higher on newer models)."
            ),
        },
    },
    AIProvider.COPILOT_API.value: {
        "label": "Microsoft Copilot — Azure OpenAI",
        "supports": ["temperature", "top_p", "max_tokens", "deployment", "api_version"],
        "temperature": {
            "min": 0.0,
            "max": 2.0,
            "step": 0.1,
            "default": 1.0,
            "help": "0.0 – 2.0, default 1.0.",
        },
        "top_p": {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "default": 1.0,
            "help": "0.0 – 1.0, default 1.0.",
        },
        "max_tokens": {
            "min": 1,
            "max": None,
            "default": 1024,
            "required": False,
            "help": "Default 1024; actual max depends on the model/deployment.",
        },
        "deployment": {
            "help": (
                "Optional Azure deployment name override (takes precedence over model)."
            ),
            "placeholder": "e.g. gpt-4o-prod",
        },
        "api_version": {
            "help": (
                "Optional. NOTE: accepted by the API contract but not yet applied "
                "per-request — v1 always uses the server-configured "
                "COPILOT_API_VERSION."
            ),
            "placeholder": "e.g. 2024-10-21",
        },
    },
}


def get_provider_config(provider: str) -> dict | None:
    """Return the UI config for `provider`, or `None` if unknown.

    ARGS
    provider: str
        Provider identifier (e.g. "openai_api").

    RETURN
    dict | None
        The provider's UI matrix, or `None` when not recognized.

    EXAMPLES
    >>> get_provider_config("openai_api")["label"]
    'OpenAI — Chat Completions'
    >>> get_provider_config("unknown_api") is None
    True
    """
    return PROVIDER_UI_CONFIG.get(provider)


def _clean(raw: str | None) -> str | None:
    """Normalize a raw form value: strip whitespace, blank -> None."""
    if raw is None:
        return None
    stripped = raw.strip()
    return stripped if stripped != "" else None


def parse_float(
    raw: str | None,
    spec: dict | None,
    field_name: str,
    errors: dict[str, str],
    required: bool = False,
) -> float | None:
    """Parse and range-validate a float form field.

    ARGS
    raw: str | None
        Raw value submitted by the form.
    spec: dict | None
        Field spec with optional `min`/`max` bounds. `None` skips bounds.
    field_name: str
        Field name used as the key in `errors` and in messages.
    errors: dict[str, str]
        Mutable error accumulator; populated in place.
    required: bool
        Whether a blank value should be reported as an error.

    RETURN
    float | None
        The parsed value, or `None` when blank/invalid.

    EXAMPLES
    >>> parse_float("1.5", {"min": 0.0, "max": 2.0}, "temperature", {})
    1.5
    """
    value = _clean(raw)
    if value is None:
        if required:
            errors[field_name] = "This field is required."
        return None
    try:
        parsed = float(value)
    except ValueError:
        errors[field_name] = "Must be a valid number."
        return None
    if spec:
        min_v, max_v = spec.get("min"), spec.get("max")
        if min_v is not None and parsed < min_v:
            errors[field_name] = f"Must be >= {min_v}."
        elif max_v is not None and parsed > max_v:
            errors[field_name] = f"Must be <= {max_v}."
    return parsed


def parse_int(
    raw: str | None,
    spec: dict | None,
    field_name: str,
    errors: dict[str, str],
    required: bool = False,
) -> int | None:
    """Parse and range-validate an integer form field.

    ARGS
    raw: str | None
        Raw value submitted by the form.
    spec: dict | None
        Field spec with optional `min`/`max` bounds. `None` skips bounds.
    field_name: str
        Field name used as the key in `errors` and in messages.
    errors: dict[str, str]
        Mutable error accumulator; populated in place.
    required: bool
        Whether a blank value should be reported as an error.

    RETURN
    int | None
        The parsed value, or `None` when blank/invalid.

    EXAMPLES
    >>> parse_int("40", {"min": 1, "max": 100}, "top_k", {})
    40
    """
    value = _clean(raw)
    if value is None:
        if required:
            errors[field_name] = "This field is required."
        return None
    try:
        parsed = int(value)
    except ValueError:
        errors[field_name] = "Must be a whole number."
        return None
    if spec:
        min_v, max_v = spec.get("min"), spec.get("max")
        if min_v is not None and parsed < min_v:
            errors[field_name] = f"Must be >= {min_v}."
        elif max_v is not None and parsed > max_v:
            errors[field_name] = f"Must be <= {max_v}."
    return parsed


def parse_text(raw: str | None) -> str | None:
    """Normalize an optional text form field (blank -> None).

    ARGS
    raw: str | None
        Raw value submitted by the form.

    RETURN
    str | None
        The trimmed value, or `None` when blank.

    EXAMPLES
    >>> parse_text("  gpt-4o-prod  ")
    'gpt-4o-prod'
    """
    return _clean(raw)
