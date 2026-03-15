import yfinance as yf
import re

def validate_ticker(ticker):
    if not ticker or len(ticker.strip()) == 0:
        return False, "Ticker symbol empty hai!", None

    if len(ticker) > 15:
        return False, "Ticker symbol bahut lamba hai!", None

    if not re.match(r'^[A-Z0-9.\-^=]+$', ticker.upper()):
        return False, f"'{ticker}' — invalid characters!", None

    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period='5d')

        if hist.empty:
            return False, f"'{ticker}' — No data found! Indian stocks ke liye '.NS' lagao (e.g. TCS.NS)", None

        info  = stock.info
        name  = info.get('longName') or info.get('shortName') or ticker

        return True, f"Found: {name}", {
            'name'  : name,
            'price' : info.get('currentPrice') or info.get('regularMarketPrice'),
            'sector': info.get('sector', 'N/A'),
        }

    except Exception as e:
        return False, f"'{ticker}' — Could not fetch! Check ticker symbol.", None