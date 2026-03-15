import re

KNOWN_TICKERS = {
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'NVDA', 'META',
    'JPM', 'V', 'JNJ', 'WMT', 'PG', 'MA', 'UNH', 'HD', 'BAC', 'XOM',
    'PFE', 'ABBV', 'KO', 'PEP', 'MRK', 'TMO', 'AVGO', 'COST', 'MCD',
    'ABT', 'ACN', 'DHR', 'NEE', 'LIN', 'TXN', 'BMY', 'ORCL', 'PM',
    'RTX', 'QCOM', 'HON', 'IBM', 'GS', 'INTU', 'SBUX', 'AMD', 'INTC',
    'NFLX', 'UBER', 'SPOT', 'PYPL', 'SQ', 'SHOP', 'SNAP', 'TWTR',
    'TCS.NS', 'INFY.NS', 'RELIANCE.NS', 'HCLTECH.NS', 'WIPRO.NS',
    'ICICIBANK.NS', 'HDFC.NS', 'HDFCBANK.NS', 'SBIN.NS', 'AXISBANK.NS',
    'BAJFINANCE.NS', 'KOTAKBANK.NS', 'LT.NS', 'MARUTI.NS', 'TATAMOTORS.NS',
    'TATASTEEL.NS', 'ADANIENT.NS', 'ADANIPORTS.NS', 'SUNPHARMA.NS',
    'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'ULTRACEMCO.NS', 'TITAN.NS',
    '^NSEI', '^GSPC', '^DJI', '^IXIC',
}

def validate_ticker(ticker):
    if not ticker or len(ticker.strip()) == 0:
        return False, "Please enter a ticker symbol!", None

    if len(ticker) > 15:
        return False, "Ticker symbol too long!", None

    ticker = ticker.upper().strip()

    if not re.match(r'^[A-Z0-9.\-\^=]+$', ticker):
        return False, f"'{ticker}' — Invalid characters in ticker!", None

    # Known ticker — directly allow
    if ticker in KNOWN_TICKERS:
        return True, f"Found: {ticker}", {
            'name'  : ticker,
            'price' : None,
            'sector': 'N/A',
        }

    # Indian stock check
    if '.' in ticker:
        suffix = ticker.split('.')[-1]
        if suffix in ['NS', 'BO', 'BSE']:
            return True, f"Found: {ticker}", {
                'name'  : ticker,
                'price' : None,
                'sector': 'N/A',
            }

    # US stock — basic format check (1-5 uppercase letters)
    if re.match(r'^[A-Z]{1,5}$', ticker):
        return True, f"Found: {ticker}", {
            'name'  : ticker,
            'price' : None,
            'sector': 'N/A',
        }

    return False, f"'{ticker}' — Invalid ticker! Use format: AAPL, TCS.NS", None