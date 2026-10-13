"""Demo integrations screen: linked sources, masked credentials, glassmorphism UI, neural link topology."""

from __future__ import annotations

import time
from html import escape
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from topology_builder import build_neural_topology_html

_PANEL = components.declare_component(
    "feed_panel",
    path=str(Path(__file__).resolve().parent / "components" / "feed_panel"),
)

INTEGRATIONS: list[dict[str, Any]] = [
    {
        "id": "jira",
        "name": "Atlassian Jira",
        "category": "sources",
        "kind": "source",
        "accent": "#0052CC",
        "icon": "📋",
        "blurb": "Requirements, defects, and release scope.",
        "account": "release-bot@abccorp.example",
        "secret_label": "API token",
        "secret_masked": "jira_atk_••••••••8c4f",
        "endpoint": "jira.abccorp.example · ABC",
        "telemetry": "24 stories · 7 open bugs",
        "default_on": True,
    },
    {
        "id": "gitlab",
        "name": "GitLab CI/CD",
        "category": "sources",
        "kind": "source",
        "accent": "#FC6D26",
        "icon": "🦊",
        "blurb": "Pipeline status and build artifacts.",
        "account": "svc-release-guardian",
        "secret_label": "Project token",
        "secret_masked": "glpat-••••••••3a91",
        "endpoint": "gitlab.abccorp.example/payments",
        "telemetry": "Pipeline #4821 passing",
        "default_on": True,
    },
    {
        "id": "wdio",
        "name": "WDIO Regression",
        "category": "sources",
        "kind": "source",
        "accent": "#0E7490",
        "icon": "🧪",
        "blurb": "Automated regression run results.",
        "account": "ci-runner-west-2",
        "secret_label": "Artifact key",
        "secret_masked": "wdio_ak_••••••••f02b",
        "endpoint": "S3 · build/abc-5.4/wdio",
        "telemetry": "156 tests · 89% executed",
        "default_on": True,
    },
    {
        "id": "rag_requirements",
        "name": "Requirement RAG",
        "category": "rag",
        "kind": "pipeline",
        "accent": "#7C3AED",
        "icon": "🧠",
        "blurb": "Embeddings over stories and AC patterns.",
        "account": "rag-req-prod",
        "secret_label": "Index key",
        "secret_masked": "rg_req_••••••••91de",
        "endpoint": "vector · release-req-v4",
        "telemetry": "1,240 chunks · 3 flags",
        "default_on": True,
    },
    {
        "id": "rag_defects",
        "name": "Defect Pattern RAG",
        "category": "rag",
        "kind": "pipeline",
        "accent": "#DB2777",
        "icon": "🔍",
        "blurb": "Similar defect clusters & failure modes.",
        "account": "rag-defect-prod",
        "secret_label": "Index key",
        "secret_masked": "rg_def_••••••••44ac",
        "endpoint": "vector · defect-sim-v2",
        "telemetry": "2 clusters · 1 pattern",
        "default_on": True,
    },
    {
        "id": "rag_regression",
        "name": "Flaky-Test RAG",
        "category": "rag",
        "kind": "pipeline",
        "accent": "#059669",
        "icon": "📈",
        "blurb": "Flake history tied to WDIO suites.",
        "account": "rag-wdio-prod",
        "secret_label": "Index key",
        "secret_masked": "rg_wdio_••••••••7b11",
        "endpoint": "vector · wdio-flake-hist",
        "telemetry": "4 suites with flake signal",
        "default_on": False,
    },
    {
        "id": "confluence",
        "name": "Confluence Runbooks",
        "category": "runbooks",
        "kind": "plugin",
        "accent": "#2563EB",
        "icon": "📚",
        "blurb": "Checklists & escalation runbooks.",
        "account": "docs-reader@abccorp.example",
        "secret_label": "OAuth client",
        "secret_masked": "conf_oauth_••••••••e8aa",
        "endpoint": "SPACE · Release Mgmt",
        "telemetry": "12 runbooks · 2 escalations",
        "default_on": True,
    },
    {
        "id": "orchestrator",
        "name": "Autonomous Core",
        "category": "runbooks",
        "kind": "core",
        "accent": "#4F46E5",
        "icon": "🛡️",
        "blurb": "Release Guardian risk orchestrator.",
        "account": "guardian-runtime",
        "secret_label": "Route",
        "secret_masked": "org-approved · v3-weights",
        "endpoint": "agents · multi-agent mesh",
        "telemetry": "Scoring engine · 100pt max",
        "default_on": True,
    },
]

