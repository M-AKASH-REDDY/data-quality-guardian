from typing import List, Dict

def _sql_ident(name: str) -> str:
    # simplistic identifier quoting
    return f'"{name}"'

def generate_sql_cleaning_script(table_name: str, rules: List[Dict[str, any]]) -> str:
    """Generate a standard SQL cleaning script from accepted rules."""
    lines = [f"-- Cleaning script for {table_name}", "WITH src AS (SELECT * FROM " + table_name + ")"]
    # We'll build a staged set of transformations using CTEs
    step = 1
    for r in rules:
        col = r.get("column")
        kind = r.get("rule")
        cte_name = f"step_{step}"
        prev = "src" if step == 1 else f"step_{step-1}"
        if kind == "fillna_mean":
            lines.append(f", {cte_name} AS (SELECT *, COALESCE({_sql_ident(col)}, AVG({_sql_ident(col)}) OVER ()) AS {_sql_ident(col)} FROM {prev})")
            step += 1
        elif kind == "fillna_mode":
            # mode is non-trivial in SQL; we approximate with most frequent using window count
            lines.append(f", freq_{step} AS (SELECT *, COUNT({_sql_ident(col)}) OVER (PARTITION BY {_sql_ident(col)}) AS cnt FROM {prev})")
            lines.append(f", {cte_name} AS (SELECT * REPLACE (COALESCE({_sql_ident(col)}, FIRST_VALUE({_sql_ident(col)}) OVER (ORDER BY cnt DESC)) AS {_sql_ident(col)}) FROM freq_{step})")
            step += 1
        elif kind == "dedupe_key":
            lines.append(f", {cte_name} AS (SELECT * FROM {prev} QUALIFY ROW_NUMBER() OVER (PARTITION BY {_sql_ident(col)} ORDER BY {_sql_ident(col)}) = 1)")
            step += 1
        # between/allowed_values enforcement left to analyst to avoid over-deleting rows
    final_prev = "src" if step == 1 else f"step_{step-1}"
    lines.append(f"SELECT * FROM {final_prev};")
    return "\n".join(lines)