import numpy as np
import pandas as pd
import yfinance as yf

def simulate_random_walk(ticker, days=90, simulations=100, period='1y'):
    try:
        stock = yf.Ticker(ticker)
        data  = stock.history(period=period, auto_adjust=True)['Close']

        if data.empty:
            return pd.DataFrame()

        data       = pd.Series(data.values, index=data.index)
        returns    = data.pct_change().dropna()
        mu         = float(returns.mean())
        sigma      = float(returns.std())
        last_price = float(data.iloc[-1])

        np.random.seed(42)
        all_paths = []

        for i in range(simulations):
            prices = [last_price]
            for _ in range(days - 1):
                shock  = float(np.random.normal(0, 1))
                change = mu + sigma * shock
                prices.append(prices[-1] * (1 + change))
            all_paths.append(prices)

        paths_array = np.array(all_paths).T
        date_index  = pd.bdate_range(start=pd.Timestamp.today(), periods=days)
        df = pd.DataFrame(
            paths_array,
            index=date_index,
            columns=[f'sim_{i}' for i in range(simulations)]
        )
        return df

    except Exception as e:
        print(f"Random walk error: {e}")
        return pd.DataFrame()

def get_confidence_intervals(paths_df):
    if paths_df.empty:
        return pd.DataFrame()
    return pd.DataFrame({
        'lower_95': paths_df.quantile(0.05, axis=1),
        'median'  : paths_df.quantile(0.50, axis=1),
        'upper_95': paths_df.quantile(0.95, axis=1),
    })
