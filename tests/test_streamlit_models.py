import pytest

from paperbanana_web.models import CredentialConfig, GenerationRequest


def test_openrouter_defaults_use_provider_qualified_model_ids():
    request = GenerationRequest.for_provider(
        provider="openrouter",
        method_content="A retrieval system indexes papers and answers queries.",
        caption="Overview of indexing, retrieval, and answer generation.",
    )

    assert request.main_model_name == "google/gemini-3.1-pro-preview"
    assert request.image_gen_model_name == "google/gemini-3.1-flash-image-preview"


def test_gemini_defaults_use_native_model_ids():
    request = GenerationRequest.for_provider(
        provider="gemini",
        method_content="A retrieval system indexes papers and answers queries.",
        caption="Overview of indexing, retrieval, and answer generation.",
    )

    assert request.main_model_name == "gemini-3.1-pro-preview"
    assert request.image_gen_model_name == "gemini-3.1-flash-image-preview"


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"method_content": "   "}, "Method or data is required"),
        ({"caption": ""}, "Figure caption is required"),
        ({"num_candidates": 7}, "between 1 and 6"),
        ({"max_critic_rounds": 0}, "between 1 and 5"),
        ({"retrieval_setting": "manual"}, "Retrieval must be Auto or None"),
    ],
)
def test_generation_request_rejects_public_app_invalid_input(override, message):
    values = {
        "provider": "gemini",
        "method_content": "Method text",
        "caption": "Caption text",
    }
    values.update(override)

    with pytest.raises(ValueError, match=message):
        GenerationRequest.for_provider(**values)


def test_credential_config_rejects_short_or_unknown_keys():
    with pytest.raises(ValueError, match="OpenRouter or Gemini"):
        CredentialConfig(provider="openai", api_key="sk-long-enough-for-validation")

    with pytest.raises(ValueError, match="at least 12 characters"):
        CredentialConfig(provider="gemini", api_key="tiny")

