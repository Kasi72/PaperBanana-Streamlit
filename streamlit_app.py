"""PaperBanana Studio — deployable Streamlit Community Cloud entrypoint."""

from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path
import time

import streamlit as st

from paperbanana_web.examples import EXAMPLE_CAPTION, EXAMPLE_METHOD
from paperbanana_web.models import CredentialConfig, GenerationRequest
from paperbanana_web.pipeline import refine_image, run_generation
from paperbanana_web.results import (
    candidate_zip,
    decode_base64_image,
    evolution_stages,
    final_description,
    final_image,
    image_png_bytes,
)
from paperbanana_web.theme import APP_CSS, PIPELINE_HTML


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

st.set_page_config(
    page_title="PaperBanana Studio",
    page_icon="🍌",
    layout="wide",
    initial_sidebar_state="auto",
)
st.markdown(f"<style>{APP_CSS}</style>", unsafe_allow_html=True)


def _initialize_state() -> None:
    defaults = {
        "workspace": "Generate",
        "provider_label": "OpenRouter",
        "api_key": "",
        "method_content": "",
        "caption": "",
        "results": [],
        "generation_mode": "demo_full",
        "generation_seconds": 0.0,
        "main_model": "google/gemini-3.1-pro-preview",
        "image_model": "google/gemini-3.1-flash-image-preview",
        "refine_source": None,
        "refined_image": None,
        "refine_message": "",
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _provider() -> str:
    return "openrouter" if st.session_state.provider_label == "OpenRouter" else "gemini"


def _sync_model_defaults() -> None:
    prefix = "google/" if _provider() == "openrouter" else ""
    st.session_state.main_model = f"{prefix}gemini-3.1-pro-preview"
    st.session_state.image_model = f"{prefix}gemini-3.1-flash-image-preview"


def _load_example() -> None:
    st.session_state.method_content = EXAMPLE_METHOD
    st.session_state.caption = EXAMPLE_CAPTION


def _start_over() -> None:
    st.session_state.results = []
    st.session_state.generation_seconds = 0.0


def _select_for_refine(image_bytes: bytes) -> None:
    st.session_state.refine_source = image_bytes
    st.session_state.refined_image = None
    st.session_state.workspace = "Refine"


def _logo_data_url() -> str:
    encoded = base64.b64encode((ASSETS / "logo.jpg").read_bytes()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _render_header() -> None:
    st.markdown(
        f"""
        <div class="pb-header">
          <div class="pb-brand">
            <img src="{_logo_data_url()}" alt="PaperBanana logo" />
            <div><span class="pb-brand-name">PaperBanana</span>
            <span class="pb-brand-sub">Turn research into publication-ready figures</span></div>
          </div>
          <div class="pb-links">
            <a href="https://arxiv.org/abs/2601.23265" target="_blank">Paper ↗</a>
            <a href="https://github.com/dwzhu-pku/PaperBanana" target="_blank">GitHub ↗</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar() -> dict:
    with st.sidebar:
        st.subheader("Session API key")
        st.caption("Used in memory for your generation only. Never saved by this app.")
        st.segmented_control(
            "Provider",
            ["OpenRouter", "Gemini"],
            key="provider_label",
            on_change=_sync_model_defaults,
        )
        placeholder = "sk-or-…" if _provider() == "openrouter" else "AIza…"
        st.text_input("API key", type="password", placeholder=placeholder, key="api_key")
        if st.button("Connect", use_container_width=True):
            try:
                CredentialConfig(provider=_provider(), api_key=st.session_state.api_key)
            except ValueError as exc:
                st.error(str(exc), icon="⚠️")
            else:
                st.success("Ready for this session.", icon="✓")

        st.divider()
        st.subheader("Pipeline")
        pipeline_mode = st.selectbox(
            "Pipeline",
            ["demo_full", "demo_planner_critic"],
            format_func=lambda value: (
                "Full pipeline" if value == "demo_full" else "Planner + Critic"
            ),
        )
        task_name = st.segmented_control(
            "Output type", ["Diagram", "Plot"], default="Diagram"
        )
        retrieval = st.segmented_control(
            "Retrieval", ["Auto", "None"], default="Auto"
        )
        num_candidates = st.selectbox("Candidates", [1, 2, 3, 4, 5, 6], index=3)
        critic_rounds = st.selectbox("Critic rounds", [1, 2, 3, 4, 5], index=1)
        aspect_ratio = st.selectbox("Aspect ratio", ["16:9", "21:9", "3:2"])
        figure_size = st.selectbox(
            "Figure size",
            ["1-3cm", "4-6cm", "7-9cm", "10-13cm", "14-17cm"],
            index=2,
        )
        with st.expander("Advanced"):
            st.text_input("Reasoning model", key="main_model")
            st.text_input("Image model", key="image_model")

        st.caption("PaperBanana is for open research use. Review the upstream license and patent notice before commercial use.")

    return {
        "pipeline_mode": pipeline_mode,
        "task_name": (task_name or "Diagram").lower(),
        "retrieval_setting": (retrieval or "Auto").lower(),
        "num_candidates": num_candidates,
        "max_critic_rounds": critic_rounds,
        "aspect_ratio": aspect_ratio,
        "figure_size": figure_size,
    }


def _render_empty_state() -> None:
    st.markdown(PIPELINE_HTML, unsafe_allow_html=True)
    _, empty_column, _ = st.columns([1, 2, 1])
    with empty_column:
        _, illustration_column, _ = st.columns([1, 3, 1])
        with illustration_column:
            st.image(ASSETS / "empty-state-workflow.png", use_container_width=True)
        st.markdown(
            """
            <div class="pb-empty">
              <h3>Your candidates will appear here</h3>
              <p>Enter your method or data and a focused caption, then generate multiple publication-ready directions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_evolution(results: list[dict], mode: str) -> None:
    available = [index for index, item in enumerate(results) if evolution_stages(item, mode)]
    if not available:
        return
    st.divider()
    selected = st.selectbox(
        "Evolution timeline",
        available,
        format_func=lambda index: f"Candidate {index + 1}",
    )
    stages = evolution_stages(results[selected], mode)
    for row_start in range(0, len(stages), 3):
        columns = st.columns(min(3, len(stages) - row_start))
        for column, stage in zip(columns, stages[row_start : row_start + 3]):
            with column:
                st.markdown(f'<div class="pb-stage-name">{stage["name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="pb-stage-copy">{stage["description"]}</div>', unsafe_allow_html=True)
                image = decode_base64_image(results[selected].get(stage["image_key"]))
                if image:
                    st.image(image, use_container_width=True)


def _render_results() -> None:
    results = st.session_state.results
    mode = st.session_state.generation_mode
    header_left, header_right = st.columns([3, 2], vertical_alignment="bottom")
    with header_left:
        st.subheader(f"{len(results)} candidates generated")
        st.markdown(
            f'<div class="pb-success">✓ Completed in {st.session_state.generation_seconds:.1f}s · candidates remain in this session</div>',
            unsafe_allow_html=True,
        )
    with header_right:
        download_col, reset_col = st.columns(2)
        with download_col:
            st.download_button(
                "Download all",
                data=candidate_zip(results, mode),
                file_name="paperbanana-candidates.zip",
                mime="application/zip",
                use_container_width=True,
            )
        with reset_col:
            st.button("Start over", on_click=_start_over, use_container_width=True)

    for row_start in range(0, len(results), 2):
        columns = st.columns(2)
        for column, index in zip(columns, range(row_start, min(row_start + 2, len(results)))):
            result = results[index]
            with column:
                with st.container(border=True):
                    st.markdown(f"#### Candidate {index + 1}")
                    stages = evolution_stages(result, mode)
                    st.markdown(
                        f'<div class="pb-candidate-meta">{len(stages)} visual stages · {max(0, len([s for s in stages if s["name"].startswith("Critic")]))} critic rounds</div>',
                        unsafe_allow_html=True,
                    )
                    image = final_image(result, mode)
                    if image is None:
                        st.warning("This candidate did not return a readable image.")
                        continue
                    st.image(image, use_container_width=True)
                    description = final_description(result, mode)
                    if description:
                        with st.expander("Generation description"):
                            st.write(description)
                    png = image_png_bytes(image)
                    action_one, action_two = st.columns(2)
                    with action_one:
                        st.download_button(
                            "Download PNG",
                            data=png,
                            file_name=f"paperbanana-candidate-{index + 1:02d}.png",
                            mime="image/png",
                            use_container_width=True,
                            key=f"download-{index}",
                        )
                    with action_two:
                        st.button(
                            "Refine",
                            on_click=_select_for_refine,
                            args=(png,),
                            use_container_width=True,
                            key=f"refine-{index}",
                        )
    _render_evolution(results, mode)


def _render_generate(settings: dict) -> None:
    title_col, example_col = st.columns([4, 1], vertical_alignment="bottom")
    with title_col:
        st.title("Create a scientific figure")
        st.caption("Describe the science; PaperBanana's agents plan, style, visualize, and critique it.")
    with example_col:
        st.button("Load example", on_click=_load_example, use_container_width=True)

    method_col, caption_col = st.columns([1.2, 1])
    with method_col:
        st.text_area(
            "Method or data",
            key="method_content",
            height=210,
            placeholder="Describe the method, data, variables, relationships, and key results.",
        )
    with caption_col:
        st.text_area(
            "Figure caption",
            key="caption",
            height=210,
            placeholder="Explain what the figure should communicate and define important symbols.",
        )

    if st.button("Generate candidates", type="primary", use_container_width=False):
        try:
            credentials = CredentialConfig(
                provider=_provider(), api_key=st.session_state.api_key
            )
            request = GenerationRequest.for_provider(
                provider=_provider(),
                method_content=st.session_state.method_content,
                caption=st.session_state.caption,
                main_model_name=st.session_state.main_model,
                image_gen_model_name=st.session_state.image_model,
                **settings,
            )
            progress = st.progress(0, text="Preparing the agent pipeline…")

            def on_candidate(completed: int, total: int) -> None:
                progress.progress(
                    completed / total,
                    text=f"Candidate {completed} of {total} completed",
                )

            started = time.perf_counter()
            st.session_state.results = run_generation(
                request, credentials, on_candidate=on_candidate
            )
            st.session_state.generation_mode = request.pipeline_mode
            st.session_state.generation_seconds = time.perf_counter() - started
            progress.empty()
            st.rerun()
        except Exception as exc:
            st.error(f"Generation could not start: {exc}", icon="⚠️")

    if st.session_state.results:
        _render_results()
    else:
        _render_empty_state()


def _render_refine() -> None:
    st.title("Refine a figure")
    st.caption("Upload a diagram or continue from a generated candidate, then describe the exact change.")
    uploaded = st.file_uploader("Upload PNG or JPEG", type=["png", "jpg", "jpeg"])
    source = uploaded.getvalue() if uploaded else st.session_state.refine_source

    before_col, controls_col = st.columns([1.15, 1])
    with before_col:
        if source:
            st.image(source, caption="Source image", use_container_width=True)
        else:
            st.info("Choose a generated candidate or upload an image to begin.")
    with controls_col:
        prompt = st.text_area(
            "Edit instructions",
            height=150,
            placeholder="For example: simplify the labels, increase spacing, and keep the scientific content unchanged.",
        )
        resolution = st.segmented_control("Resolution", ["2K", "4K"], default="2K")
        aspect_ratio = st.selectbox("Refined aspect ratio", ["16:9", "21:9", "3:2"])
        if st.button("Refine image", type="primary", use_container_width=True):
            try:
                credentials = CredentialConfig(
                    provider=_provider(), api_key=st.session_state.api_key
                )
                with st.spinner("Refining the image…"):
                    output, message = refine_image(
                        image_bytes=source or b"",
                        edit_prompt=prompt,
                        credentials=credentials,
                        image_model_name=st.session_state.image_model,
                        aspect_ratio=aspect_ratio,
                        image_size=resolution or "2K",
                    )
                st.session_state.refined_image = output
                st.session_state.refine_message = message
            except Exception as exc:
                st.error(f"Refinement failed: {exc}", icon="⚠️")

    if st.session_state.refined_image:
        st.divider()
        st.subheader("Refined result")
        st.success(st.session_state.refine_message)
        st.image(st.session_state.refined_image, use_container_width=True)
        st.download_button(
            "Download refined PNG",
            data=st.session_state.refined_image,
            file_name=f"paperbanana-refined-{datetime.now():%Y%m%d-%H%M}.png",
            mime="image/png",
        )


_initialize_state()
_render_header()
workspace = st.segmented_control(
    "Workspace",
    ["Generate", "Refine"],
    key="workspace",
    label_visibility="collapsed",
)
sidebar_settings = _render_sidebar()

if workspace == "Refine":
    _render_refine()
else:
    _render_generate(sidebar_settings)
