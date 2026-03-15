import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import yfinance as yf

# Colors
POSITIVE  = '#00C896'
NEGATIVE  = '#FF4B6E'
BG        = '#0E1117'
CARD_BG   = '#1C2333'
TEXT      = '#E8EDF2'
PALETTE   = px.colors.qualitative.Plotly
LAYOUT = dict(
    paper_bgcolor=BG, plot_bgcolor=BG,
    font=dict(color=TEXT, family='Inter, sans-serif'),
    margin=dict(l=20, r=20, t=45, b=20),
)

# ── 1. Allocation Pie ──────────────────────────────────────────────────────────
def allocation_pie(df):
    fig = px.pie(df, values='current_value', names='ticker',
                 title='Portfolio Allocation',
                 color_discrete_sequence=PALETTE, hole=0.45)
    fig.update_traces(textposition='outside', textinfo='label+percent',
                      hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<extra></extra>')
    fig.update_layout(**LAYOUT)
    return fig

# ── 2. Profit Loss Bar ─────────────────────────────────────────────────────────
def profit_loss_bar(df):
    df_sorted = df.sort_values('profit_loss', ascending=True)
    colors    = [POSITIVE if v >= 0 else NEGATIVE for v in df_sorted['profit_loss']]
    fig = go.Figure(go.Bar(
        x=df_sorted['profit_loss'], y=df_sorted['ticker'],
        orientation='h', marker_color=colors,
        text=[f'' for v in df_sorted['profit_loss']],
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>P&L: $%{x:+,.2f}<extra></extra>',
    ))
    fig.update_layout(**LAYOUT, title='Profit / Loss per Stock',
                      xaxis=dict(gridcolor='#1e2535', zeroline=True, zerolinecolor='#444'),
                      yaxis=dict(gridcolor='#1e2535'))
    return fig

# ── 3. Return % Bar ────────────────────────────────────────────────────────────
def return_pct_bar(df):
    df_sorted = df.sort_values('return_pct', ascending=False)
    colors    = [POSITIVE if v >= 0 else NEGATIVE for v in df_sorted['return_pct']]
    fig = go.Figure(go.Bar(
        x=df_sorted['ticker'], y=df_sorted['return_pct'],
        marker_color=colors,
        text=[f'{v:+.1f}%' for v in df_sorted['return_pct']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Return: %{y:+.2f}%<extra></extra>',
    ))
    fig.update_layout(**LAYOUT, title='Return % per Stock',
                      yaxis=dict(gridcolor='#1e2535', zeroline=True, zerolinecolor='#444'),
                      xaxis=dict(gridcolor='#1e2535'))
    return fig

# ── 4. Candlestick + Bollinger + MA ───────────────────────────────────────────
def candlestick_chart(hist_df, ticker):
    if hist_df.empty:
        return go.Figure().update_layout(**LAYOUT, title=f'No data for {ticker}')
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03, row_heights=[0.75, 0.25])
    fig.add_trace(go.Candlestick(
        x=hist_df.index,
        open=hist_df['Open'], high=hist_df['High'],
        low=hist_df['Low'],   close=hist_df['Close'],
        name=ticker,
        increasing_line_color=POSITIVE,
        decreasing_line_color=NEGATIVE,
    ), row=1, col=1)
    if len(hist_df) >= 20:
        ma20 = hist_df['Close'].rolling(20).mean()
        fig.add_trace(go.Scatter(x=hist_df.index, y=ma20, name='20-MA',
                                 line=dict(color='#FFA500', width=1.5, dash='dot')), row=1, col=1)
    if len(hist_df) >= 50:
        ma50 = hist_df['Close'].rolling(50).mean()
        fig.add_trace(go.Scatter(x=hist_df.index, y=ma50, name='50-MA',
                                 line=dict(color='#00BFFF', width=1.5, dash='dash')), row=1, col=1)
    if len(hist_df) >= 200:
        ma200 = hist_df['Close'].rolling(200).mean()
        fig.add_trace(go.Scatter(x=hist_df.index, y=ma200, name='200-MA',
                                 line=dict(color='#FF69B4', width=1.5)), row=1, col=1)
    if len(hist_df) >= 20:
        bb_mid  = hist_df['Close'].rolling(20).mean()
        bb_std  = hist_df['Close'].rolling(20).std()
        bb_up   = bb_mid + 2 * bb_std
        bb_down = bb_mid - 2 * bb_std
        fig.add_trace(go.Scatter(x=hist_df.index, y=bb_up, name='BB Upper',
                                 line=dict(color='rgba(150,150,255,0.5)', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist_df.index, y=bb_down, name='BB Lower',
                                 fill='tonexty', fillcolor='rgba(150,150,255,0.05)',
                                 line=dict(color='rgba(150,150,255,0.5)', width=1)), row=1, col=1)
    vol_colors = [POSITIVE if c >= o else NEGATIVE
                  for c, o in zip(hist_df['Close'], hist_df['Open'])]
    fig.add_trace(go.Bar(x=hist_df.index, y=hist_df['Volume'],
                         marker_color=vol_colors, name='Volume', opacity=0.6), row=2, col=1)
    fig.update_layout(**LAYOUT, title=f'{ticker} — Price, MA, Bollinger Bands & Volume',
                      xaxis_rangeslider_visible=False,
                      xaxis2=dict(title='Date', gridcolor='#1e2535'),
                      yaxis=dict(title='Price', gridcolor='#1e2535'),
                      yaxis2=dict(title='Volume', gridcolor='#1e2535'))
    return fig

# ── 5. RSI Chart ───────────────────────────────────────────────────────────────
def rsi_chart(prices, ticker):
    from utils.analytics import get_rsi
    rsi = get_rsi(prices)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prices.index, y=rsi,
                             name='RSI', line=dict(color='#9370DB', width=2)))
    fig.add_hline(y=70, line_dash='dash', line_color=NEGATIVE,
                  annotation_text='Overbought (70)', annotation_font_color=NEGATIVE)
    fig.add_hline(y=30, line_dash='dash', line_color=POSITIVE,
                  annotation_text='Oversold (30)', annotation_font_color=POSITIVE)
    fig.add_hrect(y0=70, y1=100, fillcolor=NEGATIVE, opacity=0.05, line_width=0)
    fig.add_hrect(y0=0,  y1=30,  fillcolor=POSITIVE, opacity=0.05, line_width=0)
    fig.update_layout(**LAYOUT, title=f'{ticker} — RSI (14)',
                      xaxis=dict(gridcolor='#1e2535'),
                      yaxis=dict(title='RSI', gridcolor='#1e2535', range=[0,100]))
    return fig

