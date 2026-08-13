# Streamlit Studio Fidelity Ledger

Compared on 2026-08-13 at a native 1440×1000 browser viewport, with an additional 390×844 responsive check.

| Comparison point | Concept evidence | Render evidence | Resolution |
|---|---|---|---|
| App structure | Narrow settings rail, wide authoring workspace, two editors | Production render preserves the rail/workspace split and editor proportions | Matched |
| Typography | Large ink-black task heading, quiet gray supporting copy, compact control labels | Heading hierarchy, label weights, and muted copy follow the same roles | Matched; uses Streamlit's production sans stack |
| Palette | True white canvas, pale cool-gray rail, deep navy support, amber actions | Render uses `#FFFFFF`, `#F6F8FB`, `#0C2147`, and `#F4B942` tokens | Matched |
| Container model | Open workspace with hairline boundaries; no bento framing | Generate stays open; only candidate results use purposeful bordered frames | Matched |
| Pipeline/empty state | Five-step horizontal pipeline and scientific workflow illustration | Same five stages and a coordinated network → matrix → visualizer → chart asset | Matched; asset simplified for small-viewport legibility |
| Candidate comparison | Two-column candidates, per-image actions, evolution timeline | Two-column candidate frames, PNG/Refine actions, and selectable timeline implemented | Matched to Streamlit-native interaction patterns |
| Refine state | Dedicated Refine workspace reachable from top navigation and candidates | Upload/candidate source, instructions, resolution/aspect controls, before/result download | Matched |
| Mobile behavior | Responsive continuation without overflow | 390×844 render has zero horizontal overflow; sidebar collapses automatically | Fixed during QA by changing sidebar state from `expanded` to `auto` |
| Header clearance | Brand/header must remain readable | Streamlit toolbar initially overlapped the custom header | Fixed by measuring the 60px toolbar and moving the custom header below it |

## Above-the-fold copy diff

The production render preserves the accepted core copy: PaperBanana, Generate, Refine, Create a scientific figure, Method or data, Figure caption, Load example, Generate candidates, Retriever, Planner, Stylist, Visualizer, Critic, and Your candidates will appear here.

Two intentional copy changes improve functional accuracy: the subtitle is retained in the branded header, and the supporting sentence explains the real agent workflow. No decorative eyebrow, badge, fake metric, or unrelated product claim was added.

## Intentional deviations

- Streamlit's own toolbar remains visible so mobile users retain the sidebar control and hosted users retain platform actions.
- The production sidebar is narrower than the concept at 1440px because Streamlit uses a fixed rail; the main authoring proportions remain faithful.
- Result selection uses a native timeline selector instead of a custom always-expanded selected-card border, improving keyboard and mobile behavior without changing the workflow.
