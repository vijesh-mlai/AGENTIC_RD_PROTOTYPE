# Agentic R&D Validation Demo (Topical Product R&D) — Synthetic Data

Working prototype for the **three-workstream** demo:
- **Workstream A (R&D-owned):** Formulation Intelligence & Trade-off Agent
- **Workstream B (R&D-adjacent):** Development Readiness & Evidence Intelligence (**NOT CSR**)
- **Workstream C (Exploratory):** Orchestration Layer (**Shadow Mode**)

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```


## Demo flow (6 minutes)
1. **Management View**: explain the three-workstream structure and success criteria.
2. **Workstream A**: set constraints, generate ranked recommendations, show traceable summary.
3. **Workstream B**: generate evidence pack, show traceable narrative (**not CSR**).
4. **Workstream C**: switch policy A/B and show ranking shifts (shadow mode).
