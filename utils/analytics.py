import pandas as pd
import numpy as np
import yfinance as yf

def get_descriptive_stats(returns_df):
    """Mean, Median, Std, Skewness, Kurtosis — NumPy + Pandas"""
    if returns_df.empty:
        return pd.DataFrame()
    stats = pd.DataFrame({
        'Mean Return'  : returns_df.mean(),
        'Median Return': returns_df.median(),
        'Std Dev'      : returns_df.std(),
        'Variance'     : returns_df.var(),
        'Skewness'     : returns_df.skew(),
        'Kurtosis'     : returns_df.kurt(),
        'Min'          : returns_df.min(),
        'Max'          : returns_df.max(),
        'Range'        : returns_df.max() - returns_df.min(),
    }).round(6)
    return stats

def get_data_quality_report(enriched_df, raw_portfolio_df):
    """Missing values, duplicates, dtypes — Data Cleaning concept"""
    report = {}

    # Missing values
    missing = enriched_df.isnull().sum()
    missing_pct = (enriched_df.isnull().sum() / len(enriched_df) * 100).round(2)
    report['missing'] = pd.DataFrame({
        'Column'       : missing.index,
        'Missing Count': missing.values,
        'Missing %'    : missing_pct.values,
    })

    # Duplicates
    report['duplicates'] = {
        'total_rows'     : len(raw_portfolio_df),
        'duplicate_rows' : raw_portfolio_df.duplicated().sum(),
        'unique_tickers' : raw_portfolio_df['ticker'].nunique(),
        'total_entries'  : len(raw_portfolio_df),
    }

    # Data types
    report['dtypes'] = pd.DataFrame({
        'Column'   : enriched_df.dtypes.index,
        'Dtype'    : enriched_df.dtypes.values.astype(str),
        'Non-Null' : enriched_df.count().values,
        'Null'     : enriched_df.isnull().sum().values,
    })

    # Basic stats
    report['shape']  = enriched_df.shape
    report['memory'] = f"{enriched_df.memory_usage(deep=True).sum() / 1024:.2f} KB"

    return report

def detect_outliers(returns_df):
    """IQR + Z-Score outlier detection"""
    if returns_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    iqr_results = []
    zscore_results = []

    for col in returns_df.columns:
        data = returns_df[col].dropna()

        # IQR Method
        Q1  = data.quantile(0.25)
        Q3  = data.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        iqr_outliers = data[(data < lower) | (data > upper)]

        iqr_results.append({
            'Ticker'        : col,
            'Q1'            : round(Q1, 4),
            'Q3'            : round(Q3, 4),
            'IQR'           : round(IQR, 4),
            'Lower Bound'   : round(lower, 4),
            'Upper Bound'   : round(upper, 4),
            'Outlier Count' : len(iqr_outliers),
            'Outlier %'     : round(len(iqr_outliers) / len(data) * 100, 2),
        })

        # Z-Score Method
        z_scores    = np.abs((data - data.mean()) / data.std())
        z_outliers  = data[z_scores > 3]

        zscore_results.append({
            'Ticker'         : col,
            'Mean'           : round(data.mean(), 4),
            'Std Dev'        : round(data.std(), 4),
            'Z>3 Outliers'   : len(z_outliers),
            'Outlier %'      : round(len(z_outliers) / len(data) * 100, 2),
            'Max Z-Score'    : round(float(z_scores.max()), 2),
        })

    return pd.DataFrame(iqr_results), pd.DataFrame(zscore_results)

def get_rsi(prices, period=14):
    """RSI — Relative Strength Index"""
    delta  = prices.diff()
    gain   = delta.where(delta > 0, 0).rolling(period).mean()
    loss   = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs     = gain / loss
    rsi    = 100 - (100 / (1 + rs))
    return rsi

def get_macd(prices, fast=12, slow=26, signal=9):
    """MACD — Moving Average Convergence Divergence"""
    ema_fast   = prices.ewm(span=fast,   adjust=False).mean()
    ema_slow   = prices.ewm(span=slow,   adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram  = macd_line - signal_line
    return macd_line, signal_line, histogram

def get_rolling_stats(returns_df, window=30):
    """Rolling mean, std, correlation — Pandas"""
    if returns_df.empty:
        return {}
    rolling = {}
    for col in returns_df.columns:
        rolling[col] = {
            'rolling_mean': returns_df[col].rolling(window).mean(),
            'rolling_std' : returns_df[col].rolling(window).std(),
        }
    if len(returns_df.columns) >= 2:
        cols = returns_df.columns[:2].tolist()
        rolling['rolling_corr'] = returns_df[cols[0]].rolling(window).corr(returns_df[cols[1]])
        rolling['corr_tickers'] = cols
    return rolling
