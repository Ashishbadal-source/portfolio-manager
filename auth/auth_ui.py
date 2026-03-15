import streamlit as st
from auth.auth_handler import signup_user, login_user

def show_auth_page():
    st.markdown("""
    <style>
      .stApp, html, body { background-color: #0E1117 !important; color: #E8EDF2 !important; }
      * { color-scheme: dark !important; }
      input { background-color: #1C2333 !important; color: #E8EDF2 !important; }
      [data-testid="stSidebar"] { background: #131A27 !important; }
      footer { visibility: hidden; }
      button[aria-label="Use system theme"] { display: none !important; }
      button[aria-label="Use light theme"]  { display: none !important; }
      .auth-title {
          text-align: center; font-size: 2.2rem;
          font-weight: 800; color: #E8EDF2; margin-bottom: 8px;
      }
      .auth-subtitle {
          text-align: center; color: #7B8FA1;
          font-size: 0.9rem; margin-bottom: 32px;
      }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="auth-title">Portfolio Manager</div>
        <div class="auth-subtitle">Track your investments in real-time</div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

        with tab_login:
            st.markdown("#### Welcome Back!")
            login_email    = st.text_input("Email", placeholder="Enter your email", key="login_email")
            login_password = st.text_input("Password", placeholder="Enter your password",
                                           type="password", key="login_pass")
            if st.button("Login", use_container_width=True, type="primary", key="login_btn"):
                if not login_email or not login_password:
                    st.error("Please fill all fields!")
                else:
                    with st.spinner("Logging in..."):
                        success, message, user = login_user(login_email, login_password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user      = user
                        st.session_state.user_id   = user['id']
                        st.session_state.username  = user['username']
                        # Cookie set karo session persist ke liye
                        try:
                            import extra_streamlit_components as stx
                            cookie_manager = stx.CookieManager(key='login_cookies')
                            cookie_manager.set('pm_user_id',  user['id'],       key='set_uid')
                            cookie_manager.set('pm_username', user['username'],  key='set_uname')
                        except:
                            pass
                        st.success(f"Welcome, {user['username']}!")
                        st.rerun()
                    else:
                        st.error(message)

        with tab_signup:
            st.markdown("#### Create Account")
            signup_username = st.text_input("Username", placeholder="Choose a username", key="signup_user")
            signup_email    = st.text_input("Email",    placeholder="Enter your email",   key="signup_email")
            signup_password = st.text_input("Password", placeholder="Choose a strong password",
                                            type="password", key="signup_pass")
            signup_confirm  = st.text_input("Confirm Password", placeholder="Confirm your password",
                                            type="password", key="signup_confirm")
            if st.button("Create Account", use_container_width=True, type="primary", key="signup_btn"):
                if not all([signup_username, signup_email, signup_password, signup_confirm]):
                    st.error("Please fill all fields!")
                elif len(signup_password) < 6:
                    st.error("Password must be at least 6 characters!")
                elif signup_password != signup_confirm:
                    st.error("Passwords do not match!")
                elif '@' not in signup_email:
                    st.error("Please enter a valid email!")
                else:
                    with st.spinner("Creating account..."):
                        success, message = signup_user(
                            signup_username, signup_email, signup_password)
                    if success:
                        st.success(message)
                        st.info("Account created! Please login now.")
                    else:
                        st.error(message)