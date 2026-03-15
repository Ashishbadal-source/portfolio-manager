import numpy as np
import pandas as pd
import yfinance as yf

def run_monte_carlo(tickers, period='1y', simulations=10000):
    if len(tickers) < 2:
        return pd.DataFrame()
    try:
        data = yf.download(' '.join(tickers), period=period,
                          auto_adjust=True, progress=False)['Close']
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])
        returns      = data.pct_change().dropna()
        mean_returns = returns.mean()
        cov_matrix   = returns.cov()

        results = []
        np.random.seed(42)
        for _ in range(simulations):
            weights = np.random.random(len(tickers))
            weights = weights / weights.sum()

            port_return = float(np.sum(mean_returns.values * weights) * 252)
            port_risk   = float(np.sqrt(
                np.dot(weights.T, np.dot(cov_matrix.values * 252, weights))
            ))
            sharpe = (port_return - 0.06) / port_risk if port_risk != 0 else 0

            results.append({
                'return' : round(port_return * 100, 2),
                'risk'   : round(port_risk * 100, 2),
                'sharpe' : round(float(sharpe), 3),
                'weights': weights.tolist(),
            })

        df = pd.DataFrame(results)
        df = df.reset_index(drop=True)
        return df

    except Exception as e:
        print(f"Monte Carlo error: {e}")
        return pd.DataFrame()

def get_optimal_portfolio(mc_df, tickers):
    if mc_df.empty:
        return {}
    try:
        idx     = int(mc_df['sharpe'].idxmax())
        best    = mc_df.iloc[idx]
        weights = best['weights']
        return {
            'tickers'        : tickers,
            'weights'        : [round(w * 100, 2) for w in weights],
            'expected_return': best['return'],
            'expected_risk'  : best['risk'],
            'sharpe_ratio'   : best['sharpe'],
        }
    except Exception as e:
        print(f"Optimal portfolio error: {e}")
        return {}

def get_min_volatility_portfolio(mc_df, tickers):
    if mc_df.empty:
        return {}
    try:
        idx     = int(mc_df['risk'].idxmin())
        best    = mc_df.iloc[idx]
        weights = best['weights']
        return {
            'tickers'        : tickers,
            'weights'        : [round(w * 100, 2) for w in weights],
            'expected_return': best['return'],
            'expected_risk'  : best['risk'],
            'sharpe_ratio'   : best['sharpe'],
        }
    except Exception as e:
        print(f"Min vol error: {e}")
        return {}
