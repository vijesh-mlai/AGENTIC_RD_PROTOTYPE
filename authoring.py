from datetime import date

def render_evidence_pack_md(evidence_pack_df, title="Development Readiness Evidence Pack"):
    lines = []
    lines.append(f"# {title}")
    lines.append(f"Date: {date.today().isoformat()}\n")
    lines.append("## Summary")
    lines.append("This pack summarizes high-priority development signals and links each statement to an underlying experiment record.\n")
    for i, r in evidence_pack_df.iterrows():
        lines.append(f"### {i+1}. {r['exp_id']}")
        lines.append(f"- Stability days: **{r['stability_days']:.0f}**")
        lines.append(f"- Irritation risk: **{r['irritation_risk']:.2f}**")
        lines.append(f"- QC fail: **{int(r['qc_fail'])}**")
        lines.append(f"- Observation: {r['observation']}")
        lines.append(f"- Trace: `{r['trace']}`\n")
    lines.append("## Governance Notes")
    lines.append("- Decision-support output only; scientific judgment remains with the R&D team.")
    lines.append("- No regulatory submission artifacts are generated; this supports readiness and cross-functional handoff quality.")
    return "\n".join(lines)

def render_formulation_recs_md(ranked_df, policy="balanced", top_k=5):
    top = ranked_df.head(top_k)
    lines = []
    lines.append(f"# Formulation Recommendations ({policy})")
    lines.append(f"Date: {date.today().isoformat()}\n")
    lines.append("## Recommended next experiments (decision-support)")
    for _, r in top.iterrows():
        pid = r.get("proposal_id","(no_id)")
        lines.append(f"### {pid}")
        lines.append(f"- Pred permeability: **{r['pred_permeability']:.1f}** (0–100)")
        lines.append(f"- Pred irritation: **{r['pred_irritation']:.2f}** (0–1)")
        lines.append(f"- Pred stability: **{r['pred_stability']:.0f} days**")
        lines.append(f"- Pred QC fail prob: **{r['pred_qc_fail_prob']:.2f}**")
        lines.append(f"- Trace: derived from row `{pid}` in proposal set\n")
    lines.append("## Governance Notes")
    lines.append("- Advisory only; final selection remains with the R&D team.")
    lines.append("- During POC, validate outputs against wet-lab results in shadow-mode.")
    return "\n".join(lines)
