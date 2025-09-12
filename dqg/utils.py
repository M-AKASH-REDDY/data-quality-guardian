from typing import Dict, Any
import pandas as pd

def df_info(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "rows": int(df.shape[0]),
        "cols": int(df.shape[1]),
        "columns": list(df.columns),
        "dtypes": {c: str(dt) for c, dt in df.dtypes.items()},
    }