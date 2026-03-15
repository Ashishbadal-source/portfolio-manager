import pandas as pd
import numpy as np

SCENARIOS = {
    '2008 Financial Crisis'  : -0.40,
    '2020 COVID Crash'       : -0.30,
    '2022 Rate Hike Selloff' : -0.20,
    'Mild Correction'        : -0.10,
    'Moderate Bull Run'      : +0.20,
    'Strong Bull Run'        : +0.40,
}

def run_stress_test(enriched_df, custom_pct=None, custom_name=None):
    """
    Har scenario mein portfolio value calculate karta hai
    enriched_df = enrich_portfolio() ka output
    """
    if enriched_df.empty:
        return pd.DataFrame()

    scenarios = SCENARIOS.copy()
    if custom_pct is not None and custom_name:
        scenarios[custom_name] = custom_pct / 100

    total_current = enriched_df['current_value'].sum()
    total_invested = enriched_df['total_invested'].sum()

    results = []
    for scenario_name, market_change in scenarios.items():
        new_value   = total_current * (1 + market_change)
        pnl_change  = new_value - total_current
        total_pnl   = new_value - total_invested
        total_return = ((new_value - total_invested) / total_invested * 100)

        results.append({
            'scenario'       : scenario_name,
            'market_change'  : f"{market_change*100:+.0f}%",
            'portfolio_value': round(new_value, 2),
            'value_change'   : round(pnl_change, 2),
            'total_pnl'      : round(total_pnl, 2),
            'total_return'   : round(total_return, 2),
        })

    return pd.DataFrame(results)

def stock_level_stress(enriched_df, market_change_pct):
    """
    Stock level pe stress test — har stock pe alag impact
    """
    if enriched_df.empty:
        return pd.DataFrame()

    change = market_change_pct / 100
    df     = enriched_df.copy()

    df['stressed_price']  = df['current_price'] * (1 + change)
    df['stressed_value']  = df['stressed_price'] * df['total_quantity']
    df['value_change']    = df['stressed_value'] - df['current_value']
    df['stressed_return'] = ((df['stressed_value'] - df['total_invested']) / df['total_invested'] * 100).round(2)

    return df[['ticker', 'current_value', 'stressed_value', 'value_change', 'stressed_return']]
