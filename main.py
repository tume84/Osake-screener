from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TICKERS = ["AAPL", "MSFT", "NOKIA.HE", "FORTUM.HE", "TSLA", "NDA-FI.HE", "NVDA", "VALMT.HE"]

@app.get("/api/stocks")
def get_stocks():
    results = []
    
    for ticker_symbol in TICKERS:
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info or {}
            
            price = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or 1.0
            prev_close = info.get("previousClose") or price
            change = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
            
            raw_cap = info.get("marketCap") or 0
            cap_val = raw_cap / 1_000_000 if raw_cap else 1000.0
            
            cap_group = "MID"
            if cap_val >= 200_000:
                cap_group = "MEGA"
            elif cap_val >= 10_000:
                cap_group = "LARGE"

            raw_div = info.get("dividendYield") or 0.0
            div_val = raw_div * 100 if raw_div < 1 else raw_div

            results.append({
                "ticker": ticker_symbol,
                "name": info.get("shortName") or info.get("longName") or ticker_symbol,
                "sector": info.get("sector") or "Muut",
                "price": round(float(price), 2),
                "change": round(float(change), 2),
                "pe": round(float(info.get("trailingPE") or info.get("forwardPE") or 15.0), 1),
                "evEbit": round(float(info.get("enterpriseToEbitda") or 10.0), 1),
                "dividend": round(float(div_val), 2),
                "cap": round(float(cap_val), 1),
                "capGroup": cap_group
            })
        except Exception as e:
            print(f"Virhe osakkeelle {ticker_symbol}: {e}")
            
    return results
