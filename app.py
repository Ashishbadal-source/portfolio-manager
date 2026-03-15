import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, date

from auth.auth_handler import init_auth_session, is_logged_in, get_current_user_id, logout_user
from auth.auth_ui import show_auth_page
from database.db_handler import (
    add_stock, get_portfolio, delete_stock, get_portfolio_summary,
    add_to_watchlist, get_watchlist, remove_from_watchlist,
    add_price_alert, get_price_alerts, delete_price_alert
)
from utils.data_handler import (
    fetch_live_prices, fetch_historical_data,
    enrich_portfolio, portfolio_summary_stats, get_returns_matrix
)
from utils.risk_metrics import calculate_all_metrics
from utils.optimizer import run_monte_carlo, get_optimal_portfolio, get_min_volatility_portfolio
from simulations.random_walk import simulate_random_walk, get_confidence_intervals
from simulations.stress_test import run_stress_test
from simulations.whatif import whatif_single_stock, best_worst_case
from utils.insights import get_stock_news, calculate_health_score
from utils.exporter import export_to_excel
from utils.tax_rebalance import calculate_rebalancing, calculate_tax
from components.charts import (
    allocation_pie, profit_loss_bar, return_pct_bar,
    candlestick_chart, portfolio_value_chart,
    correlation_heatmap_seaborn, efficient_frontier_chart,
    random_walk_chart, stress_test_chart, returns_distribution,
    stock_comparison_chart, portfolio_drawdown_chart,
    sector_breakdown_chart, risk_return_scatter,
    invested_vs_current_matplotlib, styled_portfolio_table,
    rolling_returns_heatmap, rsi_chart, macd_chart,
    pair_plot, rolling_stats_chart, rolling_correlation_chart,
    outlier_chart
)

