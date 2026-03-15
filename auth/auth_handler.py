import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

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

def signup_user(username: str, email: str, password: str):
    try:
        supabase = get_supabase()

        # Supabase built-in auth se signup
        result = supabase.auth.sign_up({
            'email'   : email,
            'password': password,
            'options' : {'data': {'username': username}}
        })

        if result.user:
            # Custom users table mein bhi save karo username ke liye
            supabase.table('users').insert({
                'id'      : result.user.id,
                'username': username,
                'email'   : email,
                'password': 'managed_by_supabase',
            }).execute()
            return True, "Account created! Please check your email to verify."
        return False, "Signup failed. Try again!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(email: str, password: str):
    try:
        supabase = get_supabase()
        result   = supabase.auth.sign_in_with_password({
            'email'   : email,
            'password': password,
        })
        if result.user:
            # Username fetch karo users table se
            user_data = supabase.table('users').select('username').eq(
                'id', result.user.id).execute()
            username = user_data.data[0]['username'] if user_data.data else email.split('@')[0]
            return True, "Login successful!", {
                'id'      : result.user.id,
                'email'   : result.user.email,
                'username': username,
            }
        return False, "Login failed!", None
    except Exception as e:
        error = str(e)
        if 'Email not confirmed' in error:
            return False, "Please verify your email first!", None
        elif 'Invalid login credentials' in error:
            return False, "Invalid email or password!", None
        return False, f"Error: {error}", None

def logout_user():
    try:
        supabase = get_supabase()
        supabase.auth.sign_out()
    except:
        pass
    st.session_state.logged_in = False
    st.session_state.user      = None
    st.session_state.user_id   = None
    st.session_state.username  = None
    st.rerun()

def is_logged_in():
    return st.session_state.get('logged_in', False)

def get_current_user_id():
    return st.session_state.get('user_id', None)

def init_auth_session():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user'       not in st.session_state: st.session_state.user      = None
    if 'user_id'    not in st.session_state: st.session_state.user_id   = None
    if 'username'   not in st.session_state: st.session_state.username  = None