_REQUIRED_IDS = {"jira", "gitlab", "wdio", "confluence", "orchestrator"}
for _item in INTEGRATIONS:
    _item["required"] = _item["id"] in _REQUIRED_IDS


def init_integration_state() -> None:
    if "integration_enabled" not in st.session_state:
        st.session_state.integration_enabled = {
            item["id"]: item["default_on"] for item in INTEGRATIONS
        }
    if "demo_step" not in st.session_state:
        st.session_state.demo_step = "connect"
    if "feed_filter" not in st.session_state:
        st.session_state.feed_filter = "all"
    if "last_sync_message" not in st.session_state:
        st.session_state.last_sync_message = None
    if "panel_revision" not in st.session_state:
        st.session_state.panel_revision = 0


def enabled_integrations() -> list[str]:
    return [
        item["id"]
        for item in INTEGRATIONS
        if st.session_state.integration_enabled.get(item["id"], False)
    ]


def missing_required() -> list[str]:
    enabled = st.session_state.integration_enabled
    return [
        item["name"]
        for item in INTEGRATIONS
        if item.get("required") and not enabled.get(item["id"], False)
    ]


def render_connection_panel(visible: list[dict[str, Any]]) -> None:
    enabled = st.session_state.integration_enabled
    items = [
        {
            "id": item["id"],
            "name": item["name"],
            "kind": str(item["kind"]).upper(),
            "icon": item["icon"],
            "secret": item["secret_masked"],
            "telemetry": item["telemetry"],
            "required": bool(item.get("required")),
            "on": bool(enabled.get(item["id"], item["default_on"])),
        }
        for item in visible
    ]
    result = _PANEL(
        items=items,
        height=int(st.session_state.feed_panel_height),
        revision=int(st.session_state.panel_revision),
        key="connections_panel",
    )
    if not isinstance(result, dict):
        return
    if int(result.get("revision", -1)) != int(st.session_state.panel_revision):
        return
    height = max(220, min(680, int(result.get("height") or st.session_state.feed_panel_height)))
    st.session_state.feed_panel_height = height
    reported = result.get("enabled") or {}
    changed = False
    for iid, value in reported.items():
        if iid in enabled and bool(enabled[iid]) != bool(value):
            enabled[iid] = bool(value)
            changed = True
    if changed:
        st.session_state.integration_enabled = enabled
        st.rerun()


