from typing import Dict, Any, List
import pandas as pd
import numpy as np

def _infer_type(series: pd.Series) -> str:
    if pd.api.types.is_integer_dtype(series):
        return "int"
    if pd.api.types.is_float_dtype(series):
        return "float"
    if pd.api.types.is_bool_dtype(series):
        return "bool"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    return "string"

def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    profile: Dict[str, Any] = {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns": {}
    }
    n_dup = int(df.duplicated().sum())
    profile["n_duplicates"] = n_dup
    profile["n_duplicates_pct"] = float((n_dup / len(df)) * 100) if len(df) else 0.0

    for col in df.columns:
        s = df[col]
        col_type = _infer_type(s)
        missing = int(s.isna().sum())
        missing_pct = float((missing / len(s)) * 100) if len(s) else 0.0
        unique = int(s.nunique(dropna=True))
        col_profile = {
            "type": col_type,
            "missing": missing,
            "missing_pct": missing_pct,
            "unique": unique
        }
        if col_type in ("int","float"):
            col_profile["min"] = float(np.nanmin(s.values)) if s.notna().any() else None
            col_profile["max"] = float(np.nanmax(s.values)) if s.notna().any() else None
            col_profile["mean"] = float(np.nanmean(s.values)) if s.notna().any() else None
            col_profile["std"]  = float(np.nanstd(s.values))  if s.notna().any() else None
        else:
            vc = s.value_counts(dropna=True).head(5)
            col_profile["top_values"] = vc.to_dict()
        profile["columns"][col] = col_profile
    return profile

def compute_health(profile: dict, anomaly_rate: float = 0.0) -> dict:
    cols = profile.get("columns", {})
    ncols = max(1, len(cols))
    avg_missing = sum(meta.get("missing_pct", 0.0) for meta in cols.values()) / ncols
    dup_pct = profile.get("n_duplicates_pct", 0.0)
    score = 100 - (0.5 * avg_missing) - (0.8 * dup_pct) - (0.7 * (anomaly_rate * 100))
    score = max(0.0, min(100.0, score))
    return {
        "score": round(score, 1),
        "avg_missing_pct": round(avg_missing, 1),
        "dup_pct": round(dup_pct, 1),
        "anomaly_rate_pct": round(anomaly_rate * 100.0, 1),
    }