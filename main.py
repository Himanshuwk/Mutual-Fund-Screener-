from fastapi import FastAPI
import sqlite3
import pandas as pd

app = FastAPI(title="MF Screener API")

DB_PATH = "db/nav_data.db"

# --------------------
# Utility
# --------------------
def get_df(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

# --------------------
# Health
# --------------------
@app.get("/")
def health():
    return {"status": "alive"}

# --------------------
# AMC List
# --------------------
@app.get("/amcs")
def get_amcs():
    df = get_df("SELECT DISTINCT amc FROM nav_data")
    return sorted(df["amc"].tolist())

# --------------------
# Schemes by AMC
# --------------------
@app.get("/schemes/{amc}")
def get_schemes(amc: str):
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
