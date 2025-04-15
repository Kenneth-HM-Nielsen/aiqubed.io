import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
import streamlit.components.v1 as components
import tempfile

st.set_page_config(page_title="Data Quality Dashboard", layout="wide")

st.title("📊 Debt Collection Data Quality & Profiling")

st.write("""
Upload a dataset submitted by a finance organization to profile its structure, check for missing values, outliers, data types, and other potential issues before submission.
""")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Raw Data Preview")
    st.dataframe(df.head())

    st.subheader("📈 Data Profiling Report")

    # Create profile and save it to a temp file
    profile = ProfileReport(df, title="Debt Collection Data Quality Report", explorative=True)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp_file:
        profile.to_file(tmp_file.name)
        with open(tmp_file.name, "r", encoding="utf-8") as f:
            report_html = f.read()
        components.html(report_html, height=1000, scrolling=True)

else:
    st.info("⬆️ Upload a .csv file to begin.")
