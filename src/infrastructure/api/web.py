"""Server-rendered HTML presentation adapter (HTMX + Bootstrap UI).

DESCRIPTION
Driving adapter that exposes a browser-facing UI for the same generation
use case already exposed as JSON by `app.py`'s `POST /api/v1/generate`.
Routes here are thin: they parse/validate form input against the
per-provider UI matrix in `provider_ui.py`, then delegate to the exact same
`create_ai_provider` + `AIService` application/bootstrap wiring used by the
JSON API. No business logic is duplicated here.

Routes:
    GET  /            Full HTML page with the generation form.
    GET  /favicon.ico  204 No Content (no branded icon yet; avoids noisy
                       404s in the browser console/network tab on every
                       page load).
    GET  /ui/fields    HTMX fragment: provider-specific parameter fields.
    POST /ui/generate  HTMX form submission: runs generation, returns the
                       full form section re-rendered with the result or
                       validation/service errors.

EXAMPLES
Mounted on the main FastAPI app in `app.py`:
>>> app.include_router(web_router)
"""

from pathlib import Path

from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.application.domain.ai_provider import AIProvider
from src.application.dto.ai_request import AIRequest
from src.bootstrap.dependencies import create_ai_provider
from src.infrastructure.api.provider_ui import (
    DEFAULT_PROVIDER,
    PROVIDER_UI_CONFIG,
    get_provider_config,
    parse_float,
    parse_int,
    parse_text,
)

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


