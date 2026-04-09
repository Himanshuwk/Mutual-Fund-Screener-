import streamlit as st
import requests
import pandas as pd

API_URL = "https://mutual-fund-screener-1.onrender.com"

st.title("📊 Mutual Fund Screener")


# --------------------
# Safe API call
# --------------------
def safe_get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except:
        return None


# --------------------
# Fund house dropdown
# --------------------
fundhouses = safe_get(f"{API_URL}/fundhouses")

if fundhouses is None:
    st.warning("Backend waking up... refresh in few seconds")
    st.stop()

fundhouses = ["All"] + fundhouses

selected = st.selectbox("Select Fund House", fundhouses)


# --------------------
# Run Screener
# --------------------
if st.button("Run Screener"):

    params = {}

    if selected != "All":
        params["fund_house"] = selected

    data = safe_get(f"{API_URL}/screener", params)

    if not data:
        st.warning("No data available")
    else:
        df = pd.DataFrame(data)
        df = df.sort_values("cagr_5y_pct", ascending=False)
        st.dataframe(df, use_container_width=True)
