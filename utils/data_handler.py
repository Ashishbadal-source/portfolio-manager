import pandas as pd
import numpy as np
import yfinance as yf
from database.db_handler import get_portfolio_summary

def fetch_live_prices(tickers):
    prices = {}
    if not tickers:
        return prices
    try:
        tickers_str = ' '.join(tickers)
        data = yf.download(tickers_str, period='1d', interval='1m',
                          progress=False, auto_adjust=True)
        if len(tickers) == 1:
            prices[tickers[0]] = float(data['Close'].iloc[-1])
        else:
            for ticker in tickers:
                try:
                    prices[ticker] = float(data['Close'][ticker].dropna().iloc[-1])
                except:
                    prices[ticker] = None
    except Exception as e:
        print(f"Price fetch error: {e}")
    return prices

def fetch_historical_data(ticker, period='1y'):
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(period=period, auto_adjust=True)
        return hist
    except Exception as e:
        print(f"Historical data error: {e}")
        return pd.DataFrame()

def fetch_ticker_info(ticker):
    try:
        info = yf.Ticker(ticker).info
        return {
            'name'      : info.get('longName', ticker),
            'sector'    : info.get('sector', 'Unknown'),
            'industry'  : info.get('industry', 'Unknown'),
            'market_cap': info.get('marketCap', None),
            'pe_ratio'  : info.get('trailingPE', None),
            'beta'      : info.get('beta', None),
        }
    except:
        return {'name': ticker, 'sector': 'Unknown', 'industry': 'Unknown'}

def enrich_portfolio(live_prices, user_id):
    df = get_portfolio_summary(user_id)
    if df.empty:
        return df

    df['total_quantity'] = pd.to_numeric(df['total_quantity'], errors='coerce').fillna(0)
    df['avg_buy_price']  = pd.to_numeric(df['avg_buy_price'],  errors='coerce').fillna(0)
    df['total_invested'] = pd.to_numeric(df['total_invested'], errors='coerce').fillna(0)

    df['current_price'] = df['ticker'].map(live_prices)
    df['current_price'] = pd.to_numeric(df['current_price'],  errors='coerce')
    df['current_value'] = df['current_price'] * df['total_quantity']
    df['profit_loss']   = df['current_value'] - df['total_invested']
    df['return_pct']    = ((df['current_value'] - df['total_invested']) / df['total_invested'] * 100).round(2)

    total_val    = df['current_value'].sum()
    df['weight'] = (df['current_value'] / total_val * 100).round(2) if total_val > 0 else 0

    return df

def portfolio_summary_stats(enriched_df):
    valid = enriched_df.dropna(subset=['current_value'])
    if valid.empty:
        return {}
    total_invested = float(valid['total_invested'].sum())
    total_value    = float(valid['current_value'].sum())
    return {
        'total_invested'   : total_invested,
        'total_value'      : total_value,
        'total_profit'     : float(valid['profit_loss'].sum()),
        'total_return_pct' : ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0,
        'num_stocks'       : len(valid),
        'best_stock'       : valid.loc[valid['return_pct'].idxmax(), 'ticker'],
        'worst_stock'      : valid.loc[valid['return_pct'].idxmin(), 'ticker'],
    }

def get_returns_matrix(tickers, period='1y'):
    try:
        raw = yf.download(' '.join(tickers), period=period,
                         auto_adjust=True, progress=False)['Close']
        if isinstance(raw, pd.Series):
            raw = raw.to_frame(name=tickers[0])
        returns = raw.pct_change().dropna()
        return returns
    except Exception as e:
        print(f"Returns matrix error: {e}")
        return pd.DataFrame()
