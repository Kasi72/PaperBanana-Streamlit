"""Pure presentation logic for the guided Streamlit generation workflow."""

from __future__ import annotations

from dataclasses import dataclass

from paperbanana_web.models import CredentialConfig


@dataclass(frozen=True)
class ReadinessCheck:
    """One user-facing prerequisite for starting a generation job."""

    label: str
    detail: str
    ready: bool


def _word_detail(value: str, empty_message: str) -> tuple[str, bool]:
    words = len(value.split())
    return (f"{words} words supplied", True) if words else (empty_message, False)


def build_readiness(
    *,
    provider: str,
    api_key: str,
    method_content: str,
    caption: str,
    task_name: str,
    aspect_ratio: str,
    num_candidates: int,
) -> list[ReadinessCheck]:
    """Describe generation readiness without leaking credential material."""

    provider_name = "OpenRouter" if provider.strip().lower() == "openrouter" else "Gemini"
    try:
        CredentialConfig(provider=provider, api_key=api_key)
    except ValueError:
        credential_detail = f"Add a session-only {provider_name} key"
        credential_ready = False
    else:
        credential_detail = f"{provider_name} key ready for this session"
        credential_ready = True

    method_detail, method_ready = _word_detail(
        method_content.strip(), "Describe the science to visualize"
    )
    caption_detail, caption_ready = _word_detail(
        caption.strip(), "State the figure's communication goal"
    )
    task_label = "Plot" if "plot" in task_name.lower() else "Diagram"

    return [
        ReadinessCheck("Provider connection", credential_detail, credential_ready),
        ReadinessCheck("Method or data", method_detail, method_ready),
        ReadinessCheck("Figure caption", caption_detail, caption_ready),
        ReadinessCheck(
            "Configuration",
            f"{task_label} · {aspect_ratio} · {int(num_candidates)} candidates",
            True,
        ),
    ]


def can_generate(checks: list[ReadinessCheck]) -> bool:
    """Return whether every prerequisite has been satisfied."""

    return bool(checks) and all(check.ready for check in checks)
