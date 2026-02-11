import streamlit as st
import pandas as pd
import os

from data_gen import generate_synthetic_formulation_data, generate_synthetic_dev_notes
from agents import FormulationIntelligenceAgent, EvidenceReadinessAgent
from orchestrator import orchestrate
from authoring import render_formulation_recs_md, render_evidence_pack_md

st.set_page_config(page_title="Agentic R&D Topical Demo", layout="wide")
st.title("Agentic AI Validation Demo — Topical Product R&D (Synthetic Data)")
st.caption("Three-workstream prototype: (A) Formulation Intelligence, (B) Development Readiness, (C) Orchestration (shadow mode).")

DATA_FORM = "synthetic_formulations.csv"
DATA_NOTES = "synthetic_dev_notes.csv"

@st.cache_data
def load_or_make_data():
    # if os.path.exists(DATA_FORM) and os.path.exists(DATA_NOTES):
        # return pd.read_csv(DATA_FORM), pd.read_csv(DATA_NOTES)
    df = generate_synthetic_formulation_data(n=1200, seed=7)
    notes = generate_synthetic_dev_notes(df, n_notes=200, seed=11)
    # df.to_csv(DATA_FORM, index=False)
    # notes.to_csv(DATA_NOTES, index=False)
    return df, notes

df, notes = load_or_make_data()

tabs = st.tabs(["Workstream A: Formulation Intelligence","Workstream B: Development Readiness","Workstream C: Orchestration (Shadow)"])

with tabs[0]:
    st.subheader("Workstream A — Formulation Intelligence & Trade-off Agent (R&D-owned)")
    st.write("Generate next-best experiment proposals with constraints. Outputs are decision-support only.")
    col1, col2, col3 = st.columns(3)
    with col1:
        max_irr = st.slider("Max irritation (constraint)", 0.10, 0.90, 0.65, 0.01)
    with col2:
        min_stab = st.slider("Min stability days (constraint)", 15, 365, 120, 5)
    with col3:
        max_fail = st.slider("Max QC fail probability (constraint)", 0.05, 0.90, 0.40, 0.01)
    policy = st.selectbox("Decision policy (for ranking)", ["balanced","speed_to_clinic","low_risk"])

    agent = FormulationIntelligenceAgent()
    proposals = agent.propose_next_experiments(
        n=12,
        constraints={"max_irritation": max_irr, "min_stability": min_stab, "max_fail_prob": max_fail}
    )
    ranked = orchestrate(proposals, policy=policy)

    st.markdown("### Ranked recommendations")
    st.dataframe(ranked[["proposal_id","pred_permeability","pred_irritation","pred_stability","pred_qc_fail_prob","policy_score"]], use_container_width=True)

    st.markdown("### Traceable recommendation summary (internal decision-support)")
    md = render_formulation_recs_md(ranked, policy=policy, top_k=5)
    st.code(md, language="markdown")

    st.download_button("Download ranked recommendations (CSV)", ranked.to_csv(index=False).encode("utf-8"), file_name=f"ranked_{policy}.csv")
    st.download_button("Download recommendation summary (MD)", md.encode("utf-8"), file_name=f"summary_{policy}.md")

with tabs[1]:
    st.subheader("Workstream B — Development Readiness & Evidence Intelligence (R&D-adjacent)")
    st.write("Creates traceable evidence packs to improve readiness and cross-functional handoff quality (NOT CSR authoring).")
    top_n = st.slider("Evidence pack size", 5, 25, 12, 1)

    ev = EvidenceReadinessAgent()
    pack = ev.build_evidence_pack(df, notes, top_n=top_n)
    st.markdown("### Evidence pack (traceable)")
    st.dataframe(pack[["exp_id","stability_days","irritation_risk","qc_fail","observation","trace"]], use_container_width=True)

    md2 = render_evidence_pack_md(pack)
    st.markdown("### Evidence pack narrative (traceable)")
    st.code(md2, language="markdown")

    st.download_button("Download evidence pack (CSV)", pack.to_csv(index=False).encode("utf-8"), file_name="evidence_pack.csv")
    st.download_button("Download evidence pack narrative (MD)", md2.encode("utf-8"), file_name="evidence_pack.md")

with tabs[2]:
    st.subheader("Workstream C — Orchestration Layer (Shadow Mode)")
    st.write("Shows how policy shifts change ranking. No execution authority; decision-support only.")
    st.info("This view is intentionally limited to highlight trade-off governance and coordination.")
    agent = FormulationIntelligenceAgent()
    proposals = agent.propose_next_experiments(n=12)

    colA, colB = st.columns(2)
    with colA:
        pol1 = st.selectbox("Policy A", ["balanced","speed_to_clinic","low_risk"], index=0)
    with colB:
        pol2 = st.selectbox("Policy B", ["balanced","speed_to_clinic","low_risk"], index=2)

    r1 = orchestrate(proposals, policy=pol1).head(8)
    r2 = orchestrate(proposals, policy=pol2).head(8)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### Top recommendations — {pol1}")
        st.dataframe(r1[["proposal_id","pred_permeability","pred_irritation","pred_stability","pred_qc_fail_prob","policy_score"]], use_container_width=True)
    with c2:
        st.markdown(f"### Top recommendations — {pol2}")
        st.dataframe(r2[["proposal_id","pred_permeability","pred_irritation","pred_stability","pred_qc_fail_prob","policy_score"]], use_container_width=True)
