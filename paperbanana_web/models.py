"""Validated, UI-independent inputs for the public Streamlit app."""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_PROVIDERS = {"openrouter", "gemini"}
SUPPORTED_PIPELINES = {"demo_full", "demo_planner_critic"}
SUPPORTED_RETRIEVAL = {"auto", "none"}
SUPPORTED_ASPECT_RATIOS = {"16:9", "21:9", "3:2"}
SUPPORTED_FIGURE_SIZES = {"1-3cm", "4-6cm", "7-9cm", "10-13cm", "14-17cm"}


@dataclass(frozen=True)
class CredentialConfig:
    provider: str
    api_key: str

    def __post_init__(self) -> None:
        provider = self.provider.strip().lower()
        api_key = self.api_key.strip()
        if provider not in SUPPORTED_PROVIDERS:
            raise ValueError("Provider must be OpenRouter or Gemini.")
        if len(api_key) < 12:
            raise ValueError("API key must be at least 12 characters.")
        object.__setattr__(self, "provider", provider)
        object.__setattr__(self, "api_key", api_key)

    @property
    def environment_variable(self) -> str:
        return (
            "OPENROUTER_API_KEY"
            if self.provider == "openrouter"
            else "GOOGLE_API_KEY"
        )


@dataclass(frozen=True)
class GenerationRequest:
    method_content: str
    caption: str
    pipeline_mode: str = "demo_full"
    task_name: str = "diagram"
    retrieval_setting: str = "auto"
    num_candidates: int = 4
    aspect_ratio: str = "16:9"
    figure_size: str = "7-9cm"
    max_critic_rounds: int = 2
    main_model_name: str = ""
    image_gen_model_name: str = ""

    def __post_init__(self) -> None:
        method_content = self.method_content.strip()
        caption = self.caption.strip()
        pipeline_mode = self.pipeline_mode.strip().lower()
        task_name = "plot" if "plot" in self.task_name.lower() else "diagram"
        retrieval_setting = self.retrieval_setting.strip().lower()

        if not method_content:
            raise ValueError("Method or data is required.")
        if not caption:
            raise ValueError("Figure caption is required.")
        if pipeline_mode not in SUPPORTED_PIPELINES:
            raise ValueError("Pipeline must be Full or Planner + Critic.")
        if retrieval_setting not in SUPPORTED_RETRIEVAL:
            raise ValueError("Retrieval must be Auto or None.")
        if not 1 <= int(self.num_candidates) <= 6:
            raise ValueError("Candidates must be between 1 and 6.")
        if not 1 <= int(self.max_critic_rounds) <= 5:
            raise ValueError("Critic rounds must be between 1 and 5.")
        if self.aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
            raise ValueError("Unsupported aspect ratio.")
        if self.figure_size not in SUPPORTED_FIGURE_SIZES:
            raise ValueError("Unsupported figure size.")
        if not self.main_model_name.strip() or not self.image_gen_model_name.strip():
            raise ValueError("Both model names are required.")

        object.__setattr__(self, "method_content", method_content)
        object.__setattr__(self, "caption", caption)
        object.__setattr__(self, "pipeline_mode", pipeline_mode)
        object.__setattr__(self, "task_name", task_name)
        object.__setattr__(self, "retrieval_setting", retrieval_setting)
        object.__setattr__(self, "num_candidates", int(self.num_candidates))
        object.__setattr__(self, "max_critic_rounds", int(self.max_critic_rounds))
        object.__setattr__(self, "main_model_name", self.main_model_name.strip())
        object.__setattr__(self, "image_gen_model_name", self.image_gen_model_name.strip())

    @classmethod
    def for_provider(
        cls,
        *,
        provider: str,
        method_content: str,
        caption: str,
        **overrides,
    ) -> "GenerationRequest":
        normalized_provider = provider.strip().lower()
        if normalized_provider not in SUPPORTED_PROVIDERS:
            raise ValueError("Provider must be OpenRouter or Gemini.")
        prefix = "google/" if normalized_provider == "openrouter" else ""
        values = {
            "method_content": method_content,
            "caption": caption,
            "main_model_name": f"{prefix}gemini-3.1-pro-preview",
            "image_gen_model_name": f"{prefix}gemini-3.1-flash-image-preview",
        }
        values.update(overrides)
        return cls(**values)

