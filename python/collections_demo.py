import streamlit as st
import pandas as pd
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report

st.set_page_config(page_title="Data Quality Dashboard", layout="wide")

st.title("📊 Debt Collection Data Quality & Profiling")

st.write("""
Upload a dataset submitted by a finance organization to profile its structure, check for missing values, outliers, data types, and other potential issues before submission.
""")

# File upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Raw Data Preview")
    st.dataframe(df.head())

    st.subheader("📈 Data Profiling Report")
    profile = ProfileReport(df, title="Debt Collection Data Quality Report", explorative=True)
    st_profile_report(profile)
else:
    st.info("⬆️ Upload a .csv file to begin.")
