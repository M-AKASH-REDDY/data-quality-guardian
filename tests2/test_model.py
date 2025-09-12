from dqg.model import fit_detect_anomalies
import pandas as pd

def test_fit_detect():
    df = pd.DataFrame({
        "x":[1,2,3,4,5,100],  # 100 is an outlier
        "y":[10,11,9,10,12,10]
    })
    out = fit_detect_anomalies(df, contamination=0.16)
    assert "scores" in out
    flagged = out["flagged"]
    assert not flagged.empty