# PaperBanana Streamlit Studio Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a secure, polished Streamlit Community Cloud app around PaperBanana's real generation and refinement pipeline.

**Architecture:** Keep Streamlit rendering separate from tested pipeline adapters. Preserve the upstream agents while adding a process-locked credential scope so visitor-supplied keys cannot cross concurrent sessions.

**Tech Stack:** Python 3.12, Streamlit, PaperBanana agents, Pillow, pytest

## Global Constraints

- Main deployment file is exactly `streamlit_app.py`.
- Visitor API keys remain memory-only and are restored/cleared after every pipeline call.
- OpenRouter and Gemini are the only public credential choices.
- Candidate count is 1–6; critic rounds are 1–5.
- The accepted visual references are `docs/design/paperbanana-generate-concept.png` and `docs/design/paperbanana-results-concept.png`.

---

### Task 1: Safe application domain and credentials

**Files:**
- Create: `paperbanana_web/__init__.py`
- Create: `paperbanana_web/models.py`
- Create: `paperbanana_web/credentials.py`
- Test: `tests/test_streamlit_models.py`
- Test: `tests/test_session_credentials.py`

**Interfaces:**
- Produces: `CredentialConfig(provider: str, api_key: str)`, `GenerationRequest(...)`, `credential_scope(credentials)`.

- [ ] Write tests that reject blank inputs, normalize provider-specific model defaults, and prove environment/client restoration after both success and exceptions.
- [ ] Run the focused tests and confirm they fail because the modules do not exist.
- [ ] Implement immutable request models and the locked credential context manager.
- [ ] Run focused tests, then the full suite.

### Task 2: Pipeline and result adapters

**Files:**
- Create: `paperbanana_web/pipeline.py`
- Create: `paperbanana_web/results.py`
- Create: `paperbanana_web/examples.py`
- Test: `tests/test_streamlit_results.py`

**Interfaces:**
- Consumes: `CredentialConfig`, `GenerationRequest`, `credential_scope`.
- Produces: `run_generation(request, credentials, on_candidate=None) -> list[dict]`, `refine_image(...) -> tuple[bytes, str]`, `final_image(result, mode)`, `evolution_stages(result, mode)`, `candidate_zip(results, mode) -> bytes`.

- [ ] Write failing result tests using literal base64 fixtures and verify malformed images are skipped from ZIPs.
- [ ] Implement adapters around `PaperVizProcessor` and upstream result-resolution helpers.
- [ ] Run focused tests, then the full suite.

### Task 3: Streamlit experience and deployment files

**Files:**
- Create: `streamlit_app.py`
- Create: `paperbanana_web/theme.py`
- Create: `.streamlit/config.toml`
- Create: `runtime.txt`
- Modify: `requirements.txt`
- Modify: `README.md`

**Interfaces:**
- Consumes: all Task 1–2 APIs.
- Produces: Generate/Results/Refine screens, session-local result state, PNG/ZIP downloads, deployment instructions.

- [ ] Implement the accepted visual system and responsive app shell with code-native controls.
- [ ] Implement generation progress, candidate comparison, evolution selection, refinement, downloads, and actionable error states.
- [ ] Add Community Cloud configuration and exact deployment-form values to the README.
- [ ] Run Python compilation and the full test suite.

### Task 4: Visual and runtime verification

**Files:**
- Create temporarily: browser screenshots under `work/qa/` (remove before handoff).
- Update as needed: `streamlit_app.py`, `paperbanana_web/theme.py`.

**Interfaces:**
- Produces: verified desktop/mobile rendering and a health-checked Streamlit process.

- [ ] Start Streamlit headlessly and confirm `/_stcore/health` returns `ok`.
- [ ] Exercise the Generate empty state, validation error, sample loading, Results fixture state, and Refine layout in a browser without paid API calls.
- [ ] Capture desktop and mobile screenshots; inspect them with the accepted concepts and fix visible drift.
- [ ] Run final full tests, compile checks, and repository status review.
