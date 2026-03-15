import numpy as np
import pandas as pd
import yfinance as yf

def calculate_sharpe_ratio(returns, risk_free_rate=0.06):
    if returns.empty:
        return 0
    excess_returns = returns - (risk_free_rate / 252)
    sharpe = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    return round(float(sharpe.iloc[0]) if hasattr(sharpe, 'iloc') else float(sharpe), 2)

def calculate_beta(stock_returns, market_returns):
    if stock_returns.empty or market_returns.empty:
        return 1.0
    aligned = pd.concat([stock_returns, market_returns], axis=1).dropna()
    if len(aligned) < 10:
        return 1.0
    covariance = aligned.cov().iloc[0, 1]
    market_var = aligned.iloc[:, 1].var()
    beta = covariance / market_var if market_var != 0 else 1.0
    return round(float(beta), 2)

def calculate_var(returns, confidence=0.95):
    if returns.empty:
        return 0
    var = np.percentile(returns.dropna(), (1 - confidence) * 100)
    return round(float(var), 4)

def calculate_max_drawdown(prices):
    if prices.empty:
        return 0
    if isinstance(prices, pd.DataFrame):
        prices = prices.squeeze()
    rolling_max = prices.cummax()
    drawdown = (prices - rolling_max) / rolling_max
    return round(float(drawdown.min().iloc[0]) if hasattr(drawdown.min(), 'iloc') else float(drawdown.min()), 4)

def calculate_volatility(returns):
    if returns.empty:
        return 0
    val = returns.std() * np.sqrt(252)
    return round(float(val.iloc[0]) if hasattr(val, 'iloc') else float(val), 4)

def calculate_all_metrics(tickers, period='1y'):
    if not tickers:
        return pd.DataFrame()
    try:
        market = yf.download('^GSPC', period=period,
                             auto_adjust=True, progress=False)['Close']
        market_returns = market.pct_change().dropna().squeeze()
    except:
        market_returns = pd.Series()

    results = []
    for ticker in tickers:
        try:
            data = yf.download(ticker, period=period,
                               auto_adjust=True, progress=False)['Close'].squeeze()
            returns = data.pct_change().dropna()

            sharpe = calculate_sharpe_ratio(returns)
            beta   = calculate_beta(returns, market_returns)
            var_95 = calculate_var(returns, 0.95)
            var_99 = calculate_var(returns, 0.99)
            max_dd = calculate_max_drawdown(data)
            vol    = calculate_volatility(returns)

            if vol < 0.15:
                risk_level = 'Low'
            elif vol < 0.30:
                risk_level = 'Medium'
            else:
                risk_level = 'High'

            results.append({
                'ticker'           : ticker,
                'sharpe_ratio'     : sharpe,
                'beta'             : beta,
                'var_95'           : f"{var_95*100:.2f}%",
                'var_99'           : f"{var_99*100:.2f}%",
                'max_drawdown'     : f"{max_dd*100:.2f}%",
                'annual_volatility': f"{vol*100:.2f}%",
                'risk_level'       : risk_level,
            })
        except Exception as e:
            print(f"Error for {ticker}: {e}")

    return pd.DataFrame(results)
