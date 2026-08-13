import os

import pytest

from paperbanana_web.credentials import credential_scope
from paperbanana_web.models import CredentialConfig


def test_credential_scope_isolates_provider_and_restores_environment(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "existing-google-key")
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    calls = []
    monkeypatch.setattr(
        "utils.generation_utils.reinitialize_clients",
        lambda: calls.append(
            (os.getenv("OPENROUTER_API_KEY"), os.getenv("GOOGLE_API_KEY"))
        ),
    )

    credentials = CredentialConfig(
        provider="openrouter", api_key="sk-or-visitor-session-key"
    )
    with credential_scope(credentials):
        assert os.getenv("OPENROUTER_API_KEY") == "sk-or-visitor-session-key"
        assert os.getenv("GOOGLE_API_KEY") is None

    assert os.getenv("OPENROUTER_API_KEY") is None
    assert os.getenv("GOOGLE_API_KEY") == "existing-google-key"
    assert calls == [
        ("sk-or-visitor-session-key", None),
        (None, "existing-google-key"),
    ]


def test_credential_scope_restores_environment_after_failure(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setattr(
        "utils.generation_utils.reinitialize_clients", lambda: []
    )
    credentials = CredentialConfig(
        provider="gemini", api_key="AIza-visitor-session-key"
    )

    with pytest.raises(RuntimeError, match="pipeline failed"):
        with credential_scope(credentials):
            raise RuntimeError("pipeline failed")

    assert os.getenv("GOOGLE_API_KEY") is None
    assert os.getenv("OPENROUTER_API_KEY") is None
