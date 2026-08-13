"""PaperBanana Studio — deployable Streamlit Community Cloud entrypoint."""

from __future__ import annotations

import base64
from datetime import datetime
from html import escape
from pathlib import Path
import time

import streamlit as st

from paperbanana_web.examples import EXAMPLE_CAPTION, EXAMPLE_METHOD
from paperbanana_web.experience import build_readiness, can_generate
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
from paperbanana_web.studio_theme import AGENT_PIPELINE_HTML, APP_CSS, WORKFLOW_HTML


ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

st.set_page_config(
    page_title="PaperBanana Studio",
    page_icon="🍌",
    layout="wide",
    initial_sidebar_state="collapsed",
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
    for key in list(st.session_state):
        if key.startswith("candidate-select-"):
            del st.session_state[key]


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
            <div>
              <span class="pb-brand-name">PaperBanana Studio</span>
              <span class="pb-brand-sub">Scientific figures, directed by you</span>
            </div>
          </div>
          <div class="pb-links">
            <span class="pb-live"><i></i> Public research workspace</span>
            <a href="https://arxiv.org/abs/2601.23265" target="_blank">Paper ↗</a>
            <a href="https://github.com/Kasi72/PaperBanana-Streamlit" target="_blank">Source ↗</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _credential_is_ready() -> bool:
    try:
        CredentialConfig(provider=_provider(), api_key=st.session_state.api_key)
    except ValueError:
        return False
    return True


def _render_connection() -> None:
    ready = _credential_is_ready()
    status = "Session key ready" if ready else "Connect a provider"
    with st.expander(f"1 · {status}", expanded=not ready, icon="🔐"):
        st.caption(
            "Your key is kept in memory for this browser session and is never written by the app."
        )
        provider_col, key_col = st.columns([1, 2.2], vertical_alignment="bottom")
        with provider_col:
            st.segmented_control(
                "Provider",
                ["OpenRouter", "Gemini"],
                key="provider_label",
                on_change=_sync_model_defaults,
            )
        with key_col:
            placeholder = "sk-or-…" if _provider() == "openrouter" else "AIza…"
            st.text_input(
                "API key",
                type="password",
                placeholder=placeholder,
                key="api_key",
                help="Used only for requests you start in this session.",
            )
        if ready:
            st.success(f"{st.session_state.provider_label} is ready for this session.", icon="✅")
        else:
            st.caption("Paste a valid key to unlock generation and refinement.")


def _render_generation_settings() -> dict:
    st.markdown('<div class="pb-section-label">3 · Configure output</div>', unsafe_allow_html=True)
    output_col, aspect_col, candidates_col = st.columns(3)
    with output_col:
        task_name = st.selectbox("Output", ["Diagram", "Plot"])
    with aspect_col:
        aspect_ratio = st.selectbox("Aspect", ["16:9", "3:2", "21:9"])
    with candidates_col:
        num_candidates = st.selectbox("Candidates", [1, 2, 3, 4, 5, 6], index=3)

    with st.expander("Advanced settings", expanded=False, icon="⚙️"):
        pipeline_col, retrieval_col, critic_col, size_col = st.columns(4)
        with pipeline_col:
            pipeline_mode = st.selectbox(
                "Pipeline",
                ["demo_full", "demo_planner_critic"],
                format_func=lambda value: (
                    "Full pipeline" if value == "demo_full" else "Planner + Critic"
                ),
            )
        with retrieval_col:
            retrieval = st.selectbox("Retrieval", ["Auto", "None"])
        with critic_col:
            critic_rounds = st.selectbox("Critic rounds", [1, 2, 3, 4, 5], index=1)
        with size_col:
            figure_size = st.selectbox(
                "Figure size",
                ["1-3cm", "4-6cm", "7-9cm", "10-13cm", "14-17cm"],
                index=2,
            )
        model_col, image_col = st.columns(2)
        with model_col:
            st.text_input("Reasoning model", key="main_model")
        with image_col:
            st.text_input("Image model", key="image_model")
        st.caption(
            "Defaults are tuned for strong quality and sensible cost. Change these only when you need direct model control."
        )

    return {
        "pipeline_mode": pipeline_mode,
        "task_name": task_name.lower(),
        "retrieval_setting": retrieval.lower(),
        "num_candidates": num_candidates,
        "max_critic_rounds": critic_rounds,
        "aspect_ratio": aspect_ratio,
        "figure_size": figure_size,
    }


def _render_readiness(settings: dict) -> bool:
    checks = build_readiness(
        provider=_provider(),
        api_key=st.session_state.api_key,
        method_content=st.session_state.method_content,
        caption=st.session_state.caption,
        task_name=settings["task_name"],
        aspect_ratio=settings["aspect_ratio"],
        num_candidates=settings["num_candidates"],
    )
    ready = can_generate(checks)
    rows = "".join(
        f"""
        <div class="pb-check {'is-ready' if item.ready else 'is-pending'}">
          <span class="pb-check-icon">{'✓' if item.ready else str(index)}</span>
          <div><strong>{escape(item.label)}</strong><small>{escape(item.detail)}</small></div>
        </div>
        """
        for index, item in enumerate(checks, start=1)
    )
    st.markdown(
        f"""
        <section class="pb-readiness {'is-complete' if ready else ''}">
          <div class="pb-panel-kicker">Live readiness</div>
          <h3>{'Ready to generate' if ready else 'Complete your brief'}</h3>
          <p>{'All checks passed. Your generation can start.' if ready else 'PaperBanana checks the essentials as you work.'}</p>
          <div class="pb-check-list">{rows}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    return ready


def _render_empty_state() -> None:
    st.markdown(
        """
        <section class="pb-empty">
          <div class="pb-empty-mark">⌁</div>
          <div>
            <h3>Your candidate studio is ready</h3>
            <p>Complete the brief above, then PaperBanana will create multiple visual directions you can compare, refine, and export.</p>
          </div>
          <div class="pb-empty-steps">
            <span><b>01</b> Describe</span><span><b>02</b> Generate</span><span><b>03</b> Compare</span><span><b>04</b> Export</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_evolution(results: list[dict], mode: str) -> None:
    available = [index for index, item in enumerate(results) if evolution_stages(item, mode)]
    if not available:
        st.info("Evolution snapshots are not available for this run.")
        return
    selected = st.selectbox(
        "Inspect candidate",
        available,
        format_func=lambda index: f"Candidate {index + 1:02d}",
    )
    stages = evolution_stages(results[selected], mode)
    st.markdown('<div class="pb-timeline-title">Prompt → plan → critique → final</div>', unsafe_allow_html=True)
    for row_start in range(0, len(stages), 3):
        columns = st.columns(min(3, len(stages) - row_start))
        for column, stage in zip(columns, stages[row_start : row_start + 3]):
            with column:
                with st.container(border=True):
                    st.markdown(
                        f'<div class="pb-stage-name">{escape(stage["name"])}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="pb-stage-copy">{escape(stage["description"])}</div>',
                        unsafe_allow_html=True,
                    )
                    image = decode_base64_image(results[selected].get(stage["image_key"]))
                    if image:
                        st.image(image, width="stretch")


def _render_candidate_grid(results: list[dict], mode: str) -> list[int]:
    selected_indices: list[int] = []
    for row_start in range(0, len(results), 2):
        columns = st.columns(2)
        for column, index in zip(columns, range(row_start, min(row_start + 2, len(results)))):
            result = results[index]
            with column:
                with st.container(border=True):
                    title_col, select_col = st.columns([3, 1], vertical_alignment="center")
                    with title_col:
                        st.markdown(f"#### Candidate {index + 1:02d}")
                    with select_col:
                        selected = st.checkbox(
                            "Select",
                            key=f"candidate-select-{index}",
                        )
                        if selected:
                            selected_indices.append(index)
                    stages = evolution_stages(result, mode)
                    critic_count = len([s for s in stages if s["name"].startswith("Critic")])
                    st.markdown(
                        f'<div class="pb-candidate-meta">Final output · {critic_count} critic rounds · session-only</div>',
                        unsafe_allow_html=True,
                    )
                    image = final_image(result, mode)
                    if image is None:
                        st.warning("This candidate did not return a readable image.")
                        continue
                    st.image(image, width="stretch")
                    description = final_description(result, mode)
                    if description:
                        with st.expander("Generation rationale"):
                            st.write(description)
                    png = image_png_bytes(image)
                    action_one, action_two = st.columns(2)
                    with action_one:
                        st.download_button(
                            "Download PNG",
                            data=png,
                            file_name=f"paperbanana-candidate-{index + 1:02d}.png",
                            mime="image/png",
                            width="stretch",
                            key=f"download-{index}",
                        )
                    with action_two:
                        st.button(
                            "Refine",
                            on_click=_select_for_refine,
                            args=(png,),
                            width="stretch",
                            key=f"refine-{index}",
                            type="primary" if selected else "secondary",
                        )
    return selected_indices


def _render_result_details(results: list[dict], mode: str) -> None:
    for index, result in enumerate(results):
        with st.expander(f"Candidate {index + 1:02d} · generation details"):
            description = final_description(result, mode)
            st.write(description or "No additional generation description was returned.")
            stages = evolution_stages(result, mode)
            st.caption(f"{len(stages)} recorded visual stages in this candidate's pipeline.")


def _render_results() -> None:
    results = st.session_state.results
    mode = st.session_state.generation_mode
    header_left, header_right = st.columns([3, 2], vertical_alignment="center")
    with header_left:
        st.title(f"{len(results)} candidates generated")
        st.markdown(
            f'<div class="pb-success"><span>✓</span> Quality-ready · completed in {st.session_state.generation_seconds:.1f}s · kept only in this session</div>',
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
                width="stretch",
            )
        with reset_col:
            st.button("Start over", on_click=_start_over, width="stretch")

    compare_tab, evolution_tab, details_tab = st.tabs(
        ["Compare candidates", "Generation evolution", "Technical details"]
    )
    with compare_tab:
        selected_indices = _render_candidate_grid(results, mode)
        if selected_indices:
            selected_results = [results[index] for index in selected_indices]
            label = (
                "1 candidate selected"
                if len(selected_indices) == 1
                else f"{len(selected_indices)} candidates selected"
            )
            tray_left, tray_right = st.columns([3, 1], vertical_alignment="center")
            with tray_left:
                st.markdown(
                    f'<div class="pb-selection"><strong>{label}</strong><span>Compare visually above or export the selected set.</span></div>',
                    unsafe_allow_html=True,
                )
            with tray_right:
                st.download_button(
                    "Download selected",
                    data=candidate_zip(selected_results, mode),
                    file_name="paperbanana-selected-candidates.zip",
                    mime="application/zip",
                    width="stretch",
                )
    with evolution_tab:
        _render_evolution(results, mode)
    with details_tab:
        _render_result_details(results, mode)


def _run_generation(settings: dict) -> None:
    try:
        credentials = CredentialConfig(provider=_provider(), api_key=st.session_state.api_key)
        request = GenerationRequest.for_provider(
            provider=_provider(),
            method_content=st.session_state.method_content,
            caption=st.session_state.caption,
            main_model_name=st.session_state.main_model,
            image_gen_model_name=st.session_state.image_model,
            **settings,
        )
        with st.status("PaperBanana is directing the figure pipeline…", expanded=True) as status:
            st.write("Interpreting the scientific brief")
            progress = st.progress(0, text="Preparing specialist agents")

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
            status.update(label="Candidate set complete", state="complete", expanded=False)
        st.rerun()
    except Exception as exc:
        st.error(f"Generation could not start: {exc}", icon="⚠️")


def _render_generate() -> None:
    if st.session_state.results:
        _render_results()
        return

    title_col, example_col = st.columns([4, 1], vertical_alignment="bottom")
    with title_col:
        st.title("Create a publication-ready figure")
        st.caption(
            "Describe the science and communication goal. Smart defaults handle the pipeline; expert controls stay one click away."
        )
    with example_col:
        st.button("Load example", on_click=_load_example, width="stretch")

    st.markdown(WORKFLOW_HTML, unsafe_allow_html=True)
    _render_connection()

    author_col, insight_col = st.columns([2.35, 1], gap="large")
    with author_col:
        st.markdown('<div class="pb-section-label">2 · Describe the figure</div>', unsafe_allow_html=True)
        st.text_area(
            "Method or data",
            key="method_content",
            height=205,
            placeholder=(
                "Describe the method, data, variables, relationships, and key results. "
                "Structured prose, bullets, JSON, or tabular data all work."
            ),
        )
        st.text_area(
            "Figure caption",
            key="caption",
            height=145,
            placeholder=(
                "State what the figure should communicate, the intended audience, and any labels or symbols that must appear."
            ),
        )
        settings = _render_generation_settings()
        readiness = build_readiness(
            provider=_provider(),
            api_key=st.session_state.api_key,
            method_content=st.session_state.method_content,
            caption=st.session_state.caption,
            task_name=settings["task_name"],
            aspect_ratio=settings["aspect_ratio"],
            num_candidates=settings["num_candidates"],
        )
        ready = can_generate(readiness)
        if st.button(
            "Generate candidates",
            type="primary",
            width="stretch",
            disabled=not ready,
        ):
            _run_generation(settings)
        if not ready:
            st.caption("Complete the readiness checks to enable generation.")
    with insight_col:
        ready = _render_readiness(settings)
        st.markdown(AGENT_PIPELINE_HTML, unsafe_allow_html=True)
        st.markdown(
            """
            <div class="pb-pro-note">
              <strong>Professional output tip</strong>
              <p>Write the caption as the figure's single communication objective. PaperBanana uses it to critique clarity—not just to add text.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _render_empty_state()


def _render_refine() -> None:
    st.title("Refine with surgical precision")
    st.caption(
        "Upload a figure or continue from a generated candidate. Describe only the changes you want; scientific content stays anchored."
    )
    st.markdown(WORKFLOW_HTML.replace("Describe", "Upload").replace("Generate", "Refine"), unsafe_allow_html=True)
    _render_connection()
    uploaded = st.file_uploader("Upload PNG or JPEG", type=["png", "jpg", "jpeg"])
    source = uploaded.getvalue() if uploaded else st.session_state.refine_source

    before_col, controls_col = st.columns([1.25, 1], gap="large")
    with before_col:
        st.markdown('<div class="pb-section-label">Source figure</div>', unsafe_allow_html=True)
        if source:
            st.image(source, caption="Original · preserved until you generate", width="stretch")
        else:
            st.info("Choose a generated candidate or upload an image to begin.")
    with controls_col:
        st.markdown('<div class="pb-section-label">Edit direction</div>', unsafe_allow_html=True)
        intent = st.segmented_control(
            "Common intent",
            ["Polish", "Simplify", "Restyle", "Correct labels"],
            default="Polish",
        )
        prompt = st.text_area(
            "Edit instructions",
            height=180,
            placeholder=(
                "Be specific: simplify labels, increase spacing, unify line weights, and keep all scientific relationships unchanged."
            ),
        )
        resolution_col, aspect_col = st.columns(2)
        with resolution_col:
            resolution = st.selectbox("Resolution", ["2K", "4K"])
        with aspect_col:
            aspect_ratio = st.selectbox("Refined aspect", ["16:9", "3:2", "21:9"])
        refine_ready = bool(source and prompt.strip() and _credential_is_ready())
        if st.button(
            "Refine figure",
            type="primary",
            width="stretch",
            disabled=not refine_ready,
        ):
            try:
                credentials = CredentialConfig(provider=_provider(), api_key=st.session_state.api_key)
                directed_prompt = f"Primary intent: {intent or 'Polish'}. {prompt.strip()}"
                with st.spinner("Applying the edit while preserving scientific structure…"):
                    output, message = refine_image(
                        image_bytes=source or b"",
                        edit_prompt=directed_prompt,
                        credentials=credentials,
                        image_model_name=st.session_state.image_model,
                        aspect_ratio=aspect_ratio,
                        image_size=resolution,
                    )
                st.session_state.refined_image = output
                st.session_state.refine_message = message
            except Exception as exc:
                st.error(f"Refinement failed: {exc}", icon="⚠️")
        if not refine_ready:
            st.caption("Add a source image, edit instructions, and a session key to continue.")

    if st.session_state.refined_image:
        st.divider()
        result_col, export_col = st.columns([2, 1], gap="large")
        with result_col:
            st.subheader("Refined result")
            st.image(st.session_state.refined_image, width="stretch")
        with export_col:
            st.success(st.session_state.refine_message)
            st.download_button(
                "Download refined PNG",
                data=st.session_state.refined_image,
                file_name=f"paperbanana-refined-{datetime.now():%Y%m%d-%H%M}.png",
                mime="image/png",
                width="stretch",
            )


def _render_footer() -> None:
    st.markdown(
        """
        <footer class="pb-footer">
          <span>PaperBanana Studio · Public research workspace</span>
          <span>Session-only credentials · Ephemeral outputs · Apache-2.0 upstream</span>
        </footer>
        """,
        unsafe_allow_html=True,
    )


_initialize_state()
_render_header()
workspace = st.segmented_control(
    "Workspace",
    ["Generate", "Refine"],
    key="workspace",
    label_visibility="collapsed",
)

if workspace == "Refine":
    _render_refine()
else:
    _render_generate()

_render_footer()
