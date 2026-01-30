import streamlit as st
import requests
import pandas as pd

API_URL = "https://mutual-fund-screener-2.onrender.com"

st.set_page_config(page_title="MF Screener", layout="wide")
st.title("📊 Mutual Fund Screener (mftool based)")

# -------------------------------
# AMC Selection
# -------------------------------

amcs = requests.get(f"{API_URL}/amcs").json()
amc = st.selectbox("Select AMC", amcs)

# -------------------------------
# Screener Filters
# -------------------------------

col1, col2 = st.columns(2)
min_roi = col1.slider("Minimum ROI (%)", 0, 50, 10)
years = col2.selectbox("ROI Period (Years)", [1, 3, 5])

# -------------------------------
# Run Screener
# -------------------------------

if st.button("Run Screener"):
    params = {
        "amc": amc,
        "min_roi": min_roi,
        "years": years
    }
    data = requests.get(f"{API_URL}/screener", params=params).json()

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No schemes matched your criteria.")

# -------------------------------
# Scheme ROI Lookup
# -------------------------------

st.divider()
st.subheader("🔍 Individual Scheme ROI")

scheme_code = st.text_input("Enter Scheme Code")
if scheme_code:
    roi = requests.get(
        f"{API_URL}/scheme/roi/{scheme_code}",
        params={"years": 3}
    ).json()

    st.metric("3Y ROI (%)", roi["roi"])

