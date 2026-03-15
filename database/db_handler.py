import os
import streamlit as st
from supabase import create_client
import pandas as pd

try:
    SUPABASE_URL = st.secrets['SUPABASE_URL']
    SUPABASE_KEY = st.secrets['SUPABASE_KEY']
except:
    from dotenv import load_dotenv
    load_dotenv()
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def add_stock(user_id, ticker, buy_price, quantity, purchase_date):
    try:
        supabase = get_supabase()
        supabase.table('portfolio').insert({
            'user_id'      : user_id,
            'ticker'       : ticker.upper().strip(),
            'buy_price'    : buy_price,
            'quantity'     : quantity,
            'purchase_date': purchase_date,
        }).execute()
        return True
    except Exception as e:
        print(f"Add stock error: {e}")
        return False

def get_portfolio(user_id):
    try:
        supabase = get_supabase()
        result   = supabase.table('portfolio').select('*').eq('user_id', user_id).execute()
        return pd.DataFrame(result.data) if result.data else pd.DataFrame()
    except Exception as e:
        print(f"Get portfolio error: {e}")
        return pd.DataFrame()

def delete_stock(user_id, stock_id):
    try:
        supabase = get_supabase()
        supabase.table('portfolio').delete()\
            .eq('id', stock_id).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Delete stock error: {e}")
        return False

def get_portfolio_summary(user_id):
    try:
        df = get_portfolio(user_id)
        if df.empty:
            return pd.DataFrame()
        df['quantity']  = pd.to_numeric(df['quantity'],  errors='coerce').fillna(0)
        df['buy_price'] = pd.to_numeric(df['buy_price'], errors='coerce').fillna(0)
        agg = df.groupby('ticker').agg(
            total_quantity =('quantity',  'sum'),
            avg_buy_price  =('buy_price', 'mean'),
            total_invested =('buy_price', lambda x: (x * df.loc[x.index, 'quantity']).sum()),
            first_purchase =('purchase_date', 'min'),
        ).reset_index()
        return agg
    except Exception as e:
        print(f"Portfolio summary error: {e}")
        return pd.DataFrame()

def add_to_watchlist(user_id, ticker):
    try:
        supabase = get_supabase()
        supabase.table('watchlist').upsert({
            'user_id': user_id,
            'ticker' : ticker.upper().strip(),
        }).execute()
        return True
    except Exception as e:
        print(f"Watchlist error: {e}")
        return False

def get_watchlist(user_id):
    try:
        supabase = get_supabase()
        result   = supabase.table('watchlist').select('*').eq('user_id', user_id).execute()
        return pd.DataFrame(result.data) if result.data else pd.DataFrame()
    except Exception as e:
        print(f"Get watchlist error: {e}")
        return pd.DataFrame()

def remove_from_watchlist(user_id, ticker):
    try:
        supabase = get_supabase()
        supabase.table('watchlist').delete()\
            .eq('user_id', user_id).eq('ticker', ticker).execute()
        return True
    except Exception as e:
        print(f"Remove watchlist error: {e}")
        return False

def add_price_alert(user_id, ticker, target_price, alert_type):
    try:
        supabase = get_supabase()
        supabase.table('price_alerts').insert({
            'user_id'     : user_id,
            'ticker'      : ticker.upper().strip(),
            'target_price': target_price,
            'alert_type'  : alert_type,
        }).execute()
        return True
    except Exception as e:
        print(f"Add alert error: {e}")
        return False

def get_price_alerts(user_id):
    try:
        supabase = get_supabase()
        result   = supabase.table('price_alerts').select('*').eq('user_id', user_id).execute()
        return pd.DataFrame(result.data) if result.data else pd.DataFrame()
    except Exception as e:
        print(f"Get alerts error: {e}")
        return pd.DataFrame()

def delete_price_alert(user_id, alert_id):
    try:
        supabase = get_supabase()
        supabase.table('price_alerts').delete()\
            .eq('id', alert_id).eq('user_id', user_id).execute()
        return True
    except Exception as e:
        print(f"Delete alert error: {e}")
        return False