# ── 6. MACD Chart ──────────────────────────────────────────────────────────────
def macd_chart(prices, ticker):
    from utils.analytics import get_macd
    macd_line, signal_line, histogram = get_macd(prices)
    colors = [POSITIVE if v >= 0 else NEGATIVE for v in histogram.fillna(0)]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05, row_heights=[0.6, 0.4])
    fig.add_trace(go.Scatter(x=prices.index, y=prices,
                             name='Price', line=dict(color=TEXT, width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=macd_line,
                             name='MACD', line=dict(color='#00BFFF', width=2)), row=2, col=1)
    fig.add_trace(go.Scatter(x=prices.index, y=signal_line,
                             name='Signal', line=dict(color='#FFA500', width=2)), row=2, col=1)
    fig.add_trace(go.Bar(x=prices.index, y=histogram,
                         name='Histogram', marker_color=colors, opacity=0.7), row=2, col=1)
    fig.update_layout(**LAYOUT, title=f'{ticker} — MACD (12, 26, 9)',
                      xaxis2=dict(gridcolor='#1e2535'),
                      yaxis=dict(title='Price', gridcolor='#1e2535'),
                      yaxis2=dict(title='MACD', gridcolor='#1e2535'))
    return fig

# ── 7. Portfolio Value Over Time ───────────────────────────────────────────────
def portfolio_value_chart(tickers, quantities, buy_prices, period='1y'):
    if not tickers:
        return go.Figure().update_layout(**LAYOUT)
    try:
        data = yf.download(' '.join(tickers), period=period,
                           auto_adjust=True, progress=False)['Close']
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])
        data.dropna(how='all', inplace=True)
        port_val = pd.Series(0.0, index=data.index)
        for t in tickers:
            if t in data.columns:
                port_val += data[t].ffill() * quantities.get(t, 0)
        invested = sum(buy_prices.get(t, 0) * quantities.get(t, 0) for t in tickers)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=port_val.index, y=port_val,
                                 fill='tozeroy', name='Portfolio Value',
                                 line=dict(color=POSITIVE, width=2),
                                 fillcolor='rgba(0,200,150,0.12)'))
        fig.add_trace(go.Scatter(x=port_val.index,
                                 y=pd.Series(invested, index=port_val.index),
                                 name='Invested', line=dict(color='#888', width=1.5, dash='dash')))
        fig.update_layout(**LAYOUT, title='Portfolio Value Over Time',
                          xaxis=dict(gridcolor='#1e2535'),
                          yaxis=dict(title='Value ($)', gridcolor='#1e2535'))
        return fig
    except Exception as e:
        return go.Figure().update_layout(**LAYOUT, title=f'Error: {e}')

