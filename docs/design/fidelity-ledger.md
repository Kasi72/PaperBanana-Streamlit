# PaperBanana Studio v2 fidelity ledger

Concept references:

- `paperbanana-studio-generate-v2.png`
- `paperbanana-studio-results-v2.png`

Rendered QA references were captured at 1440×1000 and 390×844.

| Area | Concept evidence | Render evidence | Resolution |
| --- | --- | --- | --- |
| Information hierarchy | Publication-ready title, concise supporting line, workbench rather than landing page | Same title and supporting copy lead the first viewport | Matched |
| Guided workflow | Connect, Describe, Configure, Generate rail | Four-step horizontal workflow remains visible on desktop and collapses to 2×2 on mobile | Intentional Streamlit-native adaptation |
| Connection security | Compact provider/API-key module with ready state | Session-only connection expander collapses after validation and never renders the key in readiness text | Matched and privacy strengthened |
| Progressive disclosure | Output, aspect, and candidate defaults visible; expert settings collapsed | Three basic selectors remain visible; pipeline, retrieval, critic, size, and models live under Advanced settings | Matched |
| Readiness guidance | Right-side readiness panel with individual checks | Live readiness panel reports credentials, method, caption, and configuration and enables generation only when complete | Matched |
| Agent explanation | Compact five-stage specialist rail | Dark navy five-stage pipeline panel mirrors the sequence and clarifies each role | Matched |
| Candidate review | Two-column candidate previews, selection, comparison, export and refine actions | Results render in two columns with selection checkboxes, PNG/refine actions, selected-set ZIP export, evolution and technical-detail tabs | Matched to Streamlit capabilities |
| Palette and typography | Warm white, near-black, restrained gold, blue and sage; editorial sans-serif | `Manrope` + `DM Mono`, warm canvas, gold primary action, blue guidance and sage status | Matched |
| Responsive behavior | Complete desktop surface | 390×844 render keeps hierarchy, controls, workflow, and connection form legible with no horizontal overflow | Added production behavior |
| Copy fidelity | Generate/refine navigation, publication-ready heading, readiness and export language | Required workflow and action labels are preserved; provider wording reflects OpenRouter/Gemini instead of the concept's placeholder OpenAI | Intentional product-correct deviation |

No material visual mismatch remains that blocks deployment. The results concept uses illustrative scientific candidate images; the production surface correctly renders the real images returned by PaperBanana instead of shipping mock content.
