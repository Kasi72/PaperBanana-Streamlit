"""Visual system and code-native UI fragments for PaperBanana Studio."""

APP_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
  --pb-canvas: #fbfaf7;
  --pb-paper: #ffffff;
  --pb-ink: #111827;
  --pb-muted: #667085;
  --pb-faint: #98a2b3;
  --pb-line: #e2e5e9;
  --pb-line-strong: #cbd2da;
  --pb-gold: #f4b942;
  --pb-gold-strong: #eaa81d;
  --pb-gold-soft: #fff8e7;
  --pb-blue: #3b82f6;
  --pb-blue-soft: #eff6ff;
  --pb-green: #3f9152;
  --pb-green-soft: #f0f8ef;
  --pb-navy: #0d1b2f;
  --pb-radius: 14px;
  --pb-shadow: 0 18px 45px rgba(17, 24, 39, .06);
}

html, body, [class*="css"] { font-family: "Manrope", sans-serif; }
.stApp { background: var(--pb-canvas); color: var(--pb-ink); }
header[data-testid="stHeader"] { background: rgba(251, 250, 247, .88); backdrop-filter: blur(14px); }
[data-testid="stSidebar"] { background: var(--pb-paper); border-right: 1px solid var(--pb-line); }
.block-container { max-width: 1480px; padding: 3.5rem 2.4rem 4rem; }

.pb-header {
  align-items: center;
  border-bottom: 1px solid var(--pb-line);
  display: flex;
  justify-content: space-between;
  margin-bottom: .8rem;
  min-height: 64px;
  padding: .25rem 0 .85rem;
}
.pb-brand { align-items: center; display: flex; gap: .75rem; }
.pb-brand img { border-radius: 10px; height: 42px; object-fit: cover; width: 42px; }
.pb-brand-name { color: var(--pb-ink); font-size: 1.25rem; font-weight: 800; letter-spacing: -.035em; }
.pb-brand-sub { color: var(--pb-muted); font-size: .78rem; margin-left: .55rem; }
.pb-links { align-items: center; display: flex; gap: 1rem; }
.pb-links a { color: var(--pb-ink); font-size: .8rem; font-weight: 700; text-decoration: none; }
.pb-links a:hover { color: var(--pb-blue); }
.pb-live { align-items: center; color: var(--pb-muted); display: inline-flex; font-size: .72rem; gap: .42rem; }
.pb-live i { background: var(--pb-green); border-radius: 50%; box-shadow: 0 0 0 4px rgba(63,145,82,.12); height: 7px; width: 7px; }

h1 { color: var(--pb-ink) !important; font-size: clamp(2rem, 3.3vw, 3.45rem) !important; font-weight: 800 !important; letter-spacing: -.06em !important; line-height: 1.03 !important; }
h2, h3, h4 { color: var(--pb-ink) !important; letter-spacing: -.035em !important; }
p, [data-testid="stCaptionContainer"] { color: var(--pb-muted); }
[data-testid="stCaptionContainer"] { font-size: .84rem; }

