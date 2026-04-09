from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Load static CSV once
df = pd.read_csv("data/final_fund_data.csv")

# --------------------
# Health check
# --------------------
@app.get("/")
def health():
    return {"status": "alive"}


# --------------------
# Fund house list
# --------------------
@app.get("/fundhouses")
def fundhouses():
    return sorted(df["fund_house"].dropna().unique().tolist())


# --------------------
# Screener
# --------------------
@app.get("/screener")
def screener(fund_house: str = None):

    data = df.copy()

    if fund_house:
        data = data[data["fund_house"] == fund_house]

    result = data[[
        "scheme_code",
        "scheme_name",
        "category",
        "return_3m_pct",
        "cagr_5y_pct",
        "sharpe_ratio",
        "fund_house"
    ]].dropna()

    return result.to_dict(orient="records")def get_schemes(amc: str):
    df = get_df(
        "SELECT DISTINCT scheme_code, scheme_name FROM nav_data WHERE amc = ?",
        (amc,)
    )
    return dict(zip(df["scheme_code"], df["scheme_name"]))

# --------------------
# Return Calculation
# --------------------
def calculate_return(scheme_code: int, days: int):
    df = get_df(
        "SELECT date, nav FROM nav_data WHERE scheme_code = ? ORDER BY date",
        (scheme_code,)
    )

    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])

    latest = df.iloc[-1]
    target_date = latest["date"] - pd.Timedelta(days=days)

    past = df[df["date"] <= target_date]
    if past.empty:
        return None

    start_nav = past.iloc[-1]["nav"]
    end_nav = latest["nav"]

    return round(((end_nav / start_nav) - 1) * 100, 2)

# --------------------
# Screener (1W / 1M)
# --------------------
@app.get("/screener")
def screener(amc: str, period: str = "1W"):
    days_map = {"1W": 7, "1M": 30}
    days = days_map.get(period, 7)

    schemes = get_df(
        "SELECT DISTINCT scheme_code, scheme_name FROM nav_data WHERE amc = ?",
        (amc,)
    )

    result = []

    for _, row in schemes.iterrows():
        ret = calculate_return(row["scheme_code"], days)
        if ret is None:
            continue

        result.append({
            "scheme_code": int(row["scheme_code"]),
            "scheme_name": row["scheme_name"],
            "return_percent": ret
        })

    return result
