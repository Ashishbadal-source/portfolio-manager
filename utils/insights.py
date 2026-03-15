import yfinance as yf
import pandas as pd

def get_stock_news(ticker, max_news=5):
    try:
        stock = yf.Ticker(ticker)
        news  = stock.news
        result = []
        for item in news[:max_news]:
            content = item.get('content', {})
            result.append({
                'title'    : content.get('title', 'No title'),
                'publisher': content.get('provider', {}).get('displayName', 'Unknown'),
                'link'     : content.get('canonicalUrl', {}).get('url', '#'),
                'time'     : content.get('pubDate', ''),
            })
        return result
    except Exception as e:
        print(f"News error: {e}")
        return []

def calculate_health_score(enriched_df, risk_df=None):
    score    = 100
    reasons  = []
    warnings = []

    if enriched_df.empty:
        return 0, [], []

    valid = enriched_df.dropna(subset=['current_value'])

    # Diversification check
    num_stocks = len(valid)
    if num_stocks < 3:
        score -= 20
        warnings.append("Low diversification — add more stocks")
    elif num_stocks >= 5:
        score += 5
        reasons.append("Good diversification")

    # Concentration check
    max_weight = valid['weight'].max() if 'weight' in valid.columns else 100
    if max_weight > 50:
        score -= 15
        warnings.append(f"High concentration — one stock has {max_weight:.1f}% weight")
    elif max_weight < 30:
        reasons.append("Well distributed portfolio")

    # Return check
    total_ret = ((valid['current_value'].sum() - valid['total_invested'].sum())
                 / valid['total_invested'].sum() * 100)
    if total_ret > 20:
        score += 10
        reasons.append(f"Strong returns: +{total_ret:.1f}%")
    elif total_ret < -10:
        score -= 15
        warnings.append(f"Portfolio down {total_ret:.1f}%")

    # Losing stocks check
    losing = len(valid[valid['return_pct'] < -20])
    if losing > 0:
        score -= losing * 5
        warnings.append(f"{losing} stock(s) down more than 20%")

    # Risk check
    if risk_df is not None and not risk_df.empty:
        high_risk = len(risk_df[risk_df['risk_level'] == 'High'])
        if high_risk > len(risk_df) // 2:
            score -= 10
            warnings.append("More than half portfolio is high-risk")
        else:
            reasons.append("Balanced risk profile")

    score = max(0, min(100, score))
    return round(score), reasons, warnings

def check_price_alerts(enriched_df, alerts):
    triggered = []
    for alert in alerts:
        ticker     = alert['ticker']
        target     = alert['target']
        alert_type = alert['type']
        row = enriched_df[enriched_df['ticker'] == ticker]
        if row.empty:
            continue
        current = float(row['current_price'].values[0])
        if alert_type == 'above' and current >= target:
            triggered.append({
                'ticker' : ticker,
                'message': f"{ticker} hit  — above your target of ",
                'type'   : 'success'
            })
        elif alert_type == 'below' and current <= target:
            triggered.append({
                'ticker' : ticker,
                'message': f"{ticker} hit  — below your target of ",
                'type'   : 'warning'
            })
    return triggered
