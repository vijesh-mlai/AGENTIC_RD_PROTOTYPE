import os

import pandas as pd
import streamlit as st

from agents import EvidenceReadinessAgent, FormulationIntelligenceAgent
from authoring import render_evidence_pack_md, render_formulation_recs_md
from data_gen import generate_synthetic_dev_notes, generate_synthetic_formulation_data
from orchestrator import orchestrate


# -----------------------------------------------------------------------------
# Simple Login Gate
# -----------------------------------------------------------------------------
APP_PASSWORD = os.environ.get("APP_PASSWORD", "demo-access")


def login_gate() -> None:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.title("🔒 Restricted Access")
        st.write("This prototype is for internal validation purposes only.")

        pwd = st.text_input("Enter access password", type="password")

        if st.button("Access Demo"):
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")

        st.stop()  # Critical: stops rest of app from running


login_gate()

# -----------------------------------------------------------------------------
# Guided Demo Mode (Sidebar Walkthrough)
# Place this AFTER login_gate() and BEFORE st.set_page_config / st.title (or right after set_page_config).
# -----------------------------------------------------------------------------
st.sidebar.title("Guided Demo")
demo_step = st.sidebar.radio(
    "Select walkthrough step",
    [
        "Overview",
        "Formulation Intelligence",
        "Development Readiness",
        "Orchestration (Shadow)",
    ],
)

# Optional: map step -> suggested tab index (based on your current tab order)
STEP_TO_TAB = {
    "Overview": 0,                  # Management View
    "Formulation Intelligence": 2,   # Workstream A
    "Development Readiness": 3,      # Workstream B
    "Orchestration (Shadow)": 4,     # Workstream C
}

if demo_step == "Overview":
    st.info("Start here: Review the Management View.")
elif demo_step == "Formulation Intelligence":
    st.info("Next: Explore Workstream A and generate recommendations.")
elif demo_step == "Development Readiness":
    st.info("Then: Review traceable evidence packs (NOT CSR).")
elif demo_step == "Orchestration (Shadow)":
    st.info("Finally: Compare policy-based rankings.")

st.sidebar.markdown("---")
st.sidebar.write("This guided mode ensures consistent demos across audiences.")

# Optional: show a hint telling viewers which tab to click
st.sidebar.caption(f"Suggested tab: {tabs[STEP_TO_TAB[demo_step]]._title}")  # remove if it errors

# -----------------------------------------------------------------------------
# App Shell
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Agentic R&D Topical Demo", layout="wide")
st.title("Agentic AI Validation Demo — Topical Product R&D (Synthetic Data)")
st.caption(
    "Three-workstream prototype: (A) Formulation Intelligence, "
    "(B) Development Readiness, (C) Orchestration (shadow mode)."
)

# -----------------------------------------------------------------------------
# Data (Synthetic)
# -----------------------------------------------------------------------------
@st.cache_data
def load_or_make_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = generate_synthetic_formulation_data(n=1200, seed=7)
    notes = generate_synthetic_dev_notes(df, n_notes=200, seed=11)
    return df, notes


df, notes = load_or_make_data()


# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tabs = st.tabs(
    [
        "Management View",
        "Management Metrics",
        "Workstream A: Formulation Intelligence",
        "Workstream B: Development Readiness",
        "Workstream C: Orchestration (Shadow)",
    ]
)


# -----------------------------------------------------------------------------
# Tab 0 — Executive Summary
# -----------------------------------------------------------------------------
with tabs[0]:
    st.markdown("---")
    st.subheader("What We Validated vs What We Did Not")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### ✅ Validated")
        st.markdown(
            """
- Agentic reasoning for R&D decision support
- Early risk and trade-off visibility
- Traceable, reviewable outputs
- Shadow-mode orchestration
- Human-in-the-loop governance
"""
        )

    with col_right:
        st.markdown("### ❌ Not Validated")
        st.markdown(
            """
- Production integration
- Automated execution
- Regulatory submissions or CSRs
- Replacement of scientific judgment
- Use of real or sensitive data
"""
        )


# -----------------------------------------------------------------------------
# Tab 1 — Management Metrics
# -----------------------------------------------------------------------------
with tabs[1]:
    st.subheader("Management Metrics — Validation Signals (Synthetic)")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            label="Estimated Experiment Cycles Avoided",
            value="3–5 per program",
            delta="Earlier feasibility clarity",
        )

    with m2:
        st.metric(
            label="High-Risk Formulations Flagged Early",
            value="18%",
            delta="Before lab execution",
        )

    with m3:
        st.metric(
            label="Evidence Readiness Improvement",
            value="~30–40%",
            delta="Cleaner downstream handoff",
        )

    st.markdown("---")
    st.markdown("### What these metrics represent")
    st.write(
        """
- **Avoided cycles**: recommendations that deprioritized low-probability paths
- **Risk flags**: stability / irritation / QC signals surfaced earlier
- **Readiness improvement**: fewer clarification loops downstream
"""
    )

    st.info(
        "These are directional indicators from synthetic data. "
        "In a real POC, these would be measured against baseline R&D performance."
    )


