from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def fit_detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> Dict[str, Any]:
    """Detects row-level anomalies using numeric columns via IsolationForest.
    Returns { 'scores': Series, 'flagged': DataFrame } where flagged includes reason columns.
    """
    num_df = df.select_dtypes(include=[np.number]).copy()
    if num_df.empty or len(num_df) < 3:
        return {"scores": pd.Series(dtype=float), "flagged": pd.DataFrame()}

    # Simple imputation for NaNs
    num_df = num_df.fillna(num_df.median(numeric_only=True))

    model = IsolationForest(
        n_estimators=200, contamination=contamination, random_state=42
    )
    model.fit(num_df.values)
    # Higher score = more normal. We'll invert for anomaly score
    raw_scores = model.score_samples(num_df.values)
    # Invert so larger = more anomalous (easier to reason about)
    anomaly_score = -raw_scores

    # Robust selection for small N: pick the top-k most anomalous rows
    n = len(anomaly_score)
    k = max(1, int(np.ceil(float(contamination) * n)))
    order = np.argsort(anomaly_score)           # ascending
    flag_indices = order[-k:]                   # top-k most anomalous
    flags = np.zeros(n, dtype=bool)
    flags[flag_indices] = True


    result = pd.DataFrame({
        "anomaly_score": anomaly_score,
        "is_flagged": flags
    }, index=df.index)

    flagged = df.loc[flags].copy()
    flagged["anomaly_score"] = anomaly_score[flags]

    # Add a naive reason: which numeric columns deviate most from median (z-ish metric)
    med = num_df.median()
    mad = (num_df.subtract(med).abs()).median().replace(0, 1e-9)
    dev = (num_df.subtract(med).abs()).divide(mad)
    top_reason = dev.idxmax(axis=1)
    result["top_deviation_col"] = top_reason
    flagged["top_deviation_col"] = top_reason[flags]

    return {"scores": result, "flagged": flagged}