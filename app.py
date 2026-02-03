import streamlit as st
import requests
import pandas as pd

API_URL = "https://YOUR-RENDER-URL.onrender.com"

st.set_page_config(layout="wide")
st.title("📊 Mutual Fund Screener")

# --------------------
# AMC Selection
# --------------------
amcs = ["-- Select AMC --"] + requests.get(f"{API_URL}/amcs").json()
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
    resp = requests.get(
        f"{API_URL}/screener",
        params={"amc": amc, "period": period}
    )

    data = resp.json()

    if not data:
        st.warning("No schemes matched criteria")
    else:
        df = pd.DataFrame(data).sort_values("return_percent", ascending=False)
        st.dataframe(df, use_container_width=True)
