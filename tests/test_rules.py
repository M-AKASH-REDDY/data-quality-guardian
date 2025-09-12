from dqg.rules import suggest_rules
from dqg.profiling import profile_dataframe
import pandas as pd

def test_suggest_rules_basic():
    df = pd.DataFrame({
        "CustomerID":[1,2,2],
        "Email":["a@x.com",None,"b@x.com"],
        "Age":[10,20,30],
        "Country":["USA","USA","India"]
    })
    prof = profile_dataframe(df)
    rules = suggest_rules(prof)
    # expect some basic suggestions to be present
    assert any(r.get("rule")=="not_null" and r.get("column")=="Email" for r in rules)
    assert any(r.get("rule")=="dedupe_key" and r.get("column")=="CustomerID" for r in rules)