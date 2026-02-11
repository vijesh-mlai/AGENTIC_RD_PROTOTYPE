from pathlib import Path
import numpy as np
import joblib
import pandas as pd


FEATURES = ["api_load","solvent_ratio","polymer_pct","surfactant_pct","ph","viscosity","process_temp","mix_time"]

class FormulationIntelligenceAgent:
    def __init__(self, model_dir=None):
        if model_dir is None:
            model_dir = Path(__file__).resolve().parent /
        else:
            model_dir = Path(model_dir)
        self.m_perm = joblib.load(f"{model_dir}/model_perm.joblib")
        self.m_irr  = joblib.load(f"{model_dir}/model_irr.joblib")
        self.m_stab = joblib.load(f"{model_dir}/model_stab.joblib")
        self.m_fail = joblib.load(f"{model_dir}/model_fail.joblib")

    def score(self, X: pd.DataFrame) -> pd.DataFrame:
        Xf = X[FEATURES]
        out = X.copy()
        out["pred_permeability"] = self.m_perm.predict(Xf)
        out["pred_irritation"]   = np.clip(self.m_irr.predict(Xf), 0, 1)
        out["pred_stability"]    = np.clip(self.m_stab.predict(Xf), 15, 365)
        out["pred_qc_fail_prob"] = self.m_fail.predict_proba(Xf)[:,1]
        return out

    def propose_next_experiments(self, n=10, seed=7, constraints=None):
        rng = np.random.default_rng(seed)
        candidates = pd.DataFrame({
            "api_load": rng.uniform(0.1, 5.0, 600),
            "solvent_ratio": rng.uniform(0.0, 1.0, 600),
            "polymer_pct": rng.uniform(0.0, 8.0, 600),
            "surfactant_pct": rng.uniform(0.0, 3.0, 600),
            "ph": rng.uniform(4.0, 8.0, 600),
            "viscosity": rng.lognormal(mean=2.7, sigma=0.45, size=600),
            "process_temp": rng.uniform(18, 45, 600),
            "mix_time": rng.uniform(2, 45, 600),
        })
        scored = self.score(candidates)

        if constraints:
            if "max_irritation" in constraints:
                scored = scored[scored["pred_irritation"] <= constraints["max_irritation"]]
            if "min_stability" in constraints:
                scored = scored[scored["pred_stability"] >= constraints["min_stability"]]
            if "max_fail_prob" in constraints:
                scored = scored[scored["pred_qc_fail_prob"] <= constraints["max_fail_prob"]]

        scored["utility"] = (
            0.45*(scored["pred_permeability"]/100) +
            0.35*(scored["pred_stability"]/365) -
            0.15*(scored["pred_irritation"]) -
            0.20*(scored["pred_qc_fail_prob"])
        )
        top = scored.sort_values("utility", ascending=False).head(n).reset_index(drop=True)
        top["proposal_id"] = [f"PROP-{i:03d}" for i in range(1, len(top)+1)]
        return top

class EvidenceReadinessAgent:
    def build_evidence_pack(self, formulations_df, dev_notes_df, top_n=12):
        notes = dev_notes_df.groupby("exp_id")["observation"].apply(lambda x: " ".join(list(x))).reset_index()
        merged = formulations_df.merge(notes, on="exp_id", how="left")
        merged["observation"] = merged["observation"].fillna("No notes.")
        merged["priority"] = (
            0.35*(merged["irritation_risk"]) +
            0.35*(1 - merged["stability_days"]/365) +
            0.30*(merged["qc_fail"])
        )
        pack = merged.sort_values("priority", ascending=False).head(top_n).reset_index(drop=True)
        pack["trace"] = pack["exp_id"].apply(lambda x: f"Data row exp_id={x}")
        return pack