# ── 8. Portfolio Drawdown ─────────────────────────────────────────────────────
def portfolio_drawdown_chart(tickers, quantities, period='1y'):
    try:
        data = yf.download(' '.join(tickers), period=period,
                           auto_adjust=True, progress=False)['Close']
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])
        port_val    = pd.Series(0.0, index=data.index)
        for t in tickers:
            if t in data.columns:
                port_val += data[t].ffill() * quantities.get(t, 0)
        rolling_max = port_val.cummax()
        drawdown    = (port_val - rolling_max) / rolling_max * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=drawdown.index, y=drawdown,
                                 fill='tozeroy', name='Drawdown',
                                 line=dict(color=NEGATIVE, width=2),
                                 fillcolor='rgba(255,75,110,0.15)'))
        fig.update_layout(**LAYOUT, title='Portfolio Drawdown (%)',
                          xaxis=dict(gridcolor='#1e2535'),
                          yaxis=dict(title='Drawdown (%)', gridcolor='#1e2535'))
        return fig
    except Exception as e:
        return go.Figure().update_layout(**LAYOUT, title=f'Error: {e}')

# ── 9. Stock Comparison ────────────────────────────────────────────────────────
def stock_comparison_chart(tickers, period='1y'):
    try:
        data = yf.download(' '.join(tickers), period=period,
                           auto_adjust=True, progress=False)['Close']
        if isinstance(data, pd.Series):
            data = data.to_frame(name=tickers[0])
        normalized = (data / data.iloc[0]) * 100
        fig = go.Figure()
        for i, ticker in enumerate(tickers):
            if ticker in normalized.columns:
                fig.add_trace(go.Scatter(
                    x=normalized.index, y=normalized[ticker],
                    name=ticker, line=dict(width=2, color=PALETTE[i % len(PALETTE)]),
                ))
        fig.add_hline(y=100, line_dash='dot', line_color='#555')
        fig.update_layout(**LAYOUT, title='Stock Performance Comparison (Normalized to 100)',
                          xaxis=dict(gridcolor='#1e2535'),
                          yaxis=dict(title='Normalized Price', gridcolor='#1e2535'))
        return fig
    except Exception as e:
        return go.Figure().update_layout(**LAYOUT, title=f'Error: {e}')

# ── 10. Rolling Statistics Chart ──────────────────────────────────────────────
def rolling_stats_chart(returns_df, ticker, window=30):
    if returns_df.empty or ticker not in returns_df.columns:
        return go.Figure().update_layout(**LAYOUT)
    data         = returns_df[ticker]
    rolling_mean = data.rolling(window).mean()
    rolling_std  = data.rolling(window).std()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.05,
                        subplot_titles=[f'{ticker} Rolling Mean ({window}d)',
                                        f'{ticker} Rolling Std Dev ({window}d)'])
    fig.add_trace(go.Scatter(x=data.index, y=data,
                             name='Daily Return', line=dict(color='#7B8FA1', width=0.8),
                             opacity=0.5), row=1, col=1)
    fig.add_trace(go.Scatter(x=rolling_mean.index, y=rolling_mean,
                             name='Rolling Mean', line=dict(color=POSITIVE, width=2)), row=1, col=1)
    fig.add_trace(go.Scatter(x=rolling_std.index, y=rolling_std,
                             name='Rolling Std', line=dict(color='#FFA500', width=2)), row=2, col=1)
    fig.update_layout(**LAYOUT, title=f'{ticker} — Rolling Statistics ({window}-day window)',
                      xaxis2=dict(gridcolor='#1e2535'),
                      yaxis=dict(gridcolor='#1e2535'),
                      yaxis2=dict(gridcolor='#1e2535'))
    return fig

