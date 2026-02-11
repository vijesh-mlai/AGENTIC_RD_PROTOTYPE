import pandas as pd

def orchestrate(proposals: pd.DataFrame, policy="balanced") -> pd.DataFrame:
    df = proposals.copy()
    if policy == "speed_to_clinic":
        w_perm, w_stab, w_irr, w_fail = 0.60, 0.20, 0.10, 0.25
    elif policy == "low_risk":
        w_perm, w_stab, w_irr, w_fail = 0.30, 0.55, 0.15, 0.30
    else:
        w_perm, w_stab, w_irr, w_fail = 0.45, 0.35, 0.15, 0.20

    df["policy_score"] = (
        w_perm*(df["pred_permeability"]/100) +
        w_stab*(df["pred_stability"]/365) -
        w_irr*(df["pred_irritation"]) -
        w_fail*(df["pred_qc_fail_prob"])
    )
    return df.sort_values("policy_score", ascending=False).reset_index(drop=True)
