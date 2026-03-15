import yfinance as yf

def validate_ticker(ticker):
    """
    Ticker valid hai ya nahi check karta hai
    Returns: (is_valid, message, info)
    """
    if not ticker or len(ticker.strip()) == 0:
        return False, "Ticker symbol empty hai!", None

    if len(ticker) > 10:
        return False, "Ticker symbol bahut lamba hai!", None

    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        # Agar name nahi mila toh invalid ticker hai
        name = info.get('longName') or info.get('shortName') or None

        if not name:
            return False, f"'{ticker}' — ye ticker valid nahi hai! Indian stocks ke liye '.NS' lagao (e.g. HCLTECH.NS)", None

        price = info.get('currentPrice') or info.get('regularMarketPrice') or None

        return True, f"Found: {name}", {
            'name'  : name,
            'price' : price,
            'sector': info.get('sector', 'N/A'),
        }

    except Exception as e:
        return False, f"'{ticker}' fetch nahi ho saka — internet check karo!", None