# ── 11. Rolling Correlation Chart ─────────────────────────────────────────────
def rolling_correlation_chart(returns_df, window=30):
    if returns_df.empty or len(returns_df.columns) < 2:
        return go.Figure().update_layout(**LAYOUT)
    cols   = returns_df.columns[:2].tolist()
    roll_c = returns_df[cols[0]].rolling(window).corr(returns_df[cols[1]])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=roll_c.index, y=roll_c,
                             name=f'Corr({cols[0]},{cols[1]})',
                             line=dict(color='#9370DB', width=2),
                             fill='tozeroy', fillcolor='rgba(147,112,219,0.1)'))
    fig.add_hline(y=0, line_dash='dot', line_color='#555')
    fig.update_layout(**LAYOUT,
                      title=f'Rolling {window}-day Correlation: {cols[0]} vs {cols[1]}',
                      xaxis=dict(gridcolor='#1e2535'),
                      yaxis=dict(title='Correlation', gridcolor='#1e2535', range=[-1,1]))
    return fig

# ── 12. Correlation Heatmap (Seaborn) ─────────────────────────────────────────
def correlation_heatmap_seaborn(corr_df):
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    sns.heatmap(corr_df, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, vmin=-1, vmax=1, ax=ax,
                annot_kws={'color': TEXT, 'size': 11},
                linewidths=0.5, linecolor='#2E3A4E')
    ax.tick_params(colors=TEXT, labelcolor=TEXT)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.set_xticklabels(ax.get_xticklabels(), color=TEXT)
    ax.set_yticklabels(ax.get_yticklabels(), color=TEXT)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=TEXT, labelcolor=TEXT)
    cbar.ax.yaxis.label.set_color(TEXT)
    plt.title('Stock Return Correlation Matrix', color=TEXT, pad=15, fontsize=14)
    plt.tight_layout()
    return fig

# ── 13. Efficient Frontier ─────────────────────────────────────────────────────
def efficient_frontier_chart(mc_df, optimal, min_vol):
    if mc_df.empty:
        return go.Figure().update_layout(**LAYOUT)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=mc_df['risk'], y=mc_df['return'],
        mode='markers', name='Portfolios',
        marker=dict(color=mc_df['sharpe'], colorscale='Viridis',
                    size=3, opacity=0.6,
                    colorbar=dict(title='Sharpe', tickcolor=TEXT)),
    ))
    if optimal:
        fig.add_trace(go.Scatter(
            x=[optimal['expected_risk']], y=[optimal['expected_return']],
            mode='markers', name='Max Sharpe',
            marker=dict(color='#FFD700', size=15, symbol='star'),
        ))
    if min_vol:
        fig.add_trace(go.Scatter(
            x=[min_vol['expected_risk']], y=[min_vol['expected_return']],
            mode='markers', name='Min Volatility',
            marker=dict(color='#00BFFF', size=15, symbol='diamond'),
        ))
    fig.update_layout(**LAYOUT, title='Efficient Frontier — 10,000 Portfolios',
                      xaxis=dict(title='Risk (%)', gridcolor='#1e2535'),
                      yaxis=dict(title='Return (%)', gridcolor='#1e2535'))
    return fig

