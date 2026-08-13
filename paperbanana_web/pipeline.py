"""Adapters between validated Streamlit requests and PaperBanana agents."""

from __future__ import annotations

import asyncio
import base64
from pathlib import Path
from typing import Callable

from google.genai import types

from agents.critic_agent import CriticAgent
from agents.planner_agent import PlannerAgent
from agents.polish_agent import PolishAgent
from agents.retriever_agent import RetrieverAgent
from agents.stylist_agent import StylistAgent
from agents.vanilla_agent import VanillaAgent
from agents.visualizer_agent import VisualizerAgent
from paperbanana_web.credentials import credential_scope
from paperbanana_web.models import CredentialConfig, GenerationRequest
from utils import config, generation_utils
from utils.legacy_generation_options import (
    generation_additional_info,
    normalize_legacy_input_content,
)
from utils.paperviz_processor import PaperVizProcessor


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ProgressCallback = Callable[[int, int], None]


def build_candidate_inputs(request: GenerationRequest) -> list[dict]:
    base_input = {
        "caption": request.caption,
        "content": normalize_legacy_input_content(
            request.method_content, request.task_name
        ),
        "visual_intent": request.caption,
        "additional_info": generation_additional_info(
            request.aspect_ratio, request.figure_size
        ),
        "max_critic_rounds": request.max_critic_rounds,
        "task_name": request.task_name,
    }
    return [
        {
            **base_input,
            "filename": f"streamlit_candidate_{index}",
            "candidate_id": index,
        }
        for index in range(request.num_candidates)
    ]


def _processor(request: GenerationRequest) -> PaperVizProcessor:
    exp_config = config.ExpConfig(
        dataset_name="PaperBananaBench",
        task_name=request.task_name,
        split_name="demo",
        exp_mode=request.pipeline_mode,
        retrieval_setting=request.retrieval_setting,
        main_model_name=request.main_model_name,
        image_gen_model_name=request.image_gen_model_name,
        work_dir=PROJECT_ROOT,
    )
    return PaperVizProcessor(
        exp_config=exp_config,
        vanilla_agent=VanillaAgent(exp_config=exp_config),
        planner_agent=PlannerAgent(exp_config=exp_config),
        visualizer_agent=VisualizerAgent(exp_config=exp_config),
        stylist_agent=StylistAgent(exp_config=exp_config),
        critic_agent=CriticAgent(exp_config=exp_config),
        retriever_agent=RetrieverAgent(exp_config=exp_config),
        polish_agent=PolishAgent(exp_config=exp_config),
    )


async def _run_generation_async(
    request: GenerationRequest,
    on_candidate: ProgressCallback | None = None,
) -> list[dict]:
    processor = _processor(request)
    results: list[dict] = []
    async for result in processor.process_queries_batch(
        build_candidate_inputs(request),
        max_concurrent=request.num_candidates,
        do_eval=False,
    ):
        result["task_name"] = request.task_name
        results.append(result)
        if on_candidate:
            on_candidate(len(results), request.num_candidates)
    return results


def run_generation(
    request: GenerationRequest,
    credentials: CredentialConfig,
    on_candidate: ProgressCallback | None = None,
) -> list[dict]:
    with credential_scope(credentials):
        return asyncio.run(_run_generation_async(request, on_candidate))


async def _refine_image_async(
    *,
    image_bytes: bytes,
    edit_prompt: str,
    provider: str,
    image_model_name: str,
    aspect_ratio: str,
    image_size: str,
) -> tuple[bytes, str]:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    contents = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": encoded,
            },
        },
        {"type": "text", "text": edit_prompt},
    ]

    if provider == "openrouter":
        response = await generation_utils.call_openrouter_image_generation_with_retry_async(
            model_name=image_model_name,
            contents=contents,
            config={
                "system_prompt": "",
                "temperature": 1.0,
                "aspect_ratio": aspect_ratio,
                "image_size": image_size,
            },
            max_attempts=3,
            retry_delay=10,
            error_context="streamlit_refine",
        )
        via = "OpenRouter"
    else:
        response = await generation_utils.call_gemini_with_retry_async(
            model_name=image_model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=1.0,
                candidate_count=1,
                max_output_tokens=8192,
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio, image_size=image_size
                ),
            ),
            max_attempts=3,
            retry_delay=10,
            error_context="streamlit_refine",
        )
        via = "Gemini"

    if not response or response[0] == "Error":
        raise RuntimeError(f"{via} did not return a refined image.")
    try:
        return base64.b64decode(response[0]), f"Refined with {via}."
    except (ValueError, TypeError) as exc:
        raise RuntimeError(f"{via} returned invalid image data.") from exc


def refine_image(
    *,
    image_bytes: bytes,
    edit_prompt: str,
    credentials: CredentialConfig,
    image_model_name: str,
    aspect_ratio: str = "16:9",
    image_size: str = "2K",
) -> tuple[bytes, str]:
    if not image_bytes:
        raise ValueError("Choose an image to refine.")
    if not edit_prompt.strip():
        raise ValueError("Describe the changes you want.")
    with credential_scope(credentials):
        return asyncio.run(
            _refine_image_async(
                image_bytes=image_bytes,
                edit_prompt=edit_prompt.strip(),
                provider=credentials.provider,
                image_model_name=image_model_name.strip(),
                aspect_ratio=aspect_ratio,
                image_size=image_size,
            )
        )

