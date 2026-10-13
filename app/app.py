"""Executive dashboard for the AI Release Guardian MVP."""

import json
import sys
import time
from html import escape
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
for path in (ROOT, APP_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from agents.orchestrator import Orchestrator  # noqa: E402
from integrations_demo import init_integration_state, render_connect_step  # noqa: E402
from services.report_service import (  # noqa: E402
    build_csv_report,
    build_html_report,
    build_json_report,
    build_pdf_report,
)


st.set_page_config(
    page_title="Release Guardian",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --ink:#0F172A; --muted:#64748B; --line:#E2E8F0; --surface:#FFFFFF;
        --brand:#6366F1; --brand-2:#8B5CF6; --mint:#10B981; --coral:#F43F5E;
        --sun:#F59E0B; --sky:#0EA5E9;
    }
    .stApp {
        background: radial-gradient(1200px 600px at 10% -10%, #EEF2FF 0%, transparent 55%),
                    radial-gradient(900px 500px at 100% 0%, #FDF2F8 0%, transparent 50%),
                    #F8FAFC;
        color:var(--ink);
    }
    .stApp p, .stApp label, .stApp li { color:var(--ink); }
    .stApp [data-testid="stCaptionContainer"] p { color:var(--muted); }
    [data-testid="stSidebar"] { background:#FFFFFF; border-right:1px solid var(--line); }
    [data-testid="stSidebar"] * { color:var(--ink); }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background:#EEF1FF; border:1px dashed #6172E8;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small,
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span {
        color:#303A52 !important;
    }
    [data-testid="stSidebar"] button { border-color:#B8C0D1; }
    .brand { letter-spacing:.14em; font-size:.72rem; font-weight:800; color:#465CE8; }
    .hero {
        padding:1.35rem 1.55rem; border:1px solid var(--line); border-radius:18px;
        background:linear-gradient(125deg,#FFFFFF 35%,#EEF2FF 70%,#FDF4FF);
        box-shadow:0 10px 32px rgba(99,102,241,.08); margin-bottom:1rem;
    }
    .hero h1 { margin:.22rem 0 .22rem; font-size:2rem; color:var(--ink); }
    .hero p { margin:0; color:var(--muted); }
    .score-card {
        min-height:244px; padding:1.5rem; border-radius:18px; color:white;
        display:flex; flex-direction:column; justify-content:space-between;
        box-shadow:0 12px 28px rgba(28,39,66,.14);
    }
    .score-card, .score-card * { color:#FFFFFF !important; }
    .score { font-size:4.6rem; font-weight:800; line-height:1; }
    .score small { font-size:1rem; opacity:.88; }
    .decision { font-size:1.35rem; font-weight:800; letter-spacing:.04em; }
    .eyebrow { font-size:.72rem; font-weight:800; letter-spacing:.12em; opacity:.9; }
    .risk-row { padding:.72rem 0; border-bottom:1px solid #E9ECF2; color:#303A52; }
    .risk-row:last-child { border:0; }
    .risk-dot { display:inline-block; width:9px; height:9px; border-radius:50%; margin-right:.55rem; }
    .agent-label { color:#465CE8; font-weight:800; font-size:.72rem; letter-spacing:.08em; }
    .guide {
        background:#EEF1FF; border:1px solid #D5DBF7; border-radius:14px;
        padding:.95rem 1.1rem; margin:0 0 1rem; color:#303A52;
    }
    .guide strong { color:#172033; }
    .meaning { color:#FFFFFF; opacity:.94; margin:.35rem 0 0; font-weight:600; }
    .source-flow {
        display:flex; gap:.45rem; align-items:center; flex-wrap:wrap;
        margin:.4rem 0 1.2rem;
    }
    .source-node {
        background:#FFFFFF; color:#172033; border:1px solid #C7CFDC;
        border-radius:10px; padding:.55rem .72rem; font-weight:700;
    }
    .source-node.guardian { background:#172033; color:#FFFFFF; border-color:#172033; }
    .source-node.decision { background:#E8EDFF; color:#2436A8; border-color:#AEB9F0; }
    .source-arrow { color:#526076; font-weight:800; padding:.2rem 0; }
    .st-key-source_flow { margin:.15rem 0 .75rem; flex-wrap:wrap; }
    .st-key-source_flow button {
        background:#FFFFFF; color:#172033 !important; border:1px solid #C7CFDC;
        border-radius:10px; padding:.55rem .72rem; font-weight:700;
        white-space:nowrap; cursor:pointer;
    }
    .st-key-source_flow button p { color:#172033 !important; }
    .st-key-source_flow button:hover { border-color:#6172E8; }
    .st-key-source_flow button[kind="primary"] {
        background:#172033; border-color:#172033;
    }
    .st-key-source_flow button[kind="primary"] p { color:#FFFFFF !important; }
    .st-key-source_flow [data-testid="stMarkdownContainer"] { margin:0; }
    [data-testid="stVegaLiteChart"] { padding-top:1rem; overflow:visible !important; }
    [data-testid="stVegaLiteChart"] svg { overflow:visible !important; }
    button[kind="primary"] p { color:#FFFFFF !important; }
    [data-baseweb="tab"] p { color:#27344A; font-weight:650; }
    [aria-selected="true"][data-baseweb="tab"] p { color:#3046D3; }
    div[data-testid="stMetric"] {
        background:white; border:1px solid var(--line); padding:.78rem 1rem; border-radius:14px;
        box-shadow:0 3px 12px rgba(28,39,66,.035);
    }
    [data-testid="stDownloadButton"] button { width:100%; }
    .step-rail { display:flex; align-items:center; gap:.65rem; margin-bottom:1rem; flex-wrap:wrap; }
    .step-pill {
        font-size:.72rem; font-weight:800; letter-spacing:.06em; padding:.45rem .85rem;
        border-radius:999px; background:#E2E8F0; color:#475569;
    }
    .step-pill-active {
        background:linear-gradient(135deg,#6366F1,#8B5CF6); color:#FFFFFF;
        box-shadow:0 6px 18px rgba(99,102,241,.35);
    }
    .step-line { flex:1; min-width:40px; height:2px; background:linear-gradient(90deg,#C7D2FE,#E2E8F0); }
    .demo-hero-connect h1 { font-size:1.85rem; margin:.35rem 0 .5rem; }
    .int-card {
        border:1px solid var(--line); border-radius:16px; padding:1rem 1.1rem 1.15rem;
        background:var(--surface); margin-bottom:.35rem;
        border-left:4px solid var(--accent);
        box-shadow:0 4px 20px rgba(15,23,42,.04);
    }
    .int-card-top { display:flex; align-items:flex-start; gap:.65rem; }
    .int-icon { font-size:1.45rem; line-height:1; }
    .int-kind { font-size:.65rem; font-weight:800; letter-spacing:.1em; color:var(--muted); }
    .int-name { font-weight:800; font-size:1.02rem; color:var(--ink); }
    .int-blurb { font-size:.88rem; color:var(--muted); margin:.55rem 0 .75rem; }
    .int-meta { font-size:.78rem; color:#334155; display:grid; gap:.35rem; }
    .int-meta-label {
        display:inline-block; min-width:4.5rem; font-weight:700; color:#94A3B8;
        text-transform:uppercase; font-size:.62rem; letter-spacing:.08em; margin-right:.35rem;
    }
    .int-secret {
        background:#F1F5F9; padding:.12rem .45rem; border-radius:6px; font-size:.76rem;
    }
    .int-status-on, .int-status-off {
        margin-left:auto; font-size:.65rem; font-weight:800; letter-spacing:.06em;
        padding:.28rem .55rem; border-radius:999px;
    }
    .int-status-on { background:#DCFCE7; color:#166534; }
    .int-status-off { background:#F1F5F9; color:#64748B; }
    .sync-panel { display:flex; flex-wrap:wrap; gap:.5rem; margin:.25rem 0 1rem; }
    .sync-chip {
        background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px;
        padding:.55rem .75rem; font-size:.8rem; color:#334155;
        box-shadow:0 2px 8px rgba(15,23,42,.04);
    }
    .sync-chip strong { color:#4F46E5; margin-right:.35rem; }
    .sync-empty { color:var(--muted); font-size:.9rem; }
    .ai-mark {
        display:inline-block;
        margin:0 0 .28rem;
        padding:.08rem .32rem .1rem;
        border-radius:4px;
        background:#ECEFF3;
        color:#6B7280;
        font-size:.58rem;
        font-weight:700;
        letter-spacing:.08em;
        line-height:1.2;
        vertical-align:top;
    }
    .ai-mark.is-placeholder { visibility:hidden; }
    .section-tabs { margin:.35rem 0 .8rem; }
    .release-footer {
        margin-top:2rem; padding:1rem 1.15rem; border-radius:16px;
        border:1px dashed #CBD5E1; background:#FFFFFF;
    }
    .back-link { margin-bottom:.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


RECOMMENDATION_COPY = {
    "HOLD": "Do not ship yet. Fix the blockers first.",
    "CONDITIONAL GO": "Ship only if you accept the remaining risks.",
    "GO": "The evidence supports shipping, after you approve.",
}
RESULT_SCHEMA_VERSION = 3


def ai_mark(placeholder: bool = False) -> str:
    klass = "ai-mark is-placeholder" if placeholder else "ai-mark"
    return f'<div class="{klass}" title="AI-assisted">AI</div>'


def brief_loader(message: str, seconds: float = 0.4) -> None:
    with st.spinner(message):
        time.sleep(seconds)


def is_valid_release(payload: object) -> bool:
    if not isinstance(payload, dict):
        return False
    tests = payload.get("wdio_results", payload.get("tests"))
    return all(
        isinstance(payload.get(field), list)
        for field in ("stories", "defects")
    ) and isinstance(tests, list)


def current_approval(result: dict) -> dict | None:
    approval = st.session_state.get("approval")
    if not approval:
        return None
    if approval.get("run_id") != result["run_metadata"]["run_id"]:
        st.session_state.pop("approval", None)
        return None
    return approval


@st.cache_data
def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def next_step_copy(recommendation: str, has_approval: bool) -> str:
    if has_approval:
        return (
            "<strong>You're done with the decision.</strong> "
            "Download a report to share it, or try fixes to see a safer score."
        )
    if recommendation == "HOLD":
        return (
            "<strong>Next:</strong> Review why this is held, open "
            "<em>Try fixes</em> to see what would lower the score, then record "
            "your decision in <em>Approve</em>."
        )
    if recommendation == "CONDITIONAL GO":
        return (
            "<strong>Next:</strong> Check remaining risks, try extra fixes if needed, "
            "then record your decision in <em>Approve</em>."
        )
    return (
        "<strong>Next:</strong> Review the findings, then record your approval "
        "in <em>Approve</em>. Nothing ships until a person signs off."
    )


def decision_card(assessment: dict) -> None:
    meaning = RECOMMENDATION_COPY.get(
        assessment["recommendation"],
        "Review the findings and record your decision.",
    )
    st.markdown(
        f"""
        <div class="score-card" style="background:{assessment['colour']}">
          <div class="eyebrow">SHOULD WE SHIP?</div>
          <div class="score">{assessment['score']}<small>/100</small></div>
          <div>
            <div class="decision">{escape(assessment['recommendation'])}</div>
            <div class="meaning">{escape(assessment['level'])} risk · {escape(meaning)}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


FLOW_STEPS = [
    {"id": "requirements", "label": "Jira requirements", "ai": True},
    {"id": "regression", "label": "WDIO results", "ai": True},
    {"id": "defects", "label": "Jira defects", "ai": True},
    {"id": "guardian", "label": "Release Guardian", "ai": True},
    {"id": "risk", "label": "Risk analysis", "ai": True},
    {"id": "decision", "label": "Ship decision", "ai": False},
]

SECTION_TABS = [
    ("Recommendation", True, "Preparing the recommendation…"),
    ("Charts", True, "Composing charts…"),
    ("Try fixes", True, "Loading recommendation scenarios…"),
    ("Approve", False, "Opening the decision record…"),
    ("Download", False, "Preparing exports…"),
]


def select_flow_step(step_id: str) -> None:
    if st.session_state.get("flow_step") != step_id:
        st.session_state.flow_loading = True
    st.session_state.flow_step = step_id


def blocker_count(defects: dict) -> int:
    return defects.get(
        "blocker_count",
        defects.get("critical_count", 0) + defects.get("high_count", 0),
    )


def render_source_flow(analyses: dict, assessment: dict) -> None:
    if "flow_step" not in st.session_state:
        st.session_state.flow_step = FLOW_STEPS[0]["id"]

    st.caption("Click a step to see what it contributes.")
    flow_cols = st.columns(len(FLOW_STEPS))
    for column, step in zip(flow_cols, FLOW_STEPS):
        with column:
            st.markdown(ai_mark(placeholder=not step["ai"]), unsafe_allow_html=True)
            selected = st.session_state.flow_step == step["id"]
            st.button(
                step["label"],
                key=f"flow_{step['id']}",
                type="primary" if selected else "secondary",
                use_container_width=True,
                on_click=select_flow_step,
                args=(step["id"],),
            )

    if st.session_state.pop("flow_loading", False):
        brief_loader("Loading this step…", 0.32)

    step_id = st.session_state.flow_step
    with st.container(border=True):
        if step_id == "requirements":
            st.markdown("**Jira requirements**")
            st.write(
                f"{analyses['requirements']['story_count']} stories were analysed "
                "for clarity, coverage, and acceptance-criteria risk."
            )
            render_findings("Requirement Intelligence", analyses["requirements"], ai_powered=True)
        elif step_id == "regression":
            st.markdown("**WDIO regression results**")
            st.write(
                f"{analyses['regression']['execution_coverage']:.0%} of tests ran, "
                f"{analyses['regression']['failed']} failed, and "
                f"{analyses['regression']['not_run']} were skipped or not run."
            )
            render_findings("Regression Intelligence", analyses["regression"], ai_powered=True)
        elif step_id == "defects":
            st.markdown("**Jira defects**")
            st.write(
                f"{blocker_count(analyses['defects'])} Critical/High defects remain "
                "open in this release."
            )
            render_findings("Defect Intelligence", analyses["defects"], ai_powered=True)
        elif step_id == "guardian":
            st.markdown(ai_mark(), unsafe_allow_html=True)
            st.markdown("**Release Guardian**")
            st.write(
                "Specialist agents merge requirement, regression, and defect "
                "signals into one scored view. A person still approves the outcome."
            )
            st.write(
                f"Current recommendation: **{assessment['recommendation']}** "
                f"({assessment['score']}/100, {assessment['level']} risk)."
            )
        elif step_id == "risk":
            st.markdown(ai_mark(), unsafe_allow_html=True)
            st.markdown("**Risk analysis**")
            st.write("These factors produced the current score. Actual points are shown against each factor’s maximum weight:")
            for factor, score in assessment["factors"].items():
                maximum = assessment["max_factors"][factor]
                st.write(f"• {factor}: **{score:g}** of {maximum} maximum points")
        else:
            st.markdown("**GO / CONDITIONAL GO / HOLD**")
            meaning = RECOMMENDATION_COPY.get(
                assessment["recommendation"],
                "Review the findings and record your decision.",
            )
            st.write(
                f"This release is **{assessment['recommendation']}**. {meaning}"
            )


def render_findings(title: str, result: dict, ai_powered: bool = False) -> None:
    with st.container(border=True):
        if ai_powered:
            st.markdown(ai_mark(), unsafe_allow_html=True)
        st.markdown(
            f'<div class="agent-label">{escape(title.upper())}</div>',
            unsafe_allow_html=True,
        )
        if ai_powered:
            st.caption("Model-assisted findings from synced demo evidence.")
        for finding in result["findings"]:
            st.write(f"• {finding}")


def donut_chart(data: pd.DataFrame, label: str, value: str, colours: list[str]):
    return (
        alt.Chart(data)
        .mark_arc(innerRadius=55, outerRadius=88, stroke="#FFFFFF", strokeWidth=2)
        .encode(
            theta=alt.Theta(f"{value}:Q"),
            color=alt.Color(
                f"{label}:N",
                scale=alt.Scale(domain=data[label].tolist(), range=colours),
                legend=alt.Legend(orient="bottom", title=None),
            ),
            tooltip=[label, value],
        )
        .properties(height=265, padding={"top": 14, "left": 8, "right": 8, "bottom": 8})
    )


def render_release_footer(demo_release: dict, active_release: dict) -> None:
    st.markdown('<div class="release-footer">', unsafe_allow_html=True)
    st.markdown("##### This release")
    st.caption("Optional — swap the demo JSON without leaving the assessment.")
    uploaded = st.file_uploader(
        "Upload a different release (JSON)",
        type=["json"],
        help="Leave empty to keep the built-in demo release.",
        key="release_json_upload",
    )
    if uploaded is not None:
        try:
            loaded = json.load(uploaded)
        except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
            st.error("Invalid JSON. Keeping the current release.")
        else:
            if not is_valid_release(loaded):
                st.error("JSON must include stories, WDIO results, and defects.")
            elif loaded != st.session_state.custom_release:
                st.session_state.custom_release = loaded
                st.session_state.pop("run_result", None)
                st.rerun()
    using_demo = st.session_state.custom_release is None
    st.markdown(f"**{escape(str(active_release.get('release', 'Unnamed release')))}**")
    st.caption("Built-in demo release" if using_demo else "Uploaded release")
    if not using_demo and st.button("Reset to demo release", type="secondary"):
        st.session_state.custom_release = None
        st.session_state.pop("run_result", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def style_chart(chart):
    return (
        chart.configure_axis(
            labelColor="#27344A",
            titleColor="#172033",
            labelFontSize=12,
            titleFontSize=12,
        )
        .configure_legend(
            labelColor="#27344A",
            titleColor="#172033",
            labelFontSize=12,
        )
        .configure_view(stroke=None)
    )


sample_release = load_json(ROOT / "data" / "release.json")
base_config = load_json(ROOT / "config" / "risk_config.json")

init_integration_state()
if st.session_state.demo_step == "connect":
    proceeded = render_connect_step()
    if proceeded:
        st.rerun()
    st.stop()

if st.session_state.pop("entering_analysis", False):
    brief_loader("Reading linked sources…", 0.5)

if "custom_release" not in st.session_state:
    st.session_state.custom_release = None

release = st.session_state.custom_release or sample_release
config = json.loads(json.dumps(base_config))
weights_valid = True
run_requested = False

with st.sidebar:
    st.markdown("## 🛡️ Release Guardian")
    st.caption("Linked sources · scored assessment · human sign-off")
    if st.button("← Edit connections", use_container_width=True):
        st.session_state.demo_step = "connect"
        st.rerun()
    st.divider()
    config = json.loads(json.dumps(base_config))
    with st.expander("Scoring model (demo)", expanded=False):
        st.caption("Maximum points per factor (must total 100).")
        weight_labels = {
            "critical_defects": "Jira defects max",
            "failed_tests": "WDIO failures max",
            "coverage": "WDIO coverage gaps max",
            "requirement_risk": "Jira requirement risk max",
        }
        for key, label in weight_labels.items():
            config["weights"][key] = st.number_input(
                label,
                min_value=0,
                max_value=100,
                value=config["weights"][key],
                step=5,
            )
        weight_total = sum(config["weights"].values())
        st.caption(f"Maximum total: {weight_total} / 100")
        weights_valid = weight_total == 100
        if not weights_valid:
            st.warning("Weights must total 100.")

    run_requested = st.button(
        "Re-run assessment",
        type="primary",
        use_container_width=True,
        disabled=not weights_valid,
    )
    st.caption("Recommendation only — a person decides.")

orchestrator = Orchestrator(config)
input_signature = json.dumps({"release": release, "config": config}, sort_keys=True)
result_is_stale = (
    "run_result" not in st.session_state
    or st.session_state.get("result_schema_version") != RESULT_SCHEMA_VERSION
)
if result_is_stale:
    st.session_state.run_result = orchestrator.run(release)
    st.session_state.input_signature = input_signature
    st.session_state.result_schema_version = RESULT_SCHEMA_VERSION
    st.session_state.pop("approval", None)
if run_requested and weights_valid:
    with st.spinner("Re-scoring linked evidence…"):
        st.session_state.run_result = orchestrator.run(release)
        st.session_state.input_signature = input_signature
        st.session_state.result_schema_version = RESULT_SCHEMA_VERSION
        st.session_state.pop("approval", None)
    st.toast("Assessment complete", icon="✅")

result = st.session_state.run_result
assessment = result["assessment"]
analyses = result["analyses"]
evidence_changed = st.session_state.get("input_signature") != input_signature
approval = current_approval(result)

hero_left, hero_right = st.columns([4.5, 1.5], vertical_alignment="center")
with hero_left:
    st.markdown(
        f"""
        <div class="hero">
          <div class="step-rail">
            <span class="step-pill">1 · Connect</span>
            <span class="step-line"></span>
            <span class="step-pill step-pill-active">2 · Analyze</span>
          </div>
          <div class="brand">RELEASE GUARDIAN</div>
          {ai_mark()}
          <h1>{escape(str(result['release'].get('release', 'Release readiness')))}</h1>
          <p>Specialist agents scored linked evidence — review, simulate fixes, then sign off.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with hero_right:
    st.caption("ASSESSMENT ID")
    st.code(result["run_metadata"]["run_id"], language=None)
    st.caption("Keep this ID if you share a report.")

st.markdown(
    f'<div class="guide">{next_step_copy(assessment["recommendation"], bool(approval))}</div>',
    unsafe_allow_html=True,
)

st.markdown(ai_mark(), unsafe_allow_html=True)
st.markdown("#### How the assessment works")
render_source_flow(analyses, assessment)

if evidence_changed:
    st.warning("Release data or scoring weights changed. Click **Re-run assessment** in the sidebar.")

if "active_section" not in st.session_state:
    st.session_state.active_section = "Recommendation"
tab_columns = st.columns(len(SECTION_TABS))
for column, (name, uses_ai, _message) in zip(tab_columns, SECTION_TABS):
    with column:
        st.markdown(ai_mark(placeholder=not uses_ai), unsafe_allow_html=True)
        selected = st.session_state.active_section == name
        if st.button(
            name,
            key=f"section_tab_{name}",
            type="primary" if selected else "secondary",
            use_container_width=True,
        ):
            if name != st.session_state.active_section:
                st.session_state.active_section = name
                st.session_state.pending_section_load = name
                st.rerun()

pending_section = st.session_state.pop("pending_section_load", None)
if pending_section:
    load_message = next(
        message for name, _uses_ai, message in SECTION_TABS if name == pending_section
    )
    brief_loader(load_message, 0.42)
active_section = st.session_state.active_section

if active_section == "Recommendation":
    score_col, evidence_col = st.columns([1, 1.75], gap="large")
    with score_col:
        decision_card(assessment)
    with evidence_col:
        metrics = st.columns(4)
        metrics[0].metric("Stories", analyses["requirements"]["story_count"])
        metrics[1].metric(
            "WDIO tests run",
            f"{analyses['regression']['execution_coverage']:.0%}",
        )
        metrics[2].metric("WDIO failures", analyses["regression"]["failed"])
        metrics[3].metric(
            "Critical/High Jira defects",
            blocker_count(analyses["defects"]),
        )
        st.markdown(ai_mark(), unsafe_allow_html=True)
        st.markdown("#### Why this recommendation")
        for risk in assessment["top_risks"]:
            st.markdown(
                f'<div class="risk-row"><span class="risk-dot" '
                f'style="background:{assessment["colour"]}"></span>{escape(risk)}</div>',
                unsafe_allow_html=True,
            )

    st.markdown("### What to do next")
    action_columns = st.columns(min(3, len(assessment["recommended_actions"])))
    for index, action in enumerate(assessment["recommended_actions"]):
        with action_columns[index % len(action_columns)]:
            st.info(f"**{index + 1:02d}**  \n{action}")

    st.markdown("### Snapshot")
    business_metrics = st.columns(3)
    business_metrics[0].metric(
        "WDIO tests passing",
        f"{analyses['regression']['pass_rate']:.0%}",
    )
    business_metrics[1].metric(
        "Areas touched",
        f"{len(analyses['requirements']['components'])} components",
    )
    business_metrics[2].metric(
        "Acceptance criteria at risk",
        len(analyses["requirements"]["unclear_acceptance_criteria"])
        + len(analyses["requirements"]["potentially_untested_acceptance_criteria"]),
    )

    st.markdown("### What we checked")
    st.caption("Findings from Jira requirements, WDIO regressions, and Jira defects.")
    agent_columns = st.columns(2)
    with agent_columns[0]:
        render_findings("Requirement Intelligence", analyses["requirements"], ai_powered=True)
        render_findings("Defect Intelligence", analyses["defects"], ai_powered=True)
    with agent_columns[1]:
        render_findings("Regression Intelligence", analyses["regression"], ai_powered=True)

if active_section == "Charts":
    st.markdown("### Charts")
    st.caption("Use these to explain the score in a review meeting.")
    chart_left, chart_right = st.columns(2)
    test_data = pd.DataFrame(
        {
            "Status": ["Passed", "Failed", "Skipped / not run"],
            "Tests": [
                analyses["regression"]["passed"],
                analyses["regression"]["failed"],
                analyses["regression"]["not_run"],
            ],
        }
    )
    with chart_left:
        st.markdown("#### Test results")
        st.altair_chart(
            style_chart(
                donut_chart(
                    test_data,
                    "Status",
                    "Tests",
                    ["#16815D", "#B42318", "#B66B00"],
                )
            ),
            use_container_width=True,
        )

    factor_data = pd.DataFrame(
        [
            {
                "Factor": factor,
                "Actual points": score,
                "Maximum points": assessment["max_factors"][factor],
            }
            for factor, score in assessment["factors"].items()
        ]
    )
    with chart_right:
        st.markdown("#### What is driving the score")
        st.caption("Bars show actual points earned. Hover to see the maximum weight.")
        factor_chart = (
            alt.Chart(factor_data)
            .mark_bar(cornerRadiusEnd=5, color="#465CE8")
            .encode(
                x=alt.X(
                    "Actual points:Q",
                    scale=alt.Scale(
                        domain=[0, max(assessment["max_factors"].values() or [30])]
                    ),
                    title="Actual risk points",
                ),
                y=alt.Y("Factor:N", sort="-x", title=None),
                tooltip=["Factor", "Actual points", "Maximum points"],
            )
            .properties(height=245)
        )
        st.altair_chart(style_chart(factor_chart), use_container_width=True)

    component_rows = []
    for component in analyses["requirements"]["components"]:
        component_rows.append(
            {
                "Component": component,
                "Stories": sum(
                    story.get("component") == component
                    for story in result["release"].get("stories", [])
                ),
                "Open defects": sum(
                    defect.get("component") == component
                    and defect.get("status", "").lower() not in {"closed", "resolved", "done"}
                    for defect in result["release"].get("defects", [])
                ),
            }
        )
    component_data = pd.DataFrame(component_rows).melt(
        "Component", var_name="Evidence", value_name="Count"
    )
    st.markdown("#### Risk by area")
    component_chart = (
        alt.Chart(component_data)
        .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X("Component:N", title=None),
            y=alt.Y("Count:Q", title="Items"),
            color=alt.Color(
                "Evidence:N",
                scale=alt.Scale(range=["#465CE8", "#B42318"]),
                legend=alt.Legend(orient="top", title=None),
            ),
            tooltip=["Component", "Evidence", "Count"],
        )
        .properties(height=280)
    )
    st.altair_chart(style_chart(component_chart), use_container_width=True)

if active_section == "Try fixes":
    st.markdown(ai_mark(), unsafe_allow_html=True)
    st.markdown("### Try fixes before you ship")
    st.caption("These are simulations. They do not change the original release data.")
    options = st.columns(4)
    for column in options:
        column.markdown(ai_mark(), unsafe_allow_html=True)
    resolve_blockers = options[0].checkbox(
        "Fix Critical and High bugs",
        help=f"Resolves {blocker_count(analyses['defects'])} open release blockers.",
    )
    pass_failed = options[1].checkbox(
        "Pass currently failing tests",
        help=f"Passes {analyses['regression']['failed']} failed WDIO tests.",
    )
    execute_unrun = options[2].checkbox(
        "Run tests that were skipped",
        help=f"Runs {analyses['regression']['not_run']} skipped or unexecuted tests.",
    )
    resolve_requirements = options[3].checkbox(
        "Validate requirement risks",
        help="Validates high-risk stories and unclear or uncovered acceptance criteria.",
    )

    with st.expander("See the reasons these fixes address", expanded=True):
        st.write(
            f"• **Defects:** {blocker_count(analyses['defects'])} Critical/High blockers — "
            + ", ".join(
                defect.get("id", "Unknown")
                for defect in analyses["defects"].get("blockers", [])
            )
        )
        st.write(
            f"• **Failures:** {analyses['regression']['failed']} failed WDIO tests — "
            + ", ".join(
                test.get("id", "Unknown")
                for test in analyses["regression"].get("failed_tests", [])
            )
        )
        st.write(
            f"• **Coverage:** {analyses['regression']['not_run']} tests are skipped or not run; "
            f"{len(analyses['regression']['critical_untested'])} are critical."
        )
        st.write(
            f"• **Requirements:** {analyses['requirements']['high_risk_story_count']} "
            "high-risk stories, "
            f"{len(analyses['requirements']['unclear_acceptance_criteria'])} ambiguous "
            "acceptance criteria, and "
            f"{len(analyses['requirements']['potentially_untested_acceptance_criteria'])} "
            "criteria without a clearly matching WDIO scenario."
        )

    scenario_signature = (
        resolve_blockers,
        pass_failed,
        execute_unrun,
        resolve_requirements,
    )
    if st.session_state.get("scenario_signature") != scenario_signature:
        if "scenario_signature" in st.session_state:
            brief_loader("Running the recommendation scenario…", 0.45)
        st.session_state.scenario_signature = scenario_signature

    selected_scenario = {
        "resolve_blocker_defects": resolve_blockers,
        "pass_failed_tests": pass_failed,
        "execute_unrun_tests": execute_unrun,
        "resolve_requirement_risks": resolve_requirements,
    }
    simulated = orchestrator.run(result["release"], selected_scenario)
    simulated_assessment = simulated["assessment"]
    before, arrow, after = st.columns([1, .16, 1])
    with before:
        st.caption("NOW")
        decision_card(assessment)
    with arrow:
        st.markdown(
            "<div style='font-size:2rem;text-align:center;padding-top:7rem'>→</div>",
            unsafe_allow_html=True,
        )
    with after:
        st.caption("IF YOU APPLY THESE FIXES")
        decision_card(simulated_assessment)

    remaining_factors = {
        factor: points
        for factor, points in simulated_assessment["factors"].items()
        if points > 0
    }
    any_fix_selected = any(selected_scenario.values())
    if simulated_assessment["score"] == 0:
        st.success(
            "All modeled risk reasons are resolved. The simulated score is 0/100 (0%)."
        )
    elif any_fix_selected:
        remaining_copy = "; ".join(
            (
                f"{factor}: {points:g} of "
                f"{simulated_assessment['max_factors'][factor]} max"
            )
            for factor, points in remaining_factors.items()
        )
        st.info(
            f"Remaining {simulated_assessment['score']}/100 after these fixes — "
            f"{remaining_copy}."
        )

    trajectory_scenarios = [
        ("Current", {}),
        ("Fix blockers", {"resolve_blocker_defects": True}),
        (
            "Rerun failures",
            {"resolve_blocker_defects": True, "pass_failed_tests": True},
        ),
        (
            "Close gaps",
            {
                "resolve_blocker_defects": True,
                "pass_failed_tests": True,
                "execute_unrun_tests": True,
            },
        ),
        (
            "Validate requirements",
            {
                "resolve_blocker_defects": True,
                "pass_failed_tests": True,
                "execute_unrun_tests": True,
                "resolve_requirement_risks": True,
            },
        ),
    ]
    trajectory = pd.DataFrame(
        [
            {
                "Step": step,
                "Order": index,
                "Risk score": orchestrator.run(result["release"], scenario)["assessment"]["score"],
            }
            for index, (step, scenario) in enumerate(trajectory_scenarios)
        ]
    )
    st.markdown("#### How the score can come down")
    line = (
        alt.Chart(trajectory)
        .mark_line(point=alt.OverlayMarkDef(size=85), strokeWidth=3, color="#465CE8")
        .encode(
            x=alt.X("Step:N", sort=trajectory["Step"].tolist(), title=None),
            y=alt.Y("Risk score:Q", scale=alt.Scale(domain=[0, 100])),
            tooltip=["Step", "Risk score"],
        )
        .properties(height=280)
    )
    bands = (
        alt.Chart(pd.DataFrame([
            {"from": 0, "to": 30, "Band": "GO"},
            {"from": 30, "to": 60, "Band": "CONDITIONAL GO"},
            {"from": 60, "to": 100, "Band": "HOLD"},
        ]))
        .mark_rect(opacity=.08)
        .encode(
            y="from:Q",
            y2="to:Q",
            color=alt.Color(
                "Band:N",
                scale=alt.Scale(
                    domain=["GO", "CONDITIONAL GO", "HOLD"],
                    range=["#16815D", "#E39B18", "#B42318"],
                ),
                legend=None,
            ),
        )
    )
    st.altair_chart(style_chart(bands + line), use_container_width=True)

if active_section == "Approve":
    st.markdown("### Your decision")
    st.write(
        f"The app recommends **{assessment['recommendation']}**. "
        "A person must accept or override that before this is treated as final."
    )
    choice = st.radio(
        "What do you want to do?",
        [
            f"Accept — {assessment['recommendation']}",
            "Override the recommendation",
        ],
    )
    override = choice.startswith("Override")
    override_decision = None
    if override:
        override_decision = st.selectbox(
            "Override to",
            ["HOLD", "CONDITIONAL GO", "GO"],
            help="Record the decision you are taking instead of the app recommendation.",
        )
    reason = st.text_area(
        "Why are you making this decision?",
        placeholder="Required if you override. Helpful for every release.",
    )
    approver = st.text_input("Your name or role", placeholder="e.g. Release Manager")
    if st.button("Save decision", type="primary"):
        if override and not override_decision:
            st.error("Please choose the decision you are overriding to.")
        elif override and not reason.strip():
            st.error("Please explain why you are overriding the recommendation.")
        elif not approver.strip():
            st.error("Please add your name or role.")
        else:
            st.session_state.approval = {
                "decision": (
                    f"Override — {override_decision}"
                    if override
                    else choice
                ),
                "recommendation": assessment["recommendation"],
                "approver": approver,
                "reason": reason or "AI recommendation accepted.",
                "run_id": result["run_metadata"]["run_id"],
            }
            st.success("Decision saved. You can download it from the Download tab.")
    if current_approval(result):
        st.markdown("#### Saved decision")
        st.json(st.session_state.approval)

if active_section == "Download":
    st.markdown("### Download a report")
    st.caption("Share the scored result with stakeholders or keep it for audit.")
    if approval:
        st.success("Your saved decision will be included in PDF, HTML, and JSON reports.")
    else:
        st.info("No human decision is saved yet. Reports will show approval as pending.")

    filename = str(result["release"].get("release", "release")).replace(" ", "-")
    downloads = st.columns(4)
    downloads[0].download_button(
        "PDF",
        data=build_pdf_report(result, approval),
        file_name=f"{filename}-risk-report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    downloads[1].download_button(
        "Printable HTML",
        data=build_html_report(result, approval),
        file_name=f"{filename}-risk-report.html",
        mime="text/html",
        use_container_width=True,
    )
    downloads[2].download_button(
        "JSON",
        data=build_json_report(result, approval),
        file_name=f"{filename}-decision.json",
        mime="application/json",
        use_container_width=True,
    )
    downloads[3].download_button(
        "CSV",
        data=build_csv_report(result),
        file_name=f"{filename}-risk-factors.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.markdown("#### What's in the report")
    report_contents = st.columns(3)
    report_contents[0].metric("Risk reasons", len(assessment["top_risks"]))
    report_contents[1].metric("Recommended actions", len(assessment["recommended_actions"]))
    report_contents[2].metric("Your decision", "Saved" if approval else "Pending")
    with st.expander("Preview the decision record"):
        st.json(
            {
                "run": result["run_metadata"],
                "assessment": assessment,
                "human_approval": approval,
            }
        )

render_release_footer(sample_release, release)
st.caption("Release Guardian · Agents recommend · A person decides")
