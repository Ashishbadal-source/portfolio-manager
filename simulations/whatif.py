import pandas as pd
import numpy as np

def whatif_single_stock(enriched_df, ticker, change_pct):
    """
    Agar ek stock X% badhe/ghate to portfolio pe kya asar
    """
    if enriched_df.empty:
        return {}

    df = enriched_df.copy()
    total_current = df['current_value'].sum()
    total_invested = df['total_invested'].sum()

    stock_row = df[df['ticker'] == ticker]
    if stock_row.empty:
        return {}

    change        = change_pct / 100
    old_value     = float(stock_row['current_value'].values[0])
    new_value     = old_value * (1 + change)
    value_diff    = new_value - old_value

    new_portfolio_value  = total_current + value_diff
    new_portfolio_return = ((new_portfolio_value - total_invested) / total_invested * 100)

    return {
        'ticker'              : ticker,
        'change_pct'          : change_pct,
        'old_stock_value'     : round(old_value, 2),
        'new_stock_value'     : round(new_value, 2),
        'old_portfolio_value' : round(total_current, 2),
        'new_portfolio_value' : round(new_portfolio_value, 2),
        'portfolio_impact'    : round(value_diff, 2),
        'new_return_pct'      : round(new_portfolio_return, 2),
    }

def whatif_all_stocks(enriched_df, changes_dict):
    """
    Multiple stocks ke liye ek saath what-if
    changes_dict = {'AAPL': 10, 'TSLA': -5, 'NVDA': 20}
    """
    if enriched_df.empty:
        return pd.DataFrame()

    df             = enriched_df.copy()
    total_invested = df['total_invested'].sum()

    df['change_pct']    = df['ticker'].map(changes_dict).fillna(0)
    df['new_value']     = df['current_value'] * (1 + df['change_pct'] / 100)
    df['value_change']  = df['new_value'] - df['current_value']
    df['new_return']    = ((df['new_value'] - df['total_invested']) / df['total_invested'] * 100).round(2)

    summary = {
        'old_total'  : round(df['current_value'].sum(), 2),
        'new_total'  : round(df['new_value'].sum(), 2),
        'difference' : round(df['value_change'].sum(), 2),
        'new_return' : round(
            (df['new_value'].sum() - total_invested) / total_invested * 100, 2
        ),
    }

    return df[['ticker', 'current_value', 'new_value', 'value_change', 'new_return']], summary

def best_worst_case(enriched_df, bull_pct=20, bear_pct=-20):
    """
    Best case aur worst case scenario ek saath
    """
    if enriched_df.empty:
        return {}

    total_current  = enriched_df['current_value'].sum()
    total_invested = enriched_df['total_invested'].sum()

    bull_value = total_current * (1 + bull_pct / 100)
    bear_value = total_current * (1 + bear_pct / 100)

    return {
        'current_value'  : round(total_current, 2),
        'bull_value'     : round(bull_value, 2),
        'bear_value'     : round(bear_value, 2),
        'bull_return'    : round((bull_value - total_invested) / total_invested * 100, 2),
        'bear_return'    : round((bear_value - total_invested) / total_invested * 100, 2),
        'bull_pct'       : bull_pct,
        'bear_pct'       : bear_pct,
    }
