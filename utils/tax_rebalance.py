import pandas as pd
import numpy as np

def calculate_rebalancing(enriched_df, target_weights=None):
    """
    Current vs Target allocation compare karta hai
    aur rebalancing suggestions deta hai
    """
    if enriched_df.empty:
        return pd.DataFrame()

    df = enriched_df.copy()
    n  = len(df)

    if target_weights is None:
        target_weights = {ticker: round(100/n, 2) for ticker in df['ticker']}

    total_value = df['current_value'].sum()
    results = []

    for _, row in df.iterrows():
        ticker          = row['ticker']
        current_val     = row['current_value']
        current_weight  = row['weight']
        target_weight   = target_weights.get(ticker, round(100/n, 2))
        target_value    = total_value * target_weight / 100
        diff_value      = target_value - current_val
        diff_weight     = target_weight - current_weight
        current_price   = row['current_price']
        shares_to_trade = diff_value / current_price if current_price else 0

        if abs(diff_weight) < 1:
            action = 'Hold'
        elif diff_value > 0:
            action = 'Buy'
        else:
            action = 'Sell'

        results.append({
            'ticker'         : ticker,
            'current_weight' : round(current_weight, 2),
            'target_weight'  : round(target_weight, 2),
            'diff_weight'    : round(diff_weight, 2),
            'current_value'  : round(current_val, 2),
            'target_value'   : round(target_value, 2),
            'diff_value'     : round(diff_value, 2),
            'shares_to_trade': round(abs(shares_to_trade), 2),
            'action'         : action,
        })

    return pd.DataFrame(results)


def calculate_tax(enriched_df, tax_rate_short=30.0, tax_rate_long=15.0):
    """
    Capital gains tax estimate karta hai
    Short term = held < 1 year
    Long term  = held >= 1 year
    """
    if enriched_df.empty:
        return pd.DataFrame(), {}

    from datetime import datetime
    df = enriched_df.copy()

    results = []
    total_short_gain = 0
    total_long_gain  = 0
    total_short_tax  = 0
    total_long_tax   = 0

    for _, row in df.iterrows():
        profit = row['profit_loss']
        if profit <= 0:
            results.append({
                'ticker'      : row['ticker'],
                'profit_loss' : round(profit, 2),
                'hold_type'   : 'Loss',
                'tax_rate'    : 0,
                'estimated_tax': 0,
                'net_after_tax': round(profit, 2),
            })
            continue

        try:
            purchase_date = pd.to_datetime(row['first_purchase'])
            days_held     = (datetime.now() - purchase_date).days
        except:
            days_held = 365

        if days_held < 365:
            hold_type    = 'Short Term'
            tax_rate     = tax_rate_short
            total_short_gain += profit
        else:
            hold_type    = 'Long Term'
            tax_rate     = tax_rate_long
            total_long_gain += profit

        tax_amount = profit * tax_rate / 100

        if hold_type == 'Short Term':
            total_short_tax += tax_amount
        else:
            total_long_tax += tax_amount

        results.append({
            'ticker'       : row['ticker'],
            'profit_loss'  : round(profit, 2),
            'days_held'    : days_held,
            'hold_type'    : hold_type,
            'tax_rate'     : f"{tax_rate}%",
            'estimated_tax': round(tax_amount, 2),
            'net_after_tax': round(profit - tax_amount, 2),
        })

    summary = {
        'total_short_gain': round(total_short_gain, 2),
        'total_long_gain' : round(total_long_gain, 2),
        'total_short_tax' : round(total_short_tax, 2),
        'total_long_tax'  : round(total_long_tax, 2),
        'total_tax'       : round(total_short_tax + total_long_tax, 2),
        'net_after_tax'   : round(
            (total_short_gain + total_long_gain) - (total_short_tax + total_long_tax), 2
        ),
    }

    return pd.DataFrame(results), summary