# ── 14. Random Walk ───────────────────────────────────────────────────────────
def random_walk_chart(paths_df, ci_df, ticker):
    if paths_df.empty:
        return go.Figure().update_layout(**LAYOUT)
    fig = go.Figure()
    for col in paths_df.columns[:50]:
        fig.add_trace(go.Scatter(x=paths_df.index, y=paths_df[col],
                                 mode='lines', line=dict(width=0.5, color='rgba(100,149,237,0.15)'),
                                 showlegend=False))
    if not ci_df.empty:
        fig.add_trace(go.Scatter(x=ci_df.index, y=ci_df['upper_95'],
                                 line=dict(color=POSITIVE, width=2), name='95th Percentile'))
        fig.add_trace(go.Scatter(x=ci_df.index, y=ci_df['median'],
                                 line=dict(color='#FFD700', width=2, dash='dash'), name='Median'))
        fig.add_trace(go.Scatter(x=ci_df.index, y=ci_df['lower_95'],
                                 line=dict(color=NEGATIVE, width=2), name='5th Percentile'))
    fig.update_layout(**LAYOUT, title=f'{ticker} — Random Walk Simulation',
                      xaxis=dict(gridcolor='#1e2535'),
                      yaxis=dict(title='Price ($)', gridcolor='#1e2535'))
    return fig

# ── 15. Stress Test ───────────────────────────────────────────────────────────
def stress_test_chart(stress_df):
    if stress_df.empty:
        return go.Figure().update_layout(**LAYOUT)
    colors = [POSITIVE if v >= 0 else NEGATIVE for v in stress_df['value_change']]
    fig = go.Figure(go.Bar(
        x=stress_df['scenario'], y=stress_df['portfolio_value'],
        marker_color=colors,
        text=[f'' for v in stress_df['portfolio_value']],
        textposition='outside',
    ))
    fig.update_layout(**LAYOUT, title='Stress Test — Portfolio Value per Scenario',
                      xaxis=dict(gridcolor='#1e2535'),
                      yaxis=dict(title='Portfolio Value ($)', gridcolor='#1e2535'))
    return fig

