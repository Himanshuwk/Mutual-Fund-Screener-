import streamlit as st
import requests
import pandas as pd

# --------------------
# CONFIG
# --------------------
API_URL = "https://mutual-fund-screener-1.onrender.com"

st.set_page_config(layout="wide")
st.title("📊 Mutual Fund Screener")

# --------------------
# SAFE API CALL FUNCTION
# --------------------
def safe_get_json(url, params=None):
    try:
        resp = requests.get(url, params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


# --------------------
# AMC Selection
# --------------------
amc_list = safe_get_json(f"{API_URL}/amcs")

if amc_list is None:
    st.warning("⏳ Backend is waking up... please wait 20–30 seconds and refresh.")
    st.stop()

amcs = ["-- Select AMC --"] + amc_list
amc = st.selectbox("Select AMC", amcs)

if amc == "-- Select AMC --":
    st.stop()


# --------------------
# Period Selection
# --------------------
period = st.selectbox("Return Period", ["1W", "1M"])


# --------------------
# Run Screener
# --------------------
if st.button("Run Screener"):

    data = safe_get_json(
        f"{API_URL}/screener",
        params={"amc": amc, "period": period}
    )

    if data is None:
        st.error("⚠️ Could not fetch data from backend. Try again in a few seconds.")
        st.stop()

    if not data:
        st.warning("No schemes matched criteria.")
    else:
        df = pd.DataFrame(data).sort_values("return_percent", ascending=False)
        st.dataframe(df, use_container_width=True)
