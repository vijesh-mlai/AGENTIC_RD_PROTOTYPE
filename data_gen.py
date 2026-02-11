import numpy as np
import pandas as pd

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def generate_synthetic_formulation_data(n=1200, seed=7):
    rng = np.random.default_rng(seed)

    api_load = rng.uniform(0.1, 5.0, n)
    solvent_ratio = rng.uniform(0.0, 1.0, n)
    polymer_pct = rng.uniform(0.0, 8.0, n)
    surfactant_pct = rng.uniform(0.0, 3.0, n)
    ph = rng.uniform(4.0, 8.0, n)
    viscosity = rng.lognormal(mean=2.7, sigma=0.4, size=n)
    process_temp = rng.uniform(18, 45, n)
    mix_time = rng.uniform(2, 45, n)

    perm_latent = (
        1.2 * solvent_ratio +
        0.7 * (surfactant_pct / 3.0) -
        0.6 * np.clip((np.log(viscosity) - 2.8), 0, None) +
        0.2 * (api_load / 5.0) -
        0.15 * np.abs(ph - 6.0)
    )
    permeability_score = 100 * sigmoid(perm_latent + rng.normal(0, 0.15, n))

    irr_latent = (
        1.0 * (surfactant_pct / 3.0) +
        0.5 * (api_load / 5.0) +
        0.35 * np.abs(ph - 6.0) +
        0.1 * (process_temp - 25) / 20
    )
    irritation_risk = np.clip(sigmoid(irr_latent + rng.normal(0, 0.2, n)), 0, 1)

    stab_latent = (
        1.4
        - 0.7 * solvent_ratio
        - 0.25 * np.abs(ph - 6.2)
        - 0.35 * np.abs(process_temp - 27) / 18
        - 0.15 * (api_load / 5.0)
        + 0.10 * (polymer_pct / 8.0)
    )
    stability_days = np.clip(365 * sigmoid(stab_latent + rng.normal(0, 0.18, n)), 15, 365)

    qc_fail_prob = np.clip(0.15 * irritation_risk + 0.25 * (1 - stability_days / 365), 0, 0.9)
    qc_fail = (rng.uniform(0, 1, n) < qc_fail_prob).astype(int)

    df = pd.DataFrame({
        "exp_id": [f"EXP-{i:05d}" for i in range(n)],
        "api_load": api_load,
        "solvent_ratio": solvent_ratio,
        "polymer_pct": polymer_pct,
        "surfactant_pct": surfactant_pct,
        "ph": ph,
        "viscosity": viscosity,
        "process_temp": process_temp,
        "mix_time": mix_time,
        "permeability_score": permeability_score,
        "irritation_risk": irritation_risk,
        "stability_days": stability_days,
        "qc_fail": qc_fail,
    })
    return df

def generate_synthetic_dev_notes(formulations_df, n_notes=180, seed=11):
    rng = np.random.default_rng(seed)
    sample = formulations_df.sample(min(len(formulations_df), n_notes), random_state=seed).copy()
    rows = []
    for _, r in sample.iterrows():
        obs = []
        if r["stability_days"] < 120:
            obs.append("Stability concern: accelerated degradation observed.")
        if r["irritation_risk"] > 0.65:
            obs.append("Tolerability concern: irritation proxy elevated.")
        if r["permeability_score"] > 70:
            obs.append("Permeability signal strong; favorable delivery profile.")
        if r["qc_fail"] == 1:
            obs.append("QC observation: out-of-spec event recorded in run.")
        if not obs:
            obs.append("Development observation: within expected bounds.")
        rows.append({
            "note_id": f"NOTE-{rng.integers(100000,999999)}",
            "exp_id": r["exp_id"],
            "observation": " ".join(obs),
            "review_status": rng.choice(["draft","reviewed","approved"], p=[0.35,0.45,0.20]),
        })
    return pd.DataFrame(rows)
