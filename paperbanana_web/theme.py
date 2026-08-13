"""Visual tokens and CSS for the Streamlit surface."""

APP_CSS = r"""
:root {
  --pb-ink: #101522;
  --pb-navy: #0c2147;
  --pb-muted: #667085;
  --pb-line: #dde3ec;
  --pb-soft: #f6f8fb;
  --pb-amber: #f4b942;
  --pb-amber-hover: #e9aa25;
}

.stApp { background: #ffffff; color: var(--pb-ink); }
header[data-testid="stHeader"] { background: rgba(255,255,255,.92); }
[data-testid="stSidebar"] {
  background: #f8fafc;
  border-right: 1px solid var(--pb-line);
}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top: 1.25rem; }
.block-container { max-width: 1440px; padding-top: 3.65rem; padding-bottom: 4rem; }

.pb-header {
  align-items: center;
  border-bottom: 1px solid var(--pb-line);
  display: flex;
  justify-content: space-between;
  margin: 0 0 .55rem;
  padding: .2rem 0 .65rem;
}
.pb-brand { align-items: center; display: flex; gap: .8rem; }
.pb-brand img { border-radius: 8px; height: 42px; object-fit: cover; width: 42px; }
.pb-brand-name { color: var(--pb-ink); font-size: 1.35rem; font-weight: 760; letter-spacing: -.025em; }
.pb-brand-sub { color: var(--pb-muted); font-size: .84rem; margin-left: .25rem; }
.pb-links { display: flex; gap: 1rem; }
.pb-links a { color: var(--pb-navy); font-size: .88rem; font-weight: 650; text-decoration: none; }
.pb-links a:hover { color: #264d87; }

h1 { color: var(--pb-ink) !important; font-size: clamp(2rem, 3vw, 2.75rem) !important; letter-spacing: -.045em !important; line-height: 1.08 !important; }
h2, h3 { color: var(--pb-ink) !important; letter-spacing: -.025em !important; }
p, label, [data-testid="stCaptionContainer"] { color: var(--pb-muted); }

.stButton > button, .stDownloadButton > button {
  border: 1px solid var(--pb-line);
  border-radius: 10px;
  box-shadow: none;
  font-size: .9rem;
  font-weight: 650;
  min-height: 2.65rem;
}
.stButton > button[kind="primary"] {
  background: var(--pb-amber);
  border-color: var(--pb-amber);
  color: #151515;
}
.stButton > button[kind="primary"]:hover {
  background: var(--pb-amber-hover);
  border-color: var(--pb-amber-hover);
  color: #111;
}
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-baseweb="select"] > div {
  background: #fff;
  border-color: var(--pb-line);
  border-radius: 10px;
  color: var(--pb-ink);
  font-size: .9rem;
}
[data-testid="stTextArea"] textarea { line-height: 1.55; min-height: 198px; }
[data-testid="stWidgetLabel"] p { color: #2d3648; font-size: .82rem; font-weight: 650; }

.pb-pipeline {
  align-items: start;
  display: grid;
  gap: .5rem;
  grid-template-columns: repeat(5, minmax(80px, 1fr));
  margin: 1rem 0 .5rem;
  position: relative;
}
.pb-pipeline:before {
  border-top: 1px dashed #cdd5e2;
  content: "";
  left: 8%;
  position: absolute;
  right: 8%;
  top: 16px;
}
.pb-step { color: #344054; font-size: .78rem; text-align: center; z-index: 1; }
.pb-step span {
  align-items: center;
  background: #fff;
  border: 1px solid #cfd7e4;
  border-radius: 50%;
  display: flex;
  font-size: .74rem;
  height: 32px;
  justify-content: center;
  margin: 0 auto .45rem;
  width: 32px;
}
.pb-empty { margin: 1rem auto 0; max-width: 700px; text-align: center; }
.pb-empty h3 { font-size: 1.15rem; margin: .25rem 0; }
.pb-empty p { font-size: .88rem; margin: 0 auto; max-width: 520px; }

.pb-result-heading { align-items: end; display: flex; justify-content: space-between; margin: 1.5rem 0 .75rem; }
.pb-success { color: #18864b; font-size: .86rem; }
div[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: var(--pb-line) !important;
  border-radius: 12px !important;
  box-shadow: none !important;
}
.pb-candidate-meta { color: var(--pb-muted); font-size: .78rem; margin-top: -.55rem; }
.pb-stage-name { color: var(--pb-navy); font-size: .82rem; font-weight: 700; }
.pb-stage-copy { color: var(--pb-muted); font-size: .75rem; min-height: 2.4rem; }

div[data-testid="stAlert"] { border-radius: 10px; }
hr { border-color: var(--pb-line) !important; }

@media (max-width: 760px) {
  .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 3.65rem; }
  .pb-header { align-items: flex-start; gap: .8rem; }
  .pb-brand-sub { display: none; }
  .pb-links { gap: .65rem; padding-top: .55rem; }
  .pb-pipeline { gap: .15rem; }
  .pb-step { font-size: .62rem; }
  .pb-step span { height: 26px; width: 26px; }
}
"""


PIPELINE_HTML = """
<div class="pb-pipeline" aria-label="PaperBanana pipeline">
  <div class="pb-step"><span>1</span>Retriever</div>
  <div class="pb-step"><span>2</span>Planner</div>
  <div class="pb-step"><span>3</span>Stylist</div>
  <div class="pb-step"><span>4</span>Visualizer</div>
  <div class="pb-step"><span>5</span>Critic</div>
</div>
"""
