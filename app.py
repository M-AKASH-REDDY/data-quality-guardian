import streamlit as st
import pandas as pd
import io, json, os
from dqg import (
    profile_dataframe,
    suggest_rules,
    apply_rules_preview,
    fit_detect_anomalies,
    generate_sql_cleaning_script,
    export_great_expectations,
    export_markdown_report,
    df_info,
)

st.set_page_config(page_title="Data Quality Guardian", page_icon="🛡️", layout="wide")
st.title("🛡️ Data Quality Guardian")
st.caption("Upload → Profile → Suggest Rules → Detect Anomalies → Export Fixes")

with st.expander("About", expanded=False):
    st.markdown("""
**What:** A beginner-friendly data quality assistant for Data Engineers.  
**How:** Upload a CSV/XLSX, get a profile, suggested rules, anomaly detection, and exports (GE, SQL, report).
    """)

uploaded = st.file_uploader("Upload a CSV or XLSX", type=["csv","xlsx"])

if uploaded is not None:
    try:
        if uploaded.name.lower().endswith(".xlsx"):
            df = pd.read_excel(uploaded)
        else:
            df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Failed to read file: {e}")
        st.stop()

    st.subheader("Preview")
    st.dataframe(df.head(20))

    # Basic info
    info = df_info(df)
    st.write(f"**Rows:** {info['rows']} | **Columns:** {info['cols']}")

    # Profile
    st.subheader("Profile")
    profile = profile_dataframe(df)
    st.json(profile)

    # Suggested rules with toggles
    st.subheader("Suggested Rules")
    suggested = suggest_rules(profile)
    accepted = []
    for i, r in enumerate(suggested):
        with st.container(border=True):
            col1, col2 = st.columns([4,1])
            with col1:
                st.write(r)
            with col2:
                if st.checkbox("Accept", key=f"rule_{i}"):
                    accepted.append(r)
    st.success(f"Accepted {len(accepted)} rules.") if accepted else st.info("No rules accepted yet.")

    # Preview fixes
    if accepted:
        st.subheader("Preview Fixes (non-destructive)")
        fixed, notes = apply_rules_preview(df, accepted)
        st.dataframe(fixed.head(20))
        if notes:
            st.write("**Notes:**")
            for n in notes:
                st.write("-", n)

    # Anomaly detection
    st.subheader("Anomaly Detection")
    contam = st.slider("Contamination (expected anomaly rate)", 0.01, 0.20, 0.05, 0.01)
    anomalies = fit_detect_anomalies(df, contamination=contam)
    scores = anomalies.get("scores")
    flagged = anomalies.get("flagged")
    if scores is not None and not scores.empty:
        st.write("Scores (sample):")
        st.dataframe(scores.head(20))
    if flagged is not None and not flagged.empty:
        st.warning(f"Flagged {len(flagged)} suspected anomalous rows.")
        st.dataframe(flagged.head(20))
    else:
        st.info("No anomalies flagged with current settings.")

    # Exports
    st.subheader("Exports")
    if st.button("Export Great Expectations Suite"):
        path = export_great_expectations(profile, accepted, out_dir="exports")
        with open(path, "rb") as f:
            st.download_button("Download GE Suite JSON", data=f, file_name="ge_suite.json", mime="application/json")
    if st.button("Export SQL Cleaning Script"):
        table_name = st.text_input("Source table name (for SQL CTEs)", value="my_table")
        if table_name:
            sql_script = generate_sql_cleaning_script(table_name, accepted)
            st.code(sql_script, language="sql")
            st.download_button("Download SQL", data=sql_script, file_name="cleaning.sql", mime="text/sql")
    if st.button("Export Markdown Report"):
        path = export_markdown_report(profile, accepted, anomalies, out_dir="exports")
        with open(path, "rb") as f:
            st.download_button("Download Report (.md)", data=f, file_name="report.md", mime="text/markdown")
else:
    st.info("Upload a dataset to begin. Or try the example in `examples/customers_dirty.csv`.")