from typing import Dict, Any, List, Tuple
import pandas as pd

# A simple, JSON-serializable rule format.
# Example:
# {"column":"Email","rule":"not_null"}
# {"column":"Age","rule":"between","min":0,"max":120}
# {"column":"Country","rule":"allowed_values","values":["USA","India"]}
# {"column":"CustomerID","rule":"dedupe_key"}

def suggest_rules(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    rules: List[Dict[str, Any]] = []
    cols = profile.get("columns", {})
    # heuristic: id/email-like columns should be not null
    for col, meta in cols.items():
        name_l = col.lower()
        col_type = meta.get("type")
        missing_pct = meta.get("missing_pct", 0.0)

        if any(k in name_l for k in ["id","email"]):
            rules.append({"column": col, "rule": "not_null"})

        # numeric ranges
        if col_type in ("int","float"):
            vmin, vmax = meta.get("min"), meta.get("max")
            if vmin is not None and vmax is not None:
                # add a small safety margin
                r = {"column": col, "rule": "between", "min": vmin, "max": vmax}
                rules.append(r)

        # categorical allowed values (low-cardinality strings)
        if col_type == "string":
            top = meta.get("top_values", {})
            if 0 < len(top) <= 10:
                values = list(top.keys())
                rules.append({"column": col, "rule": "allowed_values", "values": values})

        # dedupe suggestion if a column looks like a key
        if any(k in name_l for k in ["id"]):
            rules.append({"column": col, "rule": "dedupe_key"})

        # if missingness is high, suggest filling
        if missing_pct > 5.0:
            if col_type in ("int","float"):
                rules.append({"column": col, "rule": "fillna_mean"})
            else:
                rules.append({"column": col, "rule": "fillna_mode"})
    return rules

def apply_rules_preview(df: pd.DataFrame, rules: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, List[str]]:
    """Apply rules non-destructively to preview fixes. Returns (fixed_df, notes)."""
    fixed = df.copy()
    notes: List[str] = []
    for r in rules:
        col = r.get("column")
        kind = r.get("rule")
        if col not in fixed.columns:
            notes.append(f"Column '{col}' not in dataframe; skipping {kind}.")
            continue
        if kind == "fillna_mean" and fixed[col].dtype.kind in "if":
            mean_val = fixed[col].mean()
            fixed[col] = fixed[col].fillna(mean_val)
            notes.append(f"Filled NaNs in {col} with mean {mean_val:.3f}.")
        elif kind == "fillna_mode":
            mode_val = fixed[col].mode(dropna=True)
            fill = mode_val.iloc[0] if not mode_val.empty else ""
            fixed[col] = fixed[col].fillna(fill)
            notes.append(f"Filled NaNs in {col} with mode '{fill}'.")
        elif kind == "dedupe_key":
            before = len(fixed)
            fixed = fixed.drop_duplicates(subset=[col])
            after = len(fixed)
            notes.append(f"Dropped {before-after} duplicate rows based on key {col}.")
        # preview only; we don't enforce 'between'/'allowed_values' here
    return fixed, notes