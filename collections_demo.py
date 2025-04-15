import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
import tempfile
import os

st.set_page_config(page_title="Data Quality Dashboard", layout="wide")

st.title("📊 Debt Collection Data Quality & Profiling")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Raw Data Preview")
    st.dataframe(df.head())

    st.subheader("📈 Data Profiling Report")

    profile = ProfileReport(df, title="Debt Collection Data Quality Report", explorative=True)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
        profile_path = tmp_file.name
        profile.to_file(profile_path)

    with open(profile_path, "rb") as f:
        st.download_button(
            label="📥 Download Full Profiling Report",
            data=f,
            file_name="data_quality_report.html",
            mime="text/html"
        )

    st.success("✅ Report generated! Download above to view full profiling.")
else:
    st.info("⬆️ Upload a .csv file to begin.")
