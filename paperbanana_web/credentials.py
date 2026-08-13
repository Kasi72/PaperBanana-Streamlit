"""Process-safe temporary credentials for Streamlit visitor sessions.

PaperBanana's upstream provider clients are process-global. Streamlit can run
multiple sessions in one process, so a lock must cover the full pipeline call
while a visitor's key is installed.
"""

from __future__ import annotations

from contextlib import contextmanager
import os
from threading import RLock
from typing import Iterator

from paperbanana_web.models import CredentialConfig


_CREDENTIAL_LOCK = RLock()
_PROVIDER_VARIABLES = ("OPENROUTER_API_KEY", "GOOGLE_API_KEY")


@contextmanager
def credential_scope(credentials: CredentialConfig) -> Iterator[None]:
    """Install one visitor key for a complete pipeline call, then restore it."""

    from utils import generation_utils

    with _CREDENTIAL_LOCK:
        previous = {name: os.environ.get(name) for name in _PROVIDER_VARIABLES}
        try:
            for name in _PROVIDER_VARIABLES:
                os.environ.pop(name, None)
            os.environ[credentials.environment_variable] = credentials.api_key
            generation_utils.reinitialize_clients()
            yield
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
            generation_utils.reinitialize_clients()
