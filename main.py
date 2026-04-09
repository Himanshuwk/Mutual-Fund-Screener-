from fastapi import FastAPI
import pandas as pd

app = FastAPI()

# Load CSV once
df = pd.read_csv("data/final_fund_data.csv")


@app.get("/")
def health():
    return {"status": "alive"}


@app.get("/fundhouses")
def fundhouses():
    return sorted(df["fund_house"].dropna().unique().tolist())


@app.get("/screener")
def screener(fund_house: str = None):

    data = df.copy()

    if fund_house:
        data = data[data["fund_house"] == fund_house]

    result = data[
        [
            "scheme_code",
            "scheme_name",
            "category",
            "return_3m_pct",
            "cagr_5y_pct",
            "sharpe_ratio",
            "fund_house"
        ]
    ].dropna()

    return result.to_dict(orient="records")