def render_connect_step() -> bool:
    """Render the connect step as a scrollable, padded workspace.

    The Streamlit header stays clear of the title. Summary tiles size to
    their text. The connections list scrolls inside a resizable panel.
    """
    init_integration_state()
    if "feed_panel_height" not in st.session_state:
        st.session_state.feed_panel_height = 340
    enabled_map = st.session_state.integration_enabled
    linked_count = sum(1 for v in enabled_map.values() if v)
    total_count = len(INTEGRATIONS)

    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.92);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
        }
        [data-testid="stAppViewContainer"],
        section.main {
            overflow-y: auto !important;
        }
        .block-container {
            padding-top: 5.6rem !important;
            padding-bottom: 3.2rem !important;
            padding-left: 2.75rem !important;
            padding-right: 2.75rem !important;
            max-width: 1240px !important;
        }
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.15rem;
        }
        .stButton > button {
            border-radius: 10px;
            min-height: 2.45rem;
            padding: 0.35rem 0.9rem;
            font-weight: 650;
        }
        div[data-testid="stHorizontalBlock"] {
            align-items: center;
            gap: 0.85rem;
        }

        /* Glassmorphism Surface Base */
        .glass-card {
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(226, 232, 240, 0.85);
            border-radius: 14px;
            box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.04), 0 0 0 1px rgba(255, 255, 255, 0.6);
        }

        /* Top Bar */
        .glass-top-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            padding-bottom: 0.35rem;
            border-bottom: 1px solid rgba(226, 232, 240, 0.7);
        }
        .eyebrow-pill {
            font-size: 0.62rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            color: #4F46E5;
            background: rgba(238, 242, 255, 0.8);
            border: 1px solid rgba(199, 210, 254, 0.7);
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            display: inline-block;
            margin-bottom: 0.2rem;
            text-transform: uppercase;
        }
        .main-heading {
            font-size: 1.35rem;
            font-weight: 800;
            color: #0F172A;
            margin: 0;
            letter-spacing: -0.01em;
        }
        .sub-tagline {
            font-size: 0.82rem;
            color: #64748B;
            margin: 0;
        }

        /* Frosted KPI Metric Tiles */
        .section-gap { height: 1.15rem; }
        .section-label {
            font-size: 0.72rem;
            font-weight: 750;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #64748B;
            margin: 0 0 0.35rem;
        }
        .glass-kpi-tile {
            min-height: 118px;
            height: auto;
            padding: 0.95rem 1.05rem 1rem;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(226, 232, 240, 0.9);
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.04);
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            overflow: visible;
        }
        .kpi-top {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.5rem;
        }
        .kpi-label {
            font-size: 0.68rem;
            font-weight: 750;
            letter-spacing: 0.07em;
            color: #64748B;
            text-transform: uppercase;
            line-height: 1.35;
            white-space: normal;
        }
        .kpi-value {
            font-size: 1.45rem;
            font-weight: 750;
            color: #0F172A;
            line-height: 1.15;
            letter-spacing: -0.02em;
        }
        .kpi-badge {
            font-size: 0.6rem;
            font-weight: 800;
            padding: 0.12rem 0.45rem;
            border-radius: 999px;
            letter-spacing: 0.04em;
        }
        .kpi-badge-live {
            background: #ECFDF5;
            color: #047857;
            border: 1px solid #A7F3D0;
        }
        .kpi-badge-indigo {
            background: #EEF2FF;
            color: #4338CA;
            border: 1px solid #C7D2FE;
        }
        .kpi-sub {
            font-size: 0.8rem;
            color: #64748B;
            font-weight: 500;
            line-height: 1.4;
            white-space: normal;
        }
        .toolbar-note {
            font-size: 0.75rem;
            color: #94A3B8;
            margin: 0.15rem 0 0;
        }

        /* Integration Feed Rows in Scrollable Container */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px !important;
            background: rgba(255, 255, 255, 0.72);
            padding: 0.35rem 0.15rem;
        }
        .feed-row {
            display: flex;
            align-items: flex-start;
            gap: 0.7rem;
            padding: 0.7rem 0.85rem;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.96);
            border: 1px solid #E2E8F0;
            margin: 0.15rem 0.35rem 0.45rem;
            box-shadow: 0 2px 6px rgba(15, 23, 42, 0.02);
        }
        .feed-row:hover {
            border-color: #C7D2FE;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.06);
        }
        .feed-icon {
            font-size: 1.15rem;
            width: 26px;
            text-align: center;
            line-height: 1;
        }
        .feed-title {
            font-size: 0.88rem;
            font-weight: 800;
            color: #0F172A;
        }
        .feed-tag {
            font-size: 0.58rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            padding: 0.12rem 0.42rem;
            border-radius: 999px;
            background: #EEF2FF;
            color: #4F46E5;
            margin-left: 0.35rem;
        }
        .feed-secret {
            font-size: 0.72rem;
            background: #F1F5F9;
            padding: 0.08rem 0.38rem;
            border-radius: 4px;
            color: #334155;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        }
        .feed-telemetry {
            font-size: 0.72rem;
            color: #64748B;
        }

        /* Status Pills */
        .status-pill-on {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.62rem;
            font-weight: 800;
            color: #047857;
            background: #ECFDF5;
            border: 1px solid #A7F3D0;
            padding: 0.16rem 0.45rem;
            border-radius: 999px;
        }
        .status-pill-off {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            font-size: 0.62rem;
            font-weight: 700;
            color: #64748B;
            background: #F1F5F9;
            border: 1px solid #E2E8F0;
            padding: 0.16rem 0.45rem;
            border-radius: 999px;
        }
        .pulse-beacon {
            width: 5px;
            height: 5px;
            border-radius: 50%;
            background: #10B981;
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            animation: beaconPulse 2s infinite;
        }
        @keyframes beaconPulse {
            0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1.15); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* Topology Section Header */
        .topology-header-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: 1.35rem 0 0.65rem;
            padding: 0 0.15rem;
        }
        .topology-heading {
            font-size: 0.74rem;
            font-weight: 850;
            letter-spacing: 0.1em;
            color: #0F172A;
            text-transform: uppercase;
        }
        .topology-latency {
            font-size: 0.74rem;
            font-weight: 700;
            color: #4F46E5;
        }

        /* Glass Ticker Bar */
        .glass-ticker {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 0.85rem;
            padding: 0.85rem 1rem;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(226, 232, 240, 0.8);
            border-radius: 12px;
            font-size: 0.8rem;
            line-height: 1.45;
            color: #475569;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 1. Header Bar: Title, Step Indicator & Primary Action
    head_left, head_right = st.columns([2.5, 1.5], vertical_alignment="center")
    with head_left:
        st.markdown(
            f"""
            <div class="eyebrow-pill">STEP 1 OF 2 · DATA LINKING & RECEPTORS</div>
            <div style="display:flex;align-items:center;gap:.65rem;">
              <h2 class="main-heading">Release Intelligence Network</h2>
              <span class="status-pill-on"><span class="pulse-beacon"></span> {linked_count} of {total_count} CONNECTED</span>
            </div>
            <p class="sub-tagline">Connect Jira, Git pipelines, and vector RAG indices. The topology below dynamically forms neural data routes.</p>
            """,
            unsafe_allow_html=True,
        )
    with head_right:
        act_col1, act_col2 = st.columns([1, 1.5], vertical_alignment="center")
        missing = missing_required()
        with act_col1:
            if st.button("↻ Resync", use_container_width=True, type="secondary"):
                with st.spinner("Refreshing telemetry…"):
                    time.sleep(0.35)
                st.session_state.last_sync_message = (
                    f"Synchronized {linked_count} linked systems."
                )
                st.rerun()
        with act_col2:
            if st.button(
                "Continue to analysis →",
                type="primary",
                use_container_width=True,
                disabled=bool(missing),
                help=(
                    "Turn the required links back on to continue."
                    if missing
                    else "Open the scored assessment."
                ),
            ):
                st.session_state.demo_step = "analyze"
                st.session_state.entering_analysis = True
                st.session_state.last_sync_message = None
                return True
    missing = missing_required()
    if missing:
        st.caption(
            "Analysis stays off until these required links are on: "
            + ", ".join(missing)
            + ". Runbooks, Jira, GitLab, WDIO, and the core are required. RAG pipelines are optional."
        )

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1:
        st.markdown(
            """
            <div class="glass-kpi-tile">
              <div class="kpi-top">
                <span class="kpi-label">Target release</span>
                <span class="kpi-badge kpi-badge-indigo">Sprint 12</span>
              </div>
              <div class="kpi-value">ABC-5.4</div>
              <div class="kpi-sub">ABC Corp payments platform</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        st.markdown(
            f"""
            <div class="glass-kpi-tile">
              <div class="kpi-top">
                <span class="kpi-label">Connected feeds</span>
                <span class="kpi-badge kpi-badge-live">Live</span>
              </div>
              <div class="kpi-value">{linked_count}<span style="font-size:.9rem;font-weight:600;color:#64748B;"> / {total_count}</span></div>
              <div class="kpi-sub">Sources currently streaming</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        st.markdown(
            """
            <div class="glass-kpi-tile">
              <div class="kpi-top">
                <span class="kpi-label">Ingested signals</span>
                <span class="kpi-badge kpi-badge-live">Verified</span>
              </div>
              <div class="kpi-value">1,420</div>
              <div class="kpi-sub">24 stories, 156 tests, 7 defects</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        st.markdown(
            """
            <div class="glass-kpi-tile">
              <div class="kpi-top">
                <span class="kpi-label">Mesh latency</span>
                <span class="kpi-badge kpi-badge-indigo">Masked</span>
              </div>
              <div class="kpi-value">14<span style="font-size:.9rem;font-weight:600;color:#64748B;"> ms</span></div>
              <div class="kpi-sub">Demo scoring route, tokens hidden</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Connections</p>', unsafe_allow_html=True)

    ctrl_left, ctrl_right = st.columns([2.6, 1.2], vertical_alignment="bottom")
    with ctrl_left:
        filter_options = ["All", "Dev and CI", "RAG pipelines", "Runbooks"]
        selected_filter = st.radio(
            "Show",
            filter_options,
            horizontal=True,
            index=0,
            key="feed_filter_radio",
        )
    with ctrl_right:
        b1, b2 = st.columns(2, gap="small")
        with b1:
            if st.button("Link all", use_container_width=True):
                for item in INTEGRATIONS:
                    st.session_state.integration_enabled[item["id"]] = True
                st.session_state.panel_revision += 1
                st.rerun()
        with b2:
            if st.button("Unlink all", use_container_width=True):
                for item in INTEGRATIONS:
                    st.session_state.integration_enabled[item["id"]] = False
                st.session_state.panel_revision += 1
                st.rerun()

    # Filter items based on selected pill
    if selected_filter == "Dev and CI":
        visible_integrations = [i for i in INTEGRATIONS if i["category"] == "sources"]
    elif selected_filter == "RAG pipelines":
        visible_integrations = [i for i in INTEGRATIONS if i["category"] == "rag"]
    elif selected_filter == "Runbooks":
        visible_integrations = [i for i in INTEGRATIONS if i["category"] == "runbooks"]
    else:
        visible_integrations = INTEGRATIONS

    st.caption("Drag the bottom edge of the list to resize it. Scroll inside the list to move through links.")
    render_connection_panel(visible_integrations)

    # 5. Neural Link Topology Visualization (Rendered via components.html -> ZERO markdown code leakage!)
    st.markdown(
        f"""
        <div class="topology-header-row">
          <span class="topology-heading">Neural Link Topology · Data Convergence Mesh</span>
          <span class="topology-latency">⚡ {linked_count} Active Converged Pipelines · Low Latency (14ms)</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    topology_html = build_neural_topology_html(st.session_state.integration_enabled, INTEGRATIONS)
    components.html(topology_html, height=400, scrolling=False)

    # 6. Bottom Glass Ticker
    st.markdown(
        """
        <div class="glass-ticker">
          <div><strong style="color:#4F46E5;">● LIVE PIPELINE:</strong> Telemetry streaming into Autonomous Risk Engine. Evidence is evaluated across requirements, regressions, and defects.</div>
          <div><span style="color:#059669;font-weight:700;">✓ ZERO-TRUST TOKEN MASKING</span> · Deterministic Scoring · No External Data Persisted</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.last_sync_message:
        st.toast(st.session_state.last_sync_message, icon="✅")

    return False