st.set_page_config(
    page_title="Portfolio Manager",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  .stApp, html, body,
  div[data-testid="stAppViewContainer"],
  div[data-testid="stVerticalBlock"],
  section[data-testid="stSidebar"],
  .stMain, .main, .block-container {
      background-color: #0E1117 !important;
      color: #E8EDF2 !important;
  }
  * { color-scheme: dark !important; }
  input, select, textarea,
  .stNumberInput input, .stDateInput input, .stTextInput input {
      background-color: #1C2333 !important;
      color: #E8EDF2 !important;
      border-color: #2E3A4E !important;
  }
  [data-testid="metric-container"] {
      background: #1C2333 !important;
      border: 1px solid #2E3A4E !important;
      border-radius: 12px; padding: 16px 20px;
  }
  [data-testid="metric-container"] label { color: #7B8FA1 !important; font-size: 0.82rem; }
  [data-testid="metric-container"] [data-testid="metric-value"] {
      color: #E8EDF2 !important; font-size: 1.4rem; font-weight: 700;
  }
  .section-header {
      font-size: 1.1rem; font-weight: 600; color: #E8EDF2;
      border-left: 3px solid #00C896; padding-left: 10px; margin: 20px 0 12px;
  }
  .kpi-card {
      background: linear-gradient(135deg, #1C2333, #1a2744);
      border: 1px solid #2E3A4E; border-radius: 16px;
      padding: 20px; text-align: center; margin: 4px;
  }
  .kpi-icon  { font-size: 1.8rem; margin-bottom: 6px; }
  .kpi-label { color: #7B8FA1; font-size: 0.8rem; font-weight: 500; margin-bottom: 4px; }
  .kpi-value { color: #E8EDF2; font-size: 1.5rem; font-weight: 700; }
  .kpi-delta-pos { color: #00C896; font-size: 0.85rem; font-weight: 600; }
  .kpi-delta-neg { color: #FF4B6E; font-size: 0.85rem; font-weight: 600; }
  .health-card {
      background: #1C2333; border-radius: 16px;
      padding: 20px; border: 1px solid #2E3A4E; margin-bottom: 16px;
  }
  .news-card {
      background: #1C2333; border-radius: 10px;
      padding: 14px; border: 1px solid #2E3A4E; margin-bottom: 10px;
  }
  .news-title { color: #E8EDF2; font-size: 0.95rem; font-weight: 600; }
  .news-meta  { color: #7B8FA1; font-size: 0.78rem; margin-top: 4px; }
  .alert-card {
      background: #1C2333; border-radius: 10px;
      padding: 12px; border-left: 4px solid #00C896; margin-bottom: 8px;
  }
  .tax-card {
      background: #1C2333; border-radius: 12px;
      padding: 16px; border: 1px solid #2E3A4E; margin-bottom: 12px;
  }
  .user-badge {
      background: linear-gradient(135deg, #1C2333, #1a2744);
      border: 1px solid #2E3A4E; border-radius: 10px;
      padding: 10px 16px; text-align: center; margin-bottom: 12px;
  }
  [data-testid="stSidebar"] { background: #131A27 !important; }
  header[data-testid="stHeader"] { background-color: #0E1117 !important; }
  footer { visibility: hidden; }
  .stTabs [data-baseweb="tab"] { color: #E8EDF2 !important; }
  .stTabs [data-baseweb="tab-list"] { background-color: #0E1117 !important; }
  [data-testid="stDataFrame"] { background-color: #1C2333 !important; }
  button[aria-label="Use system theme"] { display: none !important; }
  button[aria-label="Use light theme"]  { display: none !important; }
  button[aria-label="Use dark theme"]   { pointer-events: none !important; }
  [data-theme="light"], [data-theme="light"] .stApp,
  [data-theme="light"] html, [data-theme="light"] body,
  [data-theme="light"] .block-container, [data-theme="light"] .main,
  [data-theme="light"] div[data-testid="stAppViewContainer"],
  [data-theme="light"] header,
  [data-theme="light"] section[data-testid="stSidebar"] {
      background-color: #0E1117 !important; color: #E8EDF2 !important;
  }
  [data-theme="light"] div, [data-theme="light"] p,
  [data-theme="light"] span, [data-theme="light"] h1,
  [data-theme="light"] h2, [data-theme="light"] h3,
  [data-theme="light"] h4, [data-theme="light"] label,
  [data-theme="light"] a { color: #E8EDF2 !important; }
  [data-theme="light"] div:not([data-testid="metric-container"]):not([data-testid="stSidebar"]) {
      background-color: #0E1117 !important;
  }
  [data-theme="light"] [data-testid="stSidebar"] { background-color: #131A27 !important; }
  [data-theme="light"] [data-testid="metric-container"] {
      background: #1C2333 !important; border: 1px solid #2E3A4E !important;
  }
  [data-theme="light"] input, [data-theme="light"] select,
  [data-theme="light"] textarea { background-color: #1C2333 !important; color: #E8EDF2 !important; }
  [data-theme="light"] .stTabs [data-baseweb="tab-list"] { background-color: #0E1117 !important; }
  [data-theme="light"] .stTabs [data-baseweb="tab"] { color: #E8EDF2 !important; }
  [data-theme="light"] button { background-color: #1C2333 !important; color: #E8EDF2 !important; }
  [data-theme="light"] .section-header { color: #E8EDF2 !important; }
</style>
""", unsafe_allow_html=True)

# -- Auth Init ------------------------------------------------------------------
init_auth_session()

# -- Show Login Page if not logged in ------------------------------------------
if not is_logged_in():
    show_auth_page()
    st.stop()

# -- Logged in — get user info --------------------------------------------------
user_id  = get_current_user_id()
username = st.session_state.username

# -- Session State Init ─────────────────────────────────────────────────────────
if 'live_prices'  not in st.session_state: st.session_state.live_prices  = {}
if 'enriched_df'  not in st.session_state: st.session_state.enriched_df  = pd.DataFrame()
if 'last_refresh' not in st.session_state: st.session_state.last_refresh = None

# -- Sidebar --------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
    <div class="user-badge">
        <div style="font-size:1.5rem;">👤</div>
        <div style="color:#00C896; font-weight:700; font-size:1rem;">{username}</div>
        <div style="color:#7B8FA1; font-size:0.75rem;">Logged in</div>
    </div>""", unsafe_allow_html=True)

    if st.button("Logout", use_container_width=True):
        logout_user()

    st.markdown("---")
    st.markdown("### Add Stock")
    ticker_input  = st.text_input("Ticker Symbol", placeholder="e.g. AAPL").upper().strip()
    buy_price_inp = st.number_input("Buy Price (USD)", min_value=0.01, value=100.0, step=0.01)
    quantity_inp  = st.number_input("Quantity", min_value=1, value=10, step=1)
    date_inp      = st.date_input("Purchase Date", value=date.today())

    if st.button("Add to Portfolio", use_container_width=True, type="primary"):
        if not ticker_input:
            st.error("Please enter a ticker symbol!")
        else:
            from utils.validator import validate_ticker
            with st.spinner(f"Validating {ticker_input}..."):
                is_valid, message, info = validate_ticker(ticker_input)
            if is_valid:
                add_stock(user_id, ticker_input, buy_price_inp, quantity_inp, str(date_inp))
                st.success(f"Added: {message}")
                if info and info.get('sector'):
                    st.caption(f"Sector: {info['sector']}")
                st.session_state.enriched_df = pd.DataFrame()
            else:
                st.error(f"Invalid Ticker — {message}")
                st.info("US: AAPL, MSFT, TSLA\nIndia: HCLTECH.NS, TCS.NS")

    st.markdown("---")
    st.markdown("### Remove Stock")
    raw_df = get_portfolio(user_id)
    if not raw_df.empty:
        remove_options = raw_df[['id','ticker','quantity']].copy()
        remove_options['label'] = remove_options.apply(
            lambda r: f"{r['ticker']} (qty: {r['quantity']}, id: {r['id']})", axis=1)
        selected_label = st.selectbox("Select to remove", remove_options['label'].tolist())
        selected_id    = int(selected_label.split("id: ")[1].replace(")", ""))
        if st.button("Remove", use_container_width=True):
            delete_stock(user_id, selected_id)
            st.success("Removed!")
            st.session_state.enriched_df = pd.DataFrame()
    else:
        st.info("Portfolio is empty!")

    st.markdown("---")
    st.markdown("### Watchlist")
    watch_ticker = st.text_input("Add to Watchlist", placeholder="e.g. GOOGL").upper().strip()
    if st.button("Add to Watchlist", use_container_width=True):
        if watch_ticker:
            add_to_watchlist(user_id, watch_ticker)
            st.success(f"{watch_ticker} added!")
    watchlist_df = get_watchlist(user_id)
    if not watchlist_df.empty:
        for _, wrow in watchlist_df.iterrows():
            wc1, wc2 = st.columns([3,1])
            with wc1:
                st.write(wrow['ticker'])
            with wc2:
                if st.button("X", key=f"wl_{wrow['id']}"):
                    remove_from_watchlist(user_id, wrow['ticker'])
                    st.rerun()

    st.markdown("---")
    hist_period = st.selectbox("Historical Period", ['1mo','3mo','6mo','1y','2y'], index=3)
    if st.button("Refresh Prices", use_container_width=True):
        st.session_state.enriched_df = pd.DataFrame()
        st.rerun()
    if st.session_state.last_refresh:
        st.caption(f"Last updated: {st.session_state.last_refresh.strftime('%H:%M:%S')}")

# -- Data Load ------------------------------------------------------------------
if st.session_state.enriched_df.empty:
    raw_df = get_portfolio(user_id)
    if not raw_df.empty:
        summary_df   = get_portfolio_summary(user_id)
        tickers_list = summary_df['ticker'].tolist()
        with st.spinner("Fetching live prices..."):
            prices = fetch_live_prices(tickers_list)

        # Agar prices nahi aaye toh buy_price use karo as fallback
        for ticker in tickers_list:
            if ticker not in prices or prices[ticker] is None:
                row = summary_df[summary_df['ticker'] == ticker]
                if not row.empty:
                    prices[ticker] = float(row['avg_buy_price'].values[0])

        st.session_state.live_prices  = prices
        st.session_state.enriched_df  = enrich_portfolio(prices, user_id)
        st.session_state.last_refresh = datetime.now()

enriched_df = st.session_state.enriched_df

# -- Header ---------------------------------------------------------------------
st.markdown(f"# Live Portfolio Manager Dashboard")
st.markdown(f"*{datetime.now().strftime('%A, %d %B %Y')}* &nbsp;|&nbsp; Welcome, **{username}**")
st.markdown("---")

if enriched_df.empty:
    st.info("Add stocks from the sidebar to get started!")
    st.stop()

summary    = portfolio_summary_stats(enriched_df)
valid_df   = enriched_df.dropna(subset=['current_value'])
tickers    = valid_df['ticker'].tolist()
quantities = dict(zip(valid_df['ticker'], valid_df['total_quantity']))
buy_prices = dict(zip(valid_df['ticker'], valid_df['avg_buy_price']))

total_invested = summary.get('total_invested', 0)
total_value    = summary.get('total_value', 0)
total_profit   = summary.get('total_profit', 0)
total_return   = summary.get('total_return_pct', 0)
delta_val      = total_value - total_invested

# -- KPI Cards ------------------------------------------------------------------
st.markdown('<div class="section-header">Portfolio Summary</div>', unsafe_allow_html=True)
c1,c2,c3,c4,c5,c6 = st.columns(6)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">💼</div>
        <div class="kpi-label">Total Invested</div>
        <div class="kpi-value">${total_invested:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    delta_class = 'kpi-delta-pos' if delta_val >= 0 else 'kpi-delta-neg'
    delta_sign  = '+' if delta_val >= 0 else ''
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📈</div>
        <div class="kpi-label">Portfolio Value</div>
        <div class="kpi-value">${total_value:,.0f}</div>
        <div class="{delta_class}">{delta_sign}${delta_val:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    pnl_class = 'kpi-delta-pos' if total_profit >= 0 else 'kpi-delta-neg'
    pnl_sign  = '+' if total_profit >= 0 else ''
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Total P&L</div>
        <div class="kpi-value {pnl_class}">{pnl_sign}${total_profit:,.0f}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    ret_class = 'kpi-delta-pos' if total_return >= 0 else 'kpi-delta-neg'
    ret_sign  = '+' if total_return >= 0 else ''
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📊</div>
        <div class="kpi-label">Total Return</div>
        <div class="kpi-value {ret_class}">{ret_sign}{total_return:.2f}%</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">🏆</div>
        <div class="kpi-label">Best Stock</div>
        <div class="kpi-value" style="color:#00C896">{summary.get('best_stock','-')}</div>
    </div>""", unsafe_allow_html=True)

with c6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon">📉</div>
        <div class="kpi-label">Worst Stock</div>
        <div class="kpi-value" style="color:#FF4B6E">{summary.get('worst_stock','-')}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# -- Price Alerts Check --------------------------------------------------------
alerts_df = get_price_alerts(user_id)
if not alerts_df.empty and not valid_df.empty:
    for _, alert in alerts_df.iterrows():
        row = valid_df[valid_df['ticker'] == alert['ticker']]
        if row.empty:
            continue
        current = float(row['current_price'].values[0])
        target  = float(alert['target_price'])
        if alert['alert_type'] == 'above' and current >= target:
            st.success(f"ALERT: {alert['ticker']} hit ${current:.2f} — above target ${target:.2f}")
        elif alert['alert_type'] == 'below' and current <= target:
            st.warning(f"ALERT: {alert['ticker']} hit ${current:.2f} — below target ${target:.2f}")

# -- Tabs -----------------------------------------------------------------------
tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9 = st.tabs([
    "Holdings", "Analytics", "Price Trends", "Risk Metrics",
    "Optimization", "Simulations", "Data Analysis", "Insights", "Tax & Rebalance"
])

# -- Tab 1: Holdings ------------------------------------------------------------
with tab1:
    st.markdown('<div class="section-header">Current Holdings</div>', unsafe_allow_html=True)
    display = valid_df.copy()
    display['Invested']      = display['total_invested'].map('${:,.2f}'.format)
    display['Current Value'] = display['current_value'].map('${:,.2f}'.format)
    display['Buy Price']     = display['avg_buy_price'].map('${:,.2f}'.format)
    display['Curr Price']    = display['current_price'].map('${:,.2f}'.format)
    display['P&L']           = display['profit_loss'].map('${:+,.2f}'.format)
    display['Return %']      = display['return_pct'].map('{:+.2f}%'.format)
    display['Weight']        = display['weight'].map('{:.1f}%'.format)
    st.dataframe(
        display[['ticker','total_quantity','Buy Price','Curr Price',
                 'Invested','Current Value','P&L','Return %','Weight']].rename(
            columns={'ticker':'Ticker','total_quantity':'Qty'}),
        use_container_width=True, hide_index=True)
    st.markdown("---")
    excel_data = export_to_excel(valid_df, summary)
    st.download_button(
        label="Download Portfolio as Excel",
        data=excel_data,
        file_name=f"portfolio_{username}_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.plotly_chart(
        portfolio_value_chart(tickers, quantities, buy_prices, hist_period),
        use_container_width=True, key='portval')
    st.markdown('<div class="section-header">Portfolio Drawdown</div>', unsafe_allow_html=True)
    st.plotly_chart(
        portfolio_drawdown_chart(tickers, quantities, hist_period),
        use_container_width=True, key='drawdown')

# -- Tab 2: Analytics -----------------------------------------------------------
with tab2:
    st.markdown('<div class="section-header">Portfolio Allocation & P&L</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.plotly_chart(allocation_pie(valid_df), use_container_width=True, key='pie')
    with c2:
        st.plotly_chart(profit_loss_bar(valid_df), use_container_width=True, key='plbar')
    st.markdown('<div class="section-header">Returns & Investment Comparison</div>', unsafe_allow_html=True)
    st.plotly_chart(return_pct_bar(valid_df), use_container_width=True, key='retbar')
    st.pyplot(invested_vs_current_matplotlib(valid_df))
    st.markdown('<div class="section-header">Stock Performance Comparison</div>', unsafe_allow_html=True)
    with st.spinner("Loading..."):
        st.plotly_chart(stock_comparison_chart(tickers, hist_period),
                        use_container_width=True, key='stockcomp')
    st.markdown('<div class="section-header">Sector Distribution</div>', unsafe_allow_html=True)
    with st.spinner("Fetching sector data..."):
        sector_values = {}
        for _, row in valid_df.iterrows():
            try:
                info   = yf.Ticker(row['ticker']).info
                sector = info.get('sector', 'Unknown')
            except:
                sector = 'Unknown'
            sector_values[sector] = sector_values.get(sector, 0) + row['current_value']
    st.pyplot(sector_breakdown_chart(sector_values, valid_df['current_value'].sum()))
    st.markdown('<div class="section-header">Returns Distribution</div>', unsafe_allow_html=True)
    sel_ticker = st.selectbox("Select Stock", tickers, key='dist_sel')
    with st.spinner("Loading..."):
        returns_df = get_returns_matrix(tickers, hist_period)
    if not returns_df.empty:
        st.pyplot(returns_distribution(returns_df, sel_ticker))
    st.markdown('<div class="section-header">Monthly Returns Heatmap</div>', unsafe_allow_html=True)
    if not returns_df.empty:
        st.pyplot(rolling_returns_heatmap(returns_df))
    st.markdown('<div class="section-header">Portfolio Detail Table</div>', unsafe_allow_html=True)
    st.dataframe(styled_portfolio_table(valid_df), use_container_width=True, hide_index=True)

# -- Tab 3: Price Trends --------------------------------------------------------
with tab3:
    sel = st.selectbox("Select Stock", tickers, key='trend_sel')
    with st.spinner(f"Loading {sel}..."):
        hist = fetch_historical_data(sel, hist_period)
    st.plotly_chart(candlestick_chart(hist, sel), use_container_width=True, key='candle')
    if not hist.empty:
        m1,m2,m3,m4 = st.columns(4)
        m1.metric("52W High",      f"${hist['Close'].max():,.2f}")
        m2.metric("52W Low",       f"${hist['Close'].min():,.2f}")
        m3.metric("Avg Volume",    f"{hist['Volume'].mean():,.0f}")
        period_ret = (hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0] * 100
        m4.metric("Period Return", f"{period_ret:+.2f}%")
    st.markdown('<div class="section-header">RSI — Relative Strength Index</div>', unsafe_allow_html=True)
    if not hist.empty:
        st.plotly_chart(rsi_chart(hist['Close'], sel), use_container_width=True, key='rsi')
    st.markdown('<div class="section-header">MACD Indicator</div>', unsafe_allow_html=True)
    if not hist.empty:
        st.plotly_chart(macd_chart(hist['Close'], sel), use_container_width=True, key='macd')

# -- Tab 4: Risk Metrics --------------------------------------------------------
with tab4:
    st.markdown('<div class="section-header">Risk Metrics</div>', unsafe_allow_html=True)
    with st.spinner("Calculating..."):
        risk_df = calculate_all_metrics(tickers, hist_period)
    if not risk_df.empty:
        st.dataframe(risk_df, use_container_width=True, hide_index=True)
        st.plotly_chart(risk_return_scatter(risk_df, valid_df),
                        use_container_width=True, key='riskret')
    st.markdown('<div class="section-header">Correlation Matrix</div>', unsafe_allow_html=True)
    if len(tickers) >= 2:
        with st.spinner("Computing..."):
            returns_df = get_returns_matrix(tickers, hist_period)
        if not returns_df.empty:
            st.pyplot(correlation_heatmap_seaborn(returns_df.corr()))
    else:
        st.info("Add at least 2 stocks!")

# -- Tab 5: Optimization --------------------------------------------------------
with tab5:
    st.markdown('<div class="section-header">Efficient Frontier — Monte Carlo</div>', unsafe_allow_html=True)
    if len(tickers) >= 2:
        with st.spinner("Simulating 10,000 portfolios..."):
            mc_df   = run_monte_carlo(tickers, hist_period, 10000)
            optimal = get_optimal_portfolio(mc_df, tickers)
            min_vol = get_min_volatility_portfolio(mc_df, tickers)
        st.plotly_chart(efficient_frontier_chart(mc_df, optimal, min_vol),
                        use_container_width=True, key='frontier')
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("#### Max Sharpe Portfolio")
            if optimal:
                for t,w in zip(optimal['tickers'], optimal['weights']):
                    st.write(f"**{t}**: {w}%")
                st.metric("Expected Return", f"{optimal['expected_return']:.2f}%")
                st.metric("Expected Risk",   f"{optimal['expected_risk']:.2f}%")
                st.metric("Sharpe Ratio",    f"{optimal['sharpe_ratio']:.3f}")
        with c2:
            st.markdown("#### Min Volatility Portfolio")
            if min_vol:
                for t,w in zip(min_vol['tickers'], min_vol['weights']):
                    st.write(f"**{t}**: {w}%")
                st.metric("Expected Return", f"{min_vol['expected_return']:.2f}%")
                st.metric("Expected Risk",   f"{min_vol['expected_risk']:.2f}%")
                st.metric("Sharpe Ratio",    f"{min_vol['sharpe_ratio']:.3f}")
    else:
        st.info("Add at least 2 stocks!")

# -- Tab 6: Simulations ---------------------------------------------------------
with tab6:
    sim_tab1, sim_tab2, sim_tab3 = st.tabs(["Random Walk", "Stress Test", "What-If"])

    with sim_tab1:
        st.markdown('<div class="section-header">Random Walk — GBM</div>', unsafe_allow_html=True)
        rw_ticker = st.selectbox("Select Stock", tickers, key='rw_sel')
        rw_days   = st.slider("Simulation Days", 30, 180, 90)
        rw_sims   = st.slider("Simulations", 50, 500, 100)
        if st.button("Run Simulation", key='rw_btn'):
            with st.spinner("Simulating..."):
                paths_df = simulate_random_walk(rw_ticker, rw_days, rw_sims, hist_period)
                ci_df    = get_confidence_intervals(paths_df)
            st.plotly_chart(random_walk_chart(paths_df, ci_df, rw_ticker),
                            use_container_width=True, key='rndwalk')

    with sim_tab2:
        st.markdown('<div class="section-header">Stress Testing</div>', unsafe_allow_html=True)
        custom_name = st.text_input("Scenario Name", placeholder="e.g. Market Crash 2025")
        custom_pct  = st.slider("Market Change %", -60, +60, -15)
        with st.spinner("Running..."):
            stress_df = run_stress_test(valid_df, custom_pct,
                                        custom_name if custom_name else None)
        if not stress_df.empty:
            st.plotly_chart(stress_test_chart(stress_df), use_container_width=True, key='stress')
            st.dataframe(stress_df, use_container_width=True, hide_index=True)

    with sim_tab3:
        st.markdown('<div class="section-header">What-If Analysis</div>', unsafe_allow_html=True)
        wi_ticker = st.selectbox("Select Stock", tickers, key='wi_sel')
        wi_change = st.slider("Price Change %", -50, +100, 10)
        result    = whatif_single_stock(valid_df, wi_ticker, wi_change)
        if result:
            w1,w2,w3 = st.columns(3)
            w1.metric("Old Portfolio", f"${result['old_portfolio_value']:,.2f}")
            w2.metric("New Portfolio", f"${result['new_portfolio_value']:,.2f}",
                      delta=f"${result['portfolio_impact']:+,.2f}")
            w3.metric("New Return %",  f"{result['new_return_pct']:+.2f}%")
        bwc = best_worst_case(valid_df)
        if bwc:
            st.markdown("#### Best vs Worst Case")
            b1,b2,b3 = st.columns(3)
            b1.metric("Current",               f"${bwc['current_value']:,.2f}")
            b2.metric(f"Bull +{bwc['bull_pct']}%", f"${bwc['bull_value']:,.2f}",
                      delta=f"{bwc['bull_return']:+.2f}%")
            b3.metric(f"Bear {bwc['bear_pct']}%",  f"${bwc['bear_value']:,.2f}",
                      delta=f"{bwc['bear_return']:+.2f}%")

# -- Tab 7: Data Analysis -------------------------------------------------------
with tab7:
    da1, da2, da3, da4 = st.tabs([
        "Descriptive Stats", "Data Quality", "Outlier Detection", "Rolling Stats"
    ])

    with da1:
        st.markdown('<div class="section-header">Descriptive Statistics</div>', unsafe_allow_html=True)
        st.caption("Mean, Median, Std, Skewness, Kurtosis — NumPy + Pandas")
        from utils.analytics import get_descriptive_stats
        with st.spinner("Computing statistics..."):
            ret_df = get_returns_matrix(tickers, hist_period)
        if not ret_df.empty:
            desc_stats = get_descriptive_stats(ret_df)
            st.dataframe(desc_stats, use_container_width=True)

    with da2:
        st.markdown('<div class="section-header">Data Quality Report</div>', unsafe_allow_html=True)
        st.caption("Missing values, duplicates, dtypes — Data Cleaning concept")
        from utils.analytics import get_data_quality_report
        raw_port = get_portfolio(user_id)
        if not raw_port.empty:
            report = get_data_quality_report(valid_df, raw_port)
            st.markdown("#### Shape & Memory")
            q1,q2 = st.columns(2)
            q1.metric("Rows × Columns", f"{report['shape'][0]} × {report['shape'][1]}")
            q2.metric("Memory Usage",   report['memory'])
            st.markdown("#### Data Types")
            st.dataframe(report['dtypes'], use_container_width=True, hide_index=True)
            st.markdown("#### Missing Values")
            st.dataframe(report['missing'], use_container_width=True, hide_index=True)
            st.markdown("#### Duplicate Check")
            dup = report['duplicates']
            d1,d2,d3 = st.columns(3)
            d1.metric("Total Entries",   dup['total_entries'])
            d2.metric("Duplicate Rows",  dup['duplicate_rows'])
            d3.metric("Unique Tickers",  dup['unique_tickers'])

    with da3:
        st.markdown('<div class="section-header">Outlier Detection</div>', unsafe_allow_html=True)
        st.caption("IQR Method + Z-Score Method")
        from utils.analytics import detect_outliers
        with st.spinner("Detecting outliers..."):
            ret_df     = get_returns_matrix(tickers, hist_period)
            iqr_df, z_df = detect_outliers(ret_df)
        if not iqr_df.empty:
            st.markdown("#### IQR Method")
            st.dataframe(iqr_df, use_container_width=True, hide_index=True)
            st.markdown("#### Z-Score Method (|Z| > 3)")
            st.dataframe(z_df, use_container_width=True, hide_index=True)
            st.markdown("#### Violin Plot — Visual Outlier Detection")
            st.pyplot(outlier_chart(ret_df))
        if len(tickers) >= 2:
            st.markdown("#### Pair Plot — Seaborn")
            st.caption("Scatter matrix of all stock returns")
            with st.spinner("Generating pair plot..."):
                st.pyplot(pair_plot(ret_df))

    with da4:
        st.markdown('<div class="section-header">Rolling Statistics</div>', unsafe_allow_html=True)
        st.caption("Rolling mean, std, correlation — Pandas")
        roll_ticker = st.selectbox("Select Stock", tickers, key='roll_sel')
        roll_window = st.slider("Rolling Window (days)", 10, 90, 30)
        with st.spinner("Computing..."):
            ret_df = get_returns_matrix(tickers, hist_period)
        if not ret_df.empty:
            st.plotly_chart(
                rolling_stats_chart(ret_df, roll_ticker, roll_window),
                use_container_width=True, key='rollstats')
        if len(tickers) >= 2:
            st.plotly_chart(
                rolling_correlation_chart(ret_df, roll_window),
                use_container_width=True, key='rollcorr')

# -- Tab 8: Insights ------------------------------------------------------------
with tab8:
    ins1, ins2, ins3 = st.tabs(["Health Score", "News Feed", "Price Alerts"])

    with ins1:
        st.markdown('<div class="section-header">Portfolio Health Score</div>', unsafe_allow_html=True)
        with st.spinner("Calculating..."):
            risk_df_h = calculate_all_metrics(tickers, hist_period)
            score, reasons, warnings_list = calculate_health_score(valid_df, risk_df_h)
        if score >= 75:   color, emoji = '#00C896', '🟢'
        elif score >= 50: color, emoji = '#FFA500', '🟡'
        else:             color, emoji = '#FF4B6E', '🔴'
        st.markdown(f"""
        <div class="health-card" style="text-align:center;">
            <div style="font-size:3rem;">{emoji}</div>
            <div style="font-size:2.5rem; font-weight:800; color:{color};">{score}/100</div>
            <div style="color:#7B8FA1; font-size:0.9rem;">Portfolio Health Score</div>
        </div>""", unsafe_allow_html=True)
        if reasons:
            st.markdown("#### Strengths")
            for r in reasons: st.success(f"✅ {r}")
        if warnings_list:
            st.markdown("#### Warnings")
            for w in warnings_list: st.warning(f"⚠️ {w}")
        st.markdown('<div class="section-header">Stock Info</div>', unsafe_allow_html=True)
        for ticker in tickers:
            try:
                info   = yf.Ticker(ticker).info
                name   = info.get('longName', ticker)
                sector = info.get('sector', 'N/A')
                pe     = info.get('trailingPE', None)
                beta   = info.get('beta', None)
                mc     = info.get('marketCap', None)
                low52  = info.get('fiftyTwoWeekLow', None)
                high52 = info.get('fiftyTwoWeekHigh', None)
            except:
                name = ticker; sector = 'N/A'; pe = None; beta = None; mc = None; low52 = None; high52 = None
            with st.expander(f"{ticker} — {name}"):
                i1,i2,i3,i4,i5 = st.columns(5)
                i1.metric("Sector",     sector)
                i2.metric("P/E Ratio",  f"{pe:.1f}"       if pe    else "N/A")
                i3.metric("Beta",       f"{beta:.2f}"      if beta  else "N/A")
                i4.metric("Market Cap", f"${mc/1e9:.1f}B"  if mc    else "N/A")
                i5.metric("52W Range",  f"${low52:.0f} - ${high52:.0f}" if low52 and high52 else "N/A")

    with ins2:
        st.markdown('<div class="section-header">Latest News</div>', unsafe_allow_html=True)
        news_ticker = st.selectbox("Select Stock", tickers, key='news_sel')
        with st.spinner(f"Fetching {news_ticker} news..."):
            news_items = get_stock_news(news_ticker, max_news=8)
        if news_items:
            for item in news_items:
                st.markdown(f"""
                <div class="news-card">
                    <div class="news-title">
                        <a href="{item['link']}" target="_blank" style="color:#E8EDF2; text-decoration:none;">
                            {item['title']}
                        </a>
                    </div>
                    <div class="news-meta">{item['publisher']} | {item['time']}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No news found.")

    with ins3:
        st.markdown('<div class="section-header">Price Alerts</div>', unsafe_allow_html=True)
        a1,a2,a3 = st.columns(3)
        with a1: alert_ticker = st.selectbox("Stock", tickers, key='alert_sel')
        with a2: alert_target = st.number_input("Target ($)", min_value=0.01, value=100.0)
        with a3: alert_type   = st.selectbox("Type", ["above","below"], key='alert_type')
        if st.button("Set Alert", type="primary"):
            add_price_alert(user_id, alert_ticker, alert_target, alert_type)
            st.success(f"Alert set: {alert_ticker} {alert_type} ${alert_target:.2f}")
            st.rerun()
        alerts_df = get_price_alerts(user_id)
        if not alerts_df.empty:
            st.markdown("#### Active Alerts")
            for _, alert in alerts_df.iterrows():
                ac1,ac2 = st.columns([4,1])
                with ac1:
                    st.markdown(f"""
                    <div class="alert-card">
                        <b>{alert['ticker']}</b> — {alert['alert_type'].upper()}
                        <b>${alert['target_price']:.2f}</b>
                    </div>""", unsafe_allow_html=True)
                with ac2:
                    if st.button("Remove", key=f"del_{alert['id']}"):
                        delete_price_alert(user_id, alert['id'])
                        st.rerun()
        else:
            st.info("No active alerts!")

# -- Tab 9: Tax & Rebalance -----------------------------------------------------
with tab9:
    tax_tab, rebal_tab = st.tabs(["Tax Calculator", "Rebalancing"])

    with tax_tab:
        st.markdown('<div class="section-header">Capital Gains Tax Estimate</div>', unsafe_allow_html=True)
        t1,t2 = st.columns(2)
        with t1: short_rate = st.slider("Short Term Tax Rate (%)", 10, 40, 30)
        with t2: long_rate  = st.slider("Long Term Tax Rate (%)",   5, 30, 15)
        tax_df, tax_summary = calculate_tax(valid_df, short_rate, long_rate)
        if not tax_df.empty:
            s1,s2,s3,s4 = st.columns(4)
            s1.metric("Short Term Gains", f"${tax_summary['total_short_gain']:,.2f}")
            s2.metric("Long Term Gains",  f"${tax_summary['total_long_gain']:,.2f}")
            s3.metric("Total Tax Due",    f"${tax_summary['total_tax']:,.2f}",
                      delta=f"-${tax_summary['total_tax']:,.2f}", delta_color="inverse")
            s4.metric("Net After Tax",    f"${tax_summary['net_after_tax']:,.2f}")
            st.dataframe(tax_df, use_container_width=True, hide_index=True)
            st.markdown(f"""
            <div class="tax-card">
                Short Term Tax ({short_rate}%): <b style="color:#FF4B6E">${tax_summary['total_short_tax']:,.2f}</b><br>
                Long Term Tax ({long_rate}%): <b style="color:#FFA500">${tax_summary['total_long_tax']:,.2f}</b><br>
                <hr style="border-color:#2E3A4E">
                Total Tax: <b style="color:#FF4B6E">${tax_summary['total_tax']:,.2f}</b><br>
                Net Profit After Tax: <b style="color:#00C896">${tax_summary['net_after_tax']:,.2f}</b>
            </div>""", unsafe_allow_html=True)

    with rebal_tab:
        st.markdown('<div class="section-header">Rebalancing Suggestions</div>', unsafe_allow_html=True)
        n = len(tickers)
        equal_weight = round(100/n, 1)
        target_weights = {}
        cols = st.columns(min(n, 4))
        for i, ticker in enumerate(tickers):
            with cols[i % min(n, 4)]:
                target_weights[ticker] = st.number_input(
                    f"{ticker} (%)", min_value=0.0, max_value=100.0,
                    value=equal_weight, step=0.5, key=f"tw_{ticker}")
        total_target = sum(target_weights.values())
        if abs(total_target - 100) > 1:
            st.warning(f"Weights sum = {total_target:.1f}% — should be 100%")
        else:
            st.success(f"Weights sum = {total_target:.1f}% ✅")
        rebal_df = calculate_rebalancing(valid_df, target_weights)
        if not rebal_df.empty:
            for _, row in rebal_df.iterrows():
                action = row['action']
                color  = '#00C896' if action=='Buy' else '#FF4B6E' if action=='Sell' else '#888'
                icon   = '📈' if action=='Buy' else '📉' if action=='Sell' else '⏸️'
                st.markdown(f"""
                <div class="alert-card" style="border-left-color:{color};">
                    {icon} <b style="color:{color};">{action} {row['ticker']}</b> —
                    {row['shares_to_trade']} shares (${abs(row['diff_value']):,.2f}) |
                    {row['current_weight']}% → {row['target_weight']}%
                </div>""", unsafe_allow_html=True)
            st.dataframe(rebal_df, use_container_width=True, hide_index=True)

# -- Footer ---------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#4A5568;font-size:0.8rem;'>"
    "Live Portfolio Manager | Python | Streamlit | Supabase | yfinance | Plotly | Seaborn | Matplotlib | Pandas"
    "</div>",
    unsafe_allow_html=True
)