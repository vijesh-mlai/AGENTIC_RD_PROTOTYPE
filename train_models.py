import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, roc_auc_score

FEATURES = ["api_load","solvent_ratio","polymer_pct","surfactant_pct","ph","viscosity","process_temp","mix_time"]

def train_all(data_path="synthetic_formulations.csv", out_dir="."):
    df = pd.read_csv(data_path)
    X = df[FEATURES]

    for target, fname in [
        ("permeability_score","model_perm.joblib"),
        ("irritation_risk","model_irr.joblib"),
        ("stability_days","model_stab.joblib"),
    ]:
        y = df[target]
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=7)
        m = RandomForestRegressor(n_estimators=250, random_state=7)
        m.fit(Xtr, ytr)
        mae = mean_absolute_error(yte, m.predict(Xte))
        joblib.dump(m, f"{out_dir}/{fname}")
        print(f"{target} MAE: {mae:.3f}")

    y = df["qc_fail"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=7)
    clf = RandomForestClassifier(n_estimators=350, random_state=7)
    clf.fit(Xtr, ytr)
    auc = roc_auc_score(yte, clf.predict_proba(Xte)[:,1])
    joblib.dump(clf, f"{out_dir}/model_fail.joblib")
    print(f"qc_fail AUC: {auc:.3f}")
