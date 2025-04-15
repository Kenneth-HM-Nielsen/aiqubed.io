import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
import streamlit.components.v1 as components
import tempfile

st.set_page_config(page_title="Debt Collections Data Quality Dashboard", layout="wide")

st.title("📊 Data Quality Dashboard")

st.write("""
Upload a CSV file to inspect the data structure, detect issues, and profile its quality before submission.
""")

uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    st.subheader("📈 Data Profiling Report")

    # Generate the profile
    profile = ProfileReport(df, title="Debt Collections Data Profiling Report", explorative=True)

    # Use a temp file to save and render the report
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp_file:
        profile.to_file(tmp_file.name)
        with open(tmp_file.name, "r", encoding='utf-8') as f:
            report_html = f.read()
        components.html(report_html, height=1000, scrolling=True)
else:
    st.info("⬆️ Please upload a CSV file to see the profiling dashboard.")