# -----------------------------------------------------------------------------
# Tab 2 — Workstream A
# -----------------------------------------------------------------------------
with tabs[2]:
    st.subheader("Workstream A — Formulation Intelligence & Trade-off Agent (R&D-owned)")
    st.write(
        "Generate next-best experiment proposals with constraints. "
        "Outputs are decision-support only."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        max_irr = st.slider("Max irritation (constraint)", 0.10, 0.90, 0.65, 0.01)

    with c2:
        min_stab = st.slider("Min stability days (constraint)", 15, 365, 120, 5)

    with c3:
        max_fail = st.slider("Max QC fail probability (constraint)", 0.05, 0.90, 0.40, 0.01)

    policy = st.selectbox(
        "Decision policy (for ranking)",
        ["balanced", "speed_to_clinic", "low_risk"],
    )

    agent = FormulationIntelligenceAgent()
    proposals = agent.propose_next_experiments(
        n=12,
        constraints={
            "max_irritation": max_irr,
            "min_stability": min_stab,
            "max_fail_prob": max_fail,
        },
    )

    ranked = orchestrate(proposals, policy=policy)

    st.markdown("### Ranked recommendations")
    st.dataframe(
        ranked[
            [
                "proposal_id",
                "pred_permeability",
                "pred_irritation",
                "pred_stability",
                "pred_qc_fail_prob",
                "policy_score",
            ]
        ],
        use_container_width=True,
    )

    st.markdown("### Traceable recommendation summary (internal decision-support)")
    md = render_formulation_recs_md(ranked, policy=policy, top_k=5)
    st.code(md, language="markdown")

    st.download_button(
        "Download ranked recommendations (CSV)",
        ranked.to_csv(index=False).encode("utf-8"),
        file_name=f"ranked_{policy}.csv",
    )
    st.download_button(
        "Download recommendation summary (MD)",
        md.encode("utf-8"),
        file_name=f"summary_{policy}.md",
    )


# -----------------------------------------------------------------------------
# Tab 3 — Workstream B
# -----------------------------------------------------------------------------
with tabs[3]:
    st.subheader("Workstream B — Development Readiness & Evidence Intelligence (R&D-adjacent)")
    st.write(
        "Creates traceable evidence packs to improve readiness and cross-functional "
        "handoff quality (NOT CSR authoring)."
    )

    top_n = st.slider("Evidence pack size", 5, 25, 12, 1)

    ev = EvidenceReadinessAgent()
    pack = ev.build_evidence_pack(df, notes, top_n=top_n)

    st.markdown("### Evidence pack (traceable)")
    st.dataframe(
        pack[["exp_id", "stability_days", "irritation_risk", "qc_fail", "observation", "trace"]],
        use_container_width=True,
    )

    md2 = render_evidence_pack_md(pack)

    st.markdown("### Evidence pack narrative (traceable)")
    st.code(md2, language="markdown")

    st.download_button(
        "Download evidence pack (CSV)",
        pack.to_csv(index=False).encode("utf-8"),
        file_name="evidence_pack.csv",
    )
    st.download_button(
        "Download evidence pack narrative (MD)",
        md2.encode("utf-8"),
        file_name="evidence_pack.md",
    )


# -----------------------------------------------------------------------------
# Tab 4 — Workstream C
# -----------------------------------------------------------------------------
with tabs[4]:
    st.subheader("Workstream C — Orchestration Layer (Shadow Mode)")
    st.write("Shows how policy shifts change ranking. No execution authority; decision-support only.")
    st.info("This view is intentionally limited to highlight trade-off governance and coordination.")

    agent = FormulationIntelligenceAgent()
    proposals = agent.propose_next_experiments(n=12)

    colA, colB = st.columns(2)

    with colA:
        pol1 = st.selectbox("Policy A", ["balanced", "speed_to_clinic", "low_risk"], index=0)

    with colB:
        pol2 = st.selectbox("Policy B", ["balanced", "speed_to_clinic", "low_risk"], index=2)

    r1 = orchestrate(proposals, policy=pol1).head(8)
    r2 = orchestrate(proposals, policy=pol2).head(8)

    left, right = st.columns(2)

    with left:
        st.markdown(f"### Top recommendations — {pol1}")
        st.dataframe(
            r1[
                [
                    "proposal_id",
                    "pred_permeability",
                    "pred_irritation",
                    "pred_stability",
                    "pred_qc_fail_prob",
                    "policy_score",
                ]
            ],
            use_container_width=True,
        )

    with right:
        st.markdown(f"### Top recommendations — {pol2}")
        st.dataframe(
            r2[
                [
                    "proposal_id",
                    "pred_permeability",
                    "pred_irritation",
                    "pred_stability",
                    "pred_qc_fail_prob",
                    "policy_score",
                ]
            ],
            use_container_width=True,
        )
