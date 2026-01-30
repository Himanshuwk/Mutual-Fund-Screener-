from fastapi import FastAPI
from mftool import Mftool
import pandas as pd
from datetime import datetime

app = FastAPI(title="MF Screener API")
@app.get("/")
def health():
    return {"status": "alive"}

mf = Mftool()

# -------------------------------
# Utilities
# -------------------------------

def calculate_roi(scheme_code: int, years: int):
    nav_data = mf.get_scheme_historical_nav(scheme_code)
    df = pd.DataFrame(nav_data)

    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df['nav'] = df['nav'].astype(float)
    df = df.sort_values("date")

    end_nav = df.iloc[-1]['nav']
    start_date = df['date'].max() - pd.DateOffset(years=years)
    start_nav = df[df['date'] <= start_date].iloc[-1]['nav']

    return round(((end_nav / start_nav) - 1) * 100, 2)

def risk_mapper(category: str):
    if category is None:
        return "Unknown"
    category = category.lower()
    if "equity" in category:
        return "High"
    elif "hybrid" in category:
        return "Medium"
    else:
        return "Low"

# -------------------------------
# APIs
# -------------------------------

@app.get("/amcs")
def get_amcs():
    try:
        schemes = mf.get_scheme_codes()   # dict: {code: scheme_name}
        amcs = set()

        for name in schemes.values():
            # Extract AMC name heuristically
            # Example: "Axis Bluechip Fund - Direct Plan - Growth"
            amc = name.split(" ")[0] + " Mutual Fund"
            amcs.add(amc)

        return sorted(list(amcs))

    except Exception as e:
        return {"error": str(e)}
@app.get("/schemes/{amc_name}")
def get_schemes(amc_name: str):
    return mf.get_amc_schemes(amc_name)

@app.get("/scheme/details/{scheme_code}")
def scheme_details(scheme_code: int):
    details = mf.get_scheme_details(scheme_code)
    details["risk"] = risk_mapper(details.get("category"))
    return details

@app.get("/scheme/roi/{scheme_code}")
def scheme_roi(scheme_code: int, years: int = 3):
    roi = calculate_roi(scheme_code, years)
    return {"scheme_code": scheme_code, "years": years, "roi": roi}

@app.get("/screener")
def screener(amc: str, min_roi: float = 10, years: int = 3):
    result = []

    try:
        schemes = mf.get_amc_schemes(amc)
    except Exception as e:
        return {"error": f"AMC fetch failed: {str(e)}"}

    for code, name in schemes.items():
        try:
            roi = calculate_roi(code, years)
        except:
            continue

        if roi < min_roi:
            continue

        try:
            details = mf.get_scheme_details(code)
            category = details.get("category")
            risk = risk_mapper(category)
        except:
            category = None
            risk = "Unknown"

        result.append({
            "scheme_code": code,
            "scheme_name": name,
            "roi": roi,
            "category": category,
            "risk": risk
        })

    return result