def _empty_form_values() -> dict:
    """Return the default (blank) form values used for a fresh page load."""
    return {
        "model": None,
        "prompt": None,
        "temperature": None,
        "top_p": None,
        "top_k": None,
        "max_tokens": None,
        "deployment": None,
        "api_version": None,
        "claude_sampling_mode": None,
    }


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the generation page with the default provider selected.

    RETURN
    HTMLResponse
        Full HTML page (extends `base.html`) with the generation form.

    EXAMPLES
    >>> client.get('/')
    """
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "providers": PROVIDER_UI_CONFIG,
            "provider": DEFAULT_PROVIDER,
            "provider_config": PROVIDER_UI_CONFIG[DEFAULT_PROVIDER],
            "form_values": _empty_form_values(),
            "field_errors": {},
            "result": None,
        },
    )


@router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    """Return an empty 204 for the browser's automatic favicon request.

    DESCRIPTION
    No branded icon exists yet; this avoids a noisy 404 in the browser
    console/network tab on every page load without adding a binary asset.

    RETURN
    Response
        Empty body, HTTP 204.

    EXAMPLES
    >>> client.get('/favicon.ico')
    """
    return Response(status_code=204)


@router.get("/ui/fields", response_class=HTMLResponse)
async def provider_fields(
    request: Request, provider: str = DEFAULT_PROVIDER
) -> HTMLResponse:
    """Return the HTMX fragment with the parameter fields for `provider`.

    DESCRIPTION
    Triggered by `hx-get` on the provider `<select>` change event. Falls
    back to the default provider's fields (with a warning) when an unknown
    provider identifier is submitted, since this is a UI convenience
    endpoint, not the authoritative validation path (that happens on
    `POST /ui/generate`).

    ARGS
    provider: str
        Provider identifier from the `<select>` element (query param).

    RETURN
    HTMLResponse
        The `fragments/provider_fields.html` fragment for `provider`.

    EXAMPLES
    >>> client.get('/ui/fields', params={'provider': 'claude_api'})
    """
    config = get_provider_config(provider)
    selected = provider if config is not None else DEFAULT_PROVIDER
    config = config or PROVIDER_UI_CONFIG[DEFAULT_PROVIDER]

    return templates.TemplateResponse(
        request,
        "fragments/provider_fields.html",
        {
            "provider": selected,
            "provider_config": config,
            "form_values": _empty_form_values(),
            "field_errors": {},
        },
    )


@router.post("/ui/generate", response_class=HTMLResponse)
async def generate_ui(  # noqa: PLR0913 - form fields mirror the AIRequest contract
    request: Request,
    provider: str = Form(""),
    model: str = Form(""),
    prompt: str = Form(""),
    temperature: str | None = Form(None),
    top_p: str | None = Form(None),
    top_k: str | None = Form(None),
    max_tokens: str | None = Form(None),
    deployment: str | None = Form(None),
    api_version: str | None = Form(None),
    claude_sampling_mode: str | None = Form(None),
) -> HTMLResponse:
    """Validate the form, run generation, and re-render the section.

    DESCRIPTION
    Mirrors the JSON API's contract and error semantics (`app.py`):
    - Unknown/unsupported provider or provider `ValueError` -> HTTP 400.
    - Unexpected internal errors -> HTTP 500.
    Additionally performs UI-level range/requiredness validation against
    the per-provider matrix in `provider_ui.py` before ever calling the
    application layer (never trust client-side `min`/`max` alone), and on
    any failure re-renders the whole `generate-section` fragment with the
    submitted values preserved and per-field errors shown.

    RETURN
    HTMLResponse
        The `fragments/generate_section.html` fragment, with either a
        success result card, a field-validation summary, or a service
        error alert. Status code matches the JSON API's semantics.

    EXAMPLES
    >>> client.post('/ui/generate', data={
    ...     'provider': 'openai_api', 'model': 'gpt-4o', 'prompt': 'Hi',
    ... })
    """
    field_errors: dict[str, str] = {}
    raw_form_values = {
        "model": model,
        "prompt": prompt,
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens,
        "deployment": deployment,
        "api_version": api_version,
        "claude_sampling_mode": claude_sampling_mode,
    }

    config = get_provider_config(provider)
    if config is None:
        field_errors["provider"] = (
            f"'{provider}' is not a supported provider. "
            f"Valid values: {', '.join(p.value for p in AIProvider)}."
        )
        # Fall back to the default provider's matrix so the form can still
        # be re-rendered coherently alongside the error.
        render_provider = DEFAULT_PROVIDER
        render_config = PROVIDER_UI_CONFIG[DEFAULT_PROVIDER]
    else:
        render_provider = provider
        render_config = config

    if not model.strip():
        field_errors["model"] = "Model is required."
    if not prompt.strip():
        field_errors["prompt"] = "Prompt is required."

    parsed_temperature: float | None = None
    parsed_top_p: float | None = None
    parsed_top_k: int | None = None
    parsed_max_tokens: int | None = None
    parsed_deployment: str | None = None
    parsed_api_version: str | None = None

    if config is not None:
        sampling_mode = claude_sampling_mode or config.get("sampling_default")

        if config.get("sampling_toggle"):
            if sampling_mode == "top_p":
                parsed_top_p = parse_float(
                    top_p, config.get("top_p"), "top_p", field_errors
                )
            else:
                parsed_temperature = parse_float(
                    temperature,
                    config.get("temperature"),
                    "temperature",
                    field_errors,
                )
        else:
            if "temperature" in config.get("supports", []):
                parsed_temperature = parse_float(
                    temperature,
                    config.get("temperature"),
                    "temperature",
                    field_errors,
                )
            if "top_p" in config.get("supports", []):
                parsed_top_p = parse_float(
                    top_p, config.get("top_p"), "top_p", field_errors
                )

        if "top_k" in config.get("supports", []):
            parsed_top_k = parse_int(top_k, config.get("top_k"), "top_k", field_errors)

        if "max_tokens" in config.get("supports", []):
            max_tokens_spec = config.get("max_tokens", {})
            parsed_max_tokens = parse_int(
                max_tokens,
                max_tokens_spec,
                "max_tokens",
                field_errors,
                required=max_tokens_spec.get("required", False),
            )

        if "deployment" in config.get("supports", []):
            parsed_deployment = parse_text(deployment)
        if "api_version" in config.get("supports", []):
            parsed_api_version = parse_text(api_version)

    if field_errors:
        return templates.TemplateResponse(
            request,
            "fragments/generate_section.html",
            {
                "providers": PROVIDER_UI_CONFIG,
                "provider": render_provider,
                "provider_config": render_config,
                "form_values": raw_form_values,
                "field_errors": field_errors,
                "result": {
                    "kind": "error",
                    "code": "VALIDATION_ERROR",
                    "message": "Please correct the highlighted fields below.",
                },
            },
            status_code=400,
        )

    # `config is not None` was enforced above (field_errors would have
    # short-circuited otherwise), so `provider` is a known AIProvider value.
    ai_request = AIRequest(
        provider=AIProvider(provider),
        model=model,
        prompt=prompt,
        temperature=parsed_temperature,
        top_p=parsed_top_p,
        top_k=parsed_top_k,
        max_tokens=parsed_max_tokens,
        deployment=parsed_deployment,
        api_version=parsed_api_version,
    )

    try:
        ai_service = create_ai_provider(ai_request.provider)
    except ValueError:
        return templates.TemplateResponse(
            request,
            "fragments/generate_section.html",
            {
                "providers": PROVIDER_UI_CONFIG,
                "provider": render_provider,
                "provider_config": render_config,
                "form_values": raw_form_values,
                "field_errors": {},
                "result": {
                    "kind": "error",
                    "code": "UNSUPPORTED_PROVIDER",
                    "message": f"Provider '{provider}' is not supported.",
                },
            },
            status_code=400,
        )

    params = {
        "model": ai_request.model,
        "prompt": ai_request.prompt,
        "temperature": ai_request.temperature,
        "top_p": ai_request.top_p,
        "top_k": ai_request.top_k,
        "max_tokens": ai_request.max_tokens,
        "deployment": ai_request.deployment,
        "api_version": ai_request.api_version,
    }

    try:
        result_text = ai_service.generate_content(params)
    except ValueError as e:
        return templates.TemplateResponse(
            request,
            "fragments/generate_section.html",
            {
                "providers": PROVIDER_UI_CONFIG,
                "provider": render_provider,
                "provider_config": render_config,
                "form_values": raw_form_values,
                "field_errors": {},
                "result": {
                    "kind": "error",
                    "code": "PROVIDER_MISCONFIGURED",
                    "message": str(e),
                },
            },
            status_code=400,
        )
    except Exception as e:
        return templates.TemplateResponse(
            request,
            "fragments/generate_section.html",
            {
                "providers": PROVIDER_UI_CONFIG,
                "provider": render_provider,
                "provider_config": render_config,
                "form_values": raw_form_values,
                "field_errors": {},
                "result": {
                    "kind": "error",
                    "code": "INTERNAL_ERROR",
                    "message": str(e),
                },
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request,
        "fragments/generate_section.html",
        {
            "providers": PROVIDER_UI_CONFIG,
            "provider": render_provider,
            "provider_config": render_config,
            "form_values": raw_form_values,
            "field_errors": {},
            "result": {
                "kind": "success",
                "provider": ai_request.provider,
                "model": ai_request.model,
                "text": result_text,
            },
        },
        status_code=200,
    )