[data-testid="stSegmentedControl"] button { min-height: 2.55rem; }
[data-testid="stSegmentedControl"] button p { color: var(--pb-ink); font-size: .82rem; font-weight: 650; }
[data-testid="stWidgetLabel"] p { color: #344054; font-size: .78rem; font-weight: 700; letter-spacing: -.01em; }
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input,
[data-baseweb="select"] > div {
  background: var(--pb-paper);
  border-color: var(--pb-line);
  border-radius: 11px;
  color: var(--pb-ink);
  font-size: .88rem;
}
[data-testid="stTextArea"] textarea { line-height: 1.62; padding: 1rem; }
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus { border-color: var(--pb-blue); box-shadow: 0 0 0 3px rgba(59,130,246,.10); }

.stButton > button, .stDownloadButton > button {
  border: 1px solid var(--pb-line-strong);
  border-radius: 10px;
  box-shadow: none;
  color: var(--pb-ink);
  font-size: .84rem;
  font-weight: 750;
  min-height: 2.75rem;
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  border-color: #9fa9b6;
  box-shadow: 0 7px 18px rgba(17,24,39,.07);
  transform: translateY(-1px);
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #ffc83d 0%, var(--pb-gold) 100%);
  border-color: var(--pb-gold-strong);
  color: #151515;
}
.stButton > button[kind="primary"]:hover { background: var(--pb-gold-strong); color: #101010; }
.stButton > button:disabled { background: #eceff2 !important; border-color: #e1e4e8 !important; color: #98a2b3 !important; transform: none; }

[data-testid="stExpander"] {
  background: rgba(255,255,255,.72);
  border: 1px solid var(--pb-line) !important;
  border-radius: var(--pb-radius) !important;
  overflow: hidden;
}
[data-testid="stExpander"] summary p { color: var(--pb-ink); font-size: .86rem; font-weight: 750; }
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: var(--pb-paper);
  border-color: var(--pb-line) !important;
  border-radius: var(--pb-radius) !important;
  box-shadow: 0 10px 28px rgba(17,24,39,.035) !important;
  transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
  border-color: #c7cdd5 !important;
  box-shadow: var(--pb-shadow) !important;
}

.pb-workflow {
  align-items: center;
  background: var(--pb-paper);
  border: 1px solid var(--pb-line);
  border-radius: 12px;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  margin: .85rem 0 1rem;
  overflow: hidden;
}
.pb-workflow-step { align-items: center; display: flex; gap: .7rem; min-height: 58px; padding: .75rem 1rem; position: relative; }
.pb-workflow-step:not(:last-child):after { background: var(--pb-line); content: ""; height: 28px; position: absolute; right: 0; width: 1px; }
.pb-workflow-step b { align-items: center; background: var(--pb-blue-soft); border-radius: 50%; color: var(--pb-blue); display: flex; font-family: "DM Mono", monospace; font-size: .72rem; height: 26px; justify-content: center; width: 26px; }
.pb-workflow-step span { color: var(--pb-ink); display: block; font-size: .78rem; font-weight: 750; }
.pb-workflow-step small { color: var(--pb-faint); display: block; font-size: .66rem; margin-top: .1rem; }

.pb-section-label { color: var(--pb-ink); font-size: .82rem; font-weight: 800; letter-spacing: -.01em; margin: .4rem 0 .65rem; }
.pb-panel-kicker { color: var(--pb-blue); font-family: "DM Mono", monospace; font-size: .66rem; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; }
.pb-readiness {
  background: var(--pb-paper);
  border: 1px solid var(--pb-line);
  border-radius: var(--pb-radius);
  box-shadow: var(--pb-shadow);
  margin-bottom: 1rem;
  padding: 1.15rem;
}
.pb-readiness.is-complete { border-color: #bad8bd; background: linear-gradient(180deg, #fff 0%, #fbfefb 100%); }
.pb-readiness h3 { font-size: 1.18rem; margin: .25rem 0 .15rem; }
.pb-readiness > p { font-size: .76rem; margin: 0 0 .8rem; }
.pb-check-list { display: grid; gap: .35rem; }
.pb-check { align-items: center; border-top: 1px solid #f0f1f3; display: flex; gap: .7rem; padding: .62rem 0 .25rem; }
.pb-check-icon { align-items: center; background: #eef1f4; border-radius: 50%; color: #77808d; display: flex; flex: 0 0 23px; font-family: "DM Mono", monospace; font-size: .68rem; height: 23px; justify-content: center; }
.pb-check.is-ready .pb-check-icon { background: var(--pb-green-soft); color: var(--pb-green); }
.pb-check strong { color: var(--pb-ink); display: block; font-size: .74rem; }
.pb-check small { color: var(--pb-muted); display: block; font-size: .66rem; line-height: 1.3; margin-top: .08rem; }

.pb-agent-panel { background: var(--pb-navy); border-radius: var(--pb-radius); color: #fff; margin-bottom: 1rem; padding: 1.15rem; }
.pb-agent-panel .pb-panel-kicker { color: #87b7ff; }
.pb-agent-panel h3 { color: #fff !important; font-size: 1rem; margin: .25rem 0 .75rem; }
.pb-agent-step { align-items: center; display: grid; gap: .65rem; grid-template-columns: 25px 1fr; padding: .35rem 0; position: relative; }
.pb-agent-step b { align-items: center; border: 1px solid rgba(255,255,255,.28); border-radius: 50%; color: #fff; display: flex; font-family: "DM Mono", monospace; font-size: .62rem; height: 24px; justify-content: center; width: 24px; }
.pb-agent-step span { color: #f8fafc; display: block; font-size: .72rem; font-weight: 700; }
.pb-agent-step small { color: #9fb0c8; display: block; font-size: .62rem; margin-top: .04rem; }
.pb-pro-note { background: var(--pb-gold-soft); border: 1px solid #f2d68f; border-radius: 12px; padding: .9rem 1rem; }
.pb-pro-note strong { color: #62480a; font-size: .75rem; }
.pb-pro-note p { color: #7a651e; font-size: .69rem; line-height: 1.48; margin: .28rem 0 0; }

.pb-empty { align-items: center; background: #f7f8f9; border: 1px dashed var(--pb-line-strong); border-radius: var(--pb-radius); display: grid; gap: 1rem; grid-template-columns: auto 1fr auto; margin-top: 1.4rem; padding: 1.15rem 1.3rem; }
.pb-empty-mark { align-items: center; background: var(--pb-paper); border: 1px solid var(--pb-line); border-radius: 12px; color: var(--pb-blue); display: flex; font-size: 1.5rem; height: 46px; justify-content: center; width: 46px; }
.pb-empty h3 { font-size: .92rem; margin: 0 0 .12rem; }
.pb-empty p { font-size: .71rem; margin: 0; max-width: 600px; }
.pb-empty-steps { display: flex; gap: .65rem; }
.pb-empty-steps span { color: var(--pb-muted); font-size: .65rem; white-space: nowrap; }
.pb-empty-steps b { color: var(--pb-ink); font-family: "DM Mono", monospace; margin-right: .15rem; }

.pb-success { align-items: center; color: var(--pb-green); display: flex; font-size: .78rem; gap: .45rem; }
.pb-success span { align-items: center; background: var(--pb-green-soft); border-radius: 50%; display: flex; height: 22px; justify-content: center; width: 22px; }
.pb-candidate-meta { color: var(--pb-muted); font-family: "DM Mono", monospace; font-size: .65rem; margin: -.55rem 0 .65rem; }
[data-testid="stImage"] img { border-radius: 8px; }
[data-testid="stTabs"] [data-baseweb="tab-list"] { gap: .25rem; justify-content: center; }
[data-testid="stTabs"] [data-baseweb="tab"] { border-radius: 9px 9px 0 0; font-size: .8rem; font-weight: 700; padding-left: 1.2rem; padding-right: 1.2rem; }
.pb-selection { background: var(--pb-navy); border-radius: 11px; color: #fff; margin-top: .65rem; padding: .9rem 1rem; }
.pb-selection strong { display: block; font-size: .82rem; }
.pb-selection span { color: #9fb0c8; display: block; font-size: .67rem; margin-top: .1rem; }
.pb-timeline-title { color: var(--pb-ink); font-size: .8rem; font-weight: 750; margin: .6rem 0 .8rem; }
.pb-stage-name { color: var(--pb-ink); font-size: .78rem; font-weight: 800; }
.pb-stage-copy { color: var(--pb-muted); font-size: .67rem; min-height: 2.2rem; }

.pb-footer { border-top: 1px solid var(--pb-line); color: var(--pb-faint); display: flex; font-size: .64rem; justify-content: space-between; margin-top: 2.5rem; padding: 1rem 0 0; }
div[data-testid="stAlert"] { border-radius: 11px; }
hr { border-color: var(--pb-line) !important; }

@media (max-width: 980px) {
  .block-container { padding-left: 1.25rem; padding-right: 1.25rem; }
  .pb-brand-sub, .pb-live { display: none; }
  .pb-workflow { grid-template-columns: repeat(2, 1fr); }
  .pb-workflow-step:nth-child(2):after { display: none; }
  .pb-empty { grid-template-columns: auto 1fr; }
  .pb-empty-steps { grid-column: 1 / -1; }
}

@media (max-width: 640px) {
  .block-container { padding: 3.25rem .85rem 3rem; }
  .pb-header { align-items: flex-start; }
  .pb-brand img { height: 36px; width: 36px; }
  .pb-brand-name { font-size: 1rem; }
  .pb-links { gap: .55rem; padding-top: .3rem; }
  .pb-links a { font-size: .68rem; }
  h1 { font-size: 2rem !important; }
  .pb-workflow-step { gap: .48rem; min-height: 50px; padding: .55rem .62rem; }
  .pb-workflow-step small { display: none; }
  .pb-empty { align-items: flex-start; grid-template-columns: 1fr; }
  .pb-empty-mark { display: none; }
  .pb-empty-steps { display: grid; grid-template-columns: 1fr 1fr; }
  .pb-footer { gap: .5rem; flex-direction: column; }
}
"""


WORKFLOW_HTML = """
<nav class="pb-workflow" aria-label="Figure workflow">
  <div class="pb-workflow-step"><b>1</b><div><span>Connect</span><small>Session provider</small></div></div>
  <div class="pb-workflow-step"><b>2</b><div><span>Describe</span><small>Science + goal</small></div></div>
  <div class="pb-workflow-step"><b>3</b><div><span>Configure</span><small>Smart defaults</small></div></div>
  <div class="pb-workflow-step"><b>4</b><div><span>Generate</span><small>Compare outputs</small></div></div>
</nav>
"""


AGENT_PIPELINE_HTML = """
<section class="pb-agent-panel">
  <div class="pb-panel-kicker">Agent pipeline</div>
  <h3>Five specialists, one directed workflow</h3>
  <div class="pb-agent-step"><b>1</b><div><span>Retrieve</span><small>Find relevant visual references</small></div></div>
  <div class="pb-agent-step"><b>2</b><div><span>Plan</span><small>Structure the scientific message</small></div></div>
  <div class="pb-agent-step"><b>3</b><div><span>Style</span><small>Apply publication conventions</small></div></div>
  <div class="pb-agent-step"><b>4</b><div><span>Visualize</span><small>Render candidate directions</small></div></div>
  <div class="pb-agent-step"><b>5</b><div><span>Critique</span><small>Improve clarity and faithfulness</small></div></div>
</section>
"""
