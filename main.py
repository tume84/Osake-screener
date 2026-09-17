from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

# Sallitaan haut frontendiltä (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seurattavat osakkeet (US & Pohjoismaat)
TICKERS = ["AAPL", "MSFT", "NOKIA.HE", "FORTUM.HE", "TSLA", "NDA-FI.HE", "NVDA", "VALMT.HE"]

@app.get("/api/stocks")
def get_stocks():
    results = []
    
    for ticker_symbol in TICKERS:
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info
            
            # Apufunktio turvalliseen datanhakuun
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
            prev_close = info.get("previousClose") or price
            change = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
            
            cap_val = info.get("marketCap", 0) / 1_000_000  # Muutetaan miljooniksi
            cap_group = "MID"
            if cap_val >= 200_000:
                cap_group = "MEGA"
            elif cap_val >= 10_000:
                cap_group = "LARGE"

            results.append({
                "ticker": ticker_symbol,
                "name": info.get("shortName", ticker_symbol),
                "sector": info.get("sector", "Muut"),
                "price": round(price, 2),
                "change": round(change, 2),
                "pe": round(info.get("trailingPE", 0) or 0, 1),
                "evEbit": round(info.get("enterpriseToEbitda", 0) or 0, 1),
                "dividend": round((info.get("dividendYield", 0) or 0) * 100, 2),
                "cap": round(cap_val, 1),
                "capGroup": cap_group
            })
        except Exception as e:
            print(f"Virhe haettaessa {ticker_symbol}: {e}")
            
    return results