# ── 16. Returns Distribution (Seaborn) ────────────────────────────────────────
def returns_distribution(returns_df, ticker):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.patch.set_facecolor(BG)
    for ax in axes:
        ax.set_facecolor(CARD_BG)
        ax.tick_params(colors=TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor('#2E3A4E')
    if ticker in returns_df.columns:
        data = returns_df[ticker].dropna()
        sns.histplot(data, ax=axes[0], kde=True, color='#6495ED', edgecolor='none')
        axes[0].set_title(f'{ticker} Returns Distribution', color=TEXT)
        axes[0].set_xlabel('Daily Return', color=TEXT)
        axes[0].set_ylabel('Frequency', color=TEXT)
        sns.boxplot(x=data, ax=axes[1], color='#6495ED')
        axes[1].set_title(f'{ticker} Returns Boxplot', color=TEXT)
        axes[1].set_xlabel('Daily Return', color=TEXT)
    plt.tight_layout()
    return fig

# ── 17. Pair Plot (Seaborn) ────────────────────────────────────────────────────
def pair_plot(returns_df):
    if returns_df.empty or len(returns_df.columns) < 2:
        fig, ax = plt.subplots(figsize=(8,6))
        fig.patch.set_facecolor(BG)
        ax.text(0.5, 0.5, 'Need 2+ stocks', ha='center', va='center', color=TEXT)
        return fig
    plt.style.use('dark_background')
    g = sns.pairplot(
        returns_df.dropna(),
        diag_kind='kde',
        plot_kws=dict(alpha=0.5, color='#6495ED', edgecolor='none'),
        diag_kws=dict(color='#00C896', fill=True),
    )
    g.fig.patch.set_facecolor(BG)
    for ax in g.axes.flatten():
        if ax:
            ax.set_facecolor(CARD_BG)
            ax.tick_params(colors=TEXT, labelcolor=TEXT)
            ax.xaxis.label.set_color(TEXT)
            ax.yaxis.label.set_color(TEXT)
            for spine in ax.spines.values():
                spine.set_edgecolor('#2E3A4E')
    g.fig.suptitle('Stock Returns Pair Plot', color=TEXT, y=1.02, fontsize=14)
    plt.tight_layout()
    return g.fig

# ── 18. Rolling Returns Heatmap (Seaborn + Pandas) ────────────────────────────
def rolling_returns_heatmap(returns_df):
    fig, ax = plt.subplots(figsize=(14, len(returns_df.columns) * 1.2 + 2))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    monthly = returns_df.resample('ME').apply(lambda x: (1 + x).prod() - 1) * 100
    monthly = monthly.T
    monthly.columns = [c.strftime('%b %Y') for c in monthly.columns]
    sns.heatmap(monthly, annot=True, fmt='.1f', cmap='RdYlGn',
                center=0, ax=ax, linewidths=0.5, linecolor='#2E3A4E',
                annot_kws={'color': 'black', 'size': 9})
    ax.tick_params(colors=TEXT)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', color=TEXT)
    ax.set_yticklabels(ax.get_yticklabels(), color=TEXT)
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(colors=TEXT, labelcolor=TEXT)
    plt.title('Monthly Returns Heatmap (%)', color=TEXT, pad=15, fontsize=14)
    plt.tight_layout()
    return fig

# ── 19. Sector Breakdown (Matplotlib) ─────────────────────────────────────────
def sector_breakdown_chart(sector_data, total_value):
    sectors     = list(sector_data.keys())
    values      = list(sector_data.values())
    colors_list = ['#00C896','#00BFFF','#FFA500','#FF69B4','#9370DB',
                   '#FFD700','#FF6347','#20B2AA','#778899','#DDA0DD']
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(BG)
    for ax in axes:
        ax.set_facecolor(BG)
    wedges, texts, autotexts = axes[0].pie(
        values, labels=sectors, autopct='%1.1f%%',
        colors=colors_list[:len(sectors)], startangle=90,
        wedgeprops=dict(width=0.6, edgecolor=BG),
        textprops=dict(color=TEXT)
    )
    for at in autotexts:
        at.set_color('black'); at.set_fontsize(9)
    axes[0].set_title('Sector Allocation', color=TEXT, fontsize=13)
    bars = axes[1].barh(sectors, values, color=colors_list[:len(sectors)], edgecolor=BG)
    axes[1].tick_params(colors=TEXT)
    axes[1].set_xlabel('Value ($)', color=TEXT)
    axes[1].set_title('Sector Value Breakdown', color=TEXT, fontsize=13)
    for bar, val in zip(bars, values):
        axes[1].text(bar.get_width() + max(values)*0.01,
                     bar.get_y() + bar.get_height()/2,
                     f'', va='center', color=TEXT, fontsize=9)
    for spine in axes[1].spines.values():
        spine.set_edgecolor('#2E3A4E')
    plt.tight_layout()
    return fig

# ── 20. Risk vs Return Scatter ────────────────────────────────────────────────
def risk_return_scatter(risk_df, enriched_df):
    if risk_df.empty:
        return go.Figure().update_layout(**LAYOUT)
    merged = risk_df.copy()
    merged['annual_volatility_num'] = merged['annual_volatility'].str.replace('%','').astype(float)
    ret_map = dict(zip(enriched_df['ticker'], enriched_df['return_pct']))
    merged['return_pct'] = merged['ticker'].map(ret_map)
    color_map = {'Low': POSITIVE, 'Medium': '#FFA500', 'High': NEGATIVE}
    fig = go.Figure()
    for risk_level, color in color_map.items():
        sub = merged[merged['risk_level'] == risk_level]
        if not sub.empty:
            fig.add_trace(go.Scatter(
                x=sub['annual_volatility_num'], y=sub['return_pct'],
                mode='markers+text', name=f'{risk_level} Risk',
                text=sub['ticker'], textposition='top center',
                marker=dict(size=14, color=color, opacity=0.85,
                            line=dict(width=1, color='white')),
            ))
    fig.add_hline(y=0, line_dash='dot', line_color='#555')
    fig.update_layout(**LAYOUT, title='Risk vs Return Analysis',
                      xaxis=dict(title='Annual Volatility (%)', gridcolor='#1e2535'),
                      yaxis=dict(title='Total Return (%)', gridcolor='#1e2535'))
    return fig

# ── 21. Invested vs Current (Matplotlib) ─────────────────────────────────────
def invested_vs_current_matplotlib(df):
    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(CARD_BG)
    x     = np.arange(len(df))
    width = 0.35
    bars1 = ax.bar(x - width/2, df['total_invested'], width,
                   label='Invested', color='#4A90D9', edgecolor=BG)
    bars2 = ax.bar(x + width/2, df['current_value'], width,
                   label='Current Value',
                   color=[POSITIVE if v >= i else NEGATIVE
                          for v, i in zip(df['current_value'], df['total_invested'])],
                   edgecolor=BG)
    ax.set_xticks(x)
    ax.set_xticklabels(df['ticker'], color=TEXT, fontsize=11)
    ax.tick_params(colors=TEXT)
    ax.set_ylabel('Value ($)', color=TEXT)
    ax.set_title('Invested vs Current Value per Stock', color=TEXT, fontsize=13)
    ax.legend(facecolor=CARD_BG, labelcolor=TEXT, edgecolor='#2E3A4E')
    for spine in ax.spines.values():
        spine.set_edgecolor('#2E3A4E')
    ax.yaxis.grid(True, color='#1e2535', alpha=0.5)
    ax.set_axisbelow(True)
    plt.tight_layout()
    return fig

# ── 22. Pandas Styled Table ───────────────────────────────────────────────────
def styled_portfolio_table(df):
    display = df[['ticker','total_quantity','avg_buy_price',
                  'current_price','total_invested','current_value',
                  'profit_loss','return_pct','weight']].copy()
    display.columns = ['Ticker','Qty','Buy Price','Curr Price',
                       'Invested','Current Value','P&L','Return %','Weight']
    def color_pnl(val):
        try:
            v = float(str(val).replace('$','').replace(',','').replace('%',''))
            color = '#00C896' if v >= 0 else '#FF4B6E'
            return f'color: {color}; font-weight: bold'
        except:
            return ''
    styled = display.style\
        .format({
            'Buy Price'    : '',
            'Curr Price'   : '',
            'Invested'     : '',
            'Current Value': '',
            'P&L'          : '',
            'Return %'     : '{:+.2f}%',
            'Weight'       : '{:.1f}%',
        })\
        .map(color_pnl, subset=['P&L','Return %'])\
        .set_properties(**{
            'background-color': '#1C2333',
            'color'           : '#E8EDF2',
            'border-color'    : '#2E3A4E',
        })\
        .set_table_styles([{
            'selector': 'th',
            'props'   : [('background-color','#131A27'),
                         ('color','#00C896'),
                         ('font-weight','bold'),
                         ('border','1px solid #2E3A4E')]
        }])
    return styled

# ── 23. Outlier Visualization (Seaborn) ───────────────────────────────────────
def outlier_chart(returns_df):
    if returns_df.empty:
        fig, ax = plt.subplots()
        fig.patch.set_facecolor(BG)
        return fig
    n   = len(returns_df.columns)
    fig, axes = plt.subplots(1, n, figsize=(5*n, 5))
    fig.patch.set_facecolor(BG)
    if n == 1:
        axes = [axes]
    for ax, col in zip(axes, returns_df.columns):
        ax.set_facecolor(CARD_BG)
        data = returns_df[col].dropna()
        sns.violinplot(y=data, ax=ax, color='#6495ED', inner='box')
        Q1  = data.quantile(0.25)
        Q3  = data.quantile(0.75)
        IQR = Q3 - Q1
        ax.axhline(Q3 + 1.5*IQR, color=NEGATIVE, linestyle='--', label='IQR Upper')
        ax.axhline(Q1 - 1.5*IQR, color=NEGATIVE, linestyle='--', label='IQR Lower')
        ax.set_title(f'{col} — Outlier Detection', color=TEXT, fontsize=11)
        ax.tick_params(colors=TEXT, labelcolor=TEXT)
        ax.set_ylabel('Daily Return', color=TEXT)
        for spine in ax.spines.values():
            spine.set_edgecolor('#2E3A4E')
        ax.legend(facecolor=CARD_BG, labelcolor=TEXT, edgecolor='#2E3A4E', fontsize=8)
    plt.suptitle('Outlier Detection — Violin + IQR Bounds', color=TEXT, fontsize=14, y=1.02)
    plt.tight_layout()
    return fig
