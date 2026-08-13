# PaperBanana Streamlit Studio Design

## Goal

Create a polished, deploy-ready Streamlit application around PaperBanana's real multi-agent generation pipeline. Each visitor supplies an OpenRouter or Gemini key for the current session; the application never writes visitor credentials to disk.

## Product surface

The app has two top-level workspaces: **Generate** and **Refine**.

Generate uses a narrow settings rail for credentials and pipeline controls, with a wide authoring canvas for method/data and caption input. Successful runs present candidates in a two-column comparison layout, individual PNG downloads, a ZIP download, and a selectable evolution timeline.

Refine accepts an uploaded image or a generated candidate, edit instructions, output resolution, and aspect ratio. It presents before/after images and a PNG download.

Visual references:

- `docs/design/paperbanana-generate-concept.png`
- `docs/design/paperbanana-results-concept.png`

## Architecture

- `streamlit_app.py` owns Streamlit composition and session state only.
- `paperbanana_web/models.py` validates provider and generation input.
- `paperbanana_web/credentials.py` temporarily installs one visitor key while holding a process-wide lock, restores the prior environment afterward, and reinitializes the upstream clients at both boundaries. This prevents two Streamlit sessions from crossing credentials while preserving the upstream global-client API.
- `paperbanana_web/pipeline.py` adapts validated requests to `PaperVizProcessor`, reports per-candidate progress, and exposes image refinement.
- `paperbanana_web/results.py` decodes final outputs, exposes evolution stages, and creates in-memory ZIP downloads.
- `paperbanana_web/theme.py` contains the extracted visual tokens and Streamlit CSS.

The credential lock intentionally serializes separate visitors' generation jobs. Candidate generation within one job remains parallel. This is the safest compatibility layer for the upstream repository's process-global API clients and is appropriate for a resource-constrained Streamlit Community Cloud deployment.

## Design system

- Background: true white; secondary surface `#F6F8FB`.
- Text: ink `#101522`; muted `#667085`; support navy `#0C2147`.
- Accent: banana amber `#F4B942`; accent hover `#E9AA25`.
- Borders: `#DDE3EC`, 1px; radii 10–12px; shadows used only for active/floating feedback.
- Typography: Streamlit's sans stack with explicit sizes and weights for headings, labels, controls, and captions.
- Container model: open page, narrow rail, purposeful candidate frames; no nested card grid.

## Data flow

1. The visitor chooses a provider and enters a password-masked key held by Streamlit session state.
2. The app validates inputs and constructs an immutable generation request.
3. The pipeline adapter enters a credential scope, creates PaperBanana agents, and iterates the upstream async batch generator.
4. Progress updates after each completed candidate. Raw results stay in session memory.
5. Presentation helpers resolve each final image and evolution stages. Downloads are assembled in memory.
6. The credential scope restores all pre-existing environment values and upstream clients even on failure.

## Errors and limits

- Missing/short keys and blank method/caption fields fail before any API call.
- Public-cloud candidate count is capped at 6 and critic rounds at 5.
- Provider errors are shown without echoing credentials.
- Missing datasets degrade to the upstream no-reference behavior; users can select Retrieval = None explicitly.
- Generated files are session-memory downloads; Community Cloud storage is treated as ephemeral.

## Testing

- Unit tests cover request validation, provider/model defaults, credential restoration, image decoding, and ZIP creation.
- The complete upstream test suite must remain green.
- A Streamlit smoke test starts `streamlit_app.py` headlessly and confirms the health endpoint.
- Browser QA covers Generate, Results, and Refine layouts at desktop and mobile widths without making paid API calls.

## Deployment

The repository root exposes `streamlit_app.py`, `requirements.txt`, `.streamlit/config.toml`, and `runtime.txt`. Streamlit Community Cloud can deploy it with repository + branch + main file path `streamlit_app.py`; no server-side secrets are required.
