import requests
import datetime
from sqlalchemy.orm import Session
from models import Rate
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_and_store_rates(session: Session):
    api_keys = {
        "fastforex": os.getenv("FASTFOREX_API_KEY"),
        "currencyfreaks": os.getenv("CURRENCYFREAKS_API_KEY"),
        "exchangerates": os.getenv("EXCHANGERATES_API_KEY"),
    }
    fetched_rates = []

    # FastForex
    try:
        url = f"https://api.fastforex.io/fetch-multi?from=USD&to=GBP,ZAR&api_key={api_keys['fastforex']}"
        resp = requests.get(url).json()
        usd_gbp = resp["results"]["GBP"]
        usd_zar = resp["results"]["ZAR"]
        zar_gbp = usd_gbp / usd_zar
        fetched_rates.append({"usd_gbp": usd_gbp, "usd_zar": usd_zar, "zar_gbp": zar_gbp})
    except Exception:
        pass

    # CurrencyFreaks
    try:
        url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_keys['currencyfreaks']}&symbols=GBP,ZAR"
        resp = requests.get(url).json()
        usd_gbp = float(resp["rates"]["GBP"])
        usd_zar = float(resp["rates"]["ZAR"])
        zar_gbp = usd_gbp / usd_zar
        fetched_rates.append({"usd_gbp": usd_gbp, "usd_zar": usd_zar, "zar_gbp": zar_gbp})
    except Exception:
        pass

    # ExchangeRatesAPI
    try:
        url = f"https://api.exchangeratesapi.io/v1/latest?access_key={api_keys['exchangerates']}&base=USD&symbols=GBP,ZAR"
        resp = requests.get(url).json()
        usd_gbp = resp["rates"]["GBP"]
        usd_zar = resp["rates"]["ZAR"]
        zar_gbp = usd_gbp / usd_zar
        fetched_rates.append({"usd_gbp": usd_gbp, "usd_zar": usd_zar, "zar_gbp": zar_gbp})
    except Exception:
        pass

    if not fetched_rates:
        raise ValueError("Failed to fetch rates from all APIs")

    # Calculate averages
    avg_usd_gbp = sum(r["usd_gbp"] for r in fetched_rates) / len(fetched_rates)
    avg_usd_zar = sum(r["usd_zar"] for r in fetched_rates) / len(fetched_rates)
    avg_zar_gbp = sum(r["zar_gbp"] for r in fetched_rates) / len(fetched_rates)

    # Store
    new_rate = Rate(
        timestamp=datetime.datetime.utcnow(),
        usd_gbp=avg_usd_gbp,
        usd_zar=avg_usd_zar,
        zar_gbp=avg_zar_gbp,
    )
    session.add(new_rate)
    session.commit()