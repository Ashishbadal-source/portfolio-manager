# import streamlit as st
# from auth.auth_handler import signup_user, login_user

# def show_auth_page():
#     st.markdown("""
#     <style>
#       .stApp, html, body { background-color: #0E1117 !important; color: #E8EDF2 !important; }
#       * { color-scheme: dark !important; }
#       input { background-color: #1C2333 !important; color: #E8EDF2 !important; }
#       [data-testid="stSidebar"] { background: #131A27 !important; }
#       footer { visibility: hidden; }
#       button[aria-label="Use system theme"] { display: none !important; }
#       button[aria-label="Use light theme"]  { display: none !important; }
#       .auth-title {
#           text-align: center; font-size: 2.2rem;
#           font-weight: 800; color: #E8EDF2; margin-bottom: 8px;
#       }
#       .auth-subtitle {
#           text-align: center; color: #7B8FA1;
#           font-size: 0.9rem; margin-bottom: 32px;
#       }
#     </style>
#     """, unsafe_allow_html=True)

#     col1, col2, col3 = st.columns([1, 2, 1])
#     with col2:
#         st.markdown("""
#         <div class="auth-title">Portfolio Manager</div>
#         <div class="auth-subtitle">Track your investments in real-time</div>
#         """, unsafe_allow_html=True)

#         tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

#         with tab_login:
#             st.markdown("#### Welcome Back!")
#             login_email    = st.text_input("Email", placeholder="Enter your email", key="login_email")
#             login_password = st.text_input("Password", placeholder="Enter your password",
#                                            type="password", key="login_pass")
#             if st.button("Login", use_container_width=True, type="primary", key="login_btn"):
#                 if not login_email or not login_password:
#                     st.error("Please fill all fields!")
#                 else:
#                     with st.spinner("Logging in..."):
#                         success, message, user = login_user(login_email, login_password)
#                     if success:
#                         st.session_state.logged_in = True
#                         st.session_state.user      = user
#                         st.session_state.user_id   = user['id']
#                         st.session_state.username  = user['username']
#                         # Cookie set karo session persist ke liye
#                         try:
#                             import extra_streamlit_components as stx
#                             cookie_manager = stx.CookieManager(key='login_cookies')
#                             cookie_manager.set('pm_user_id',  user['id'],       key='set_uid')
#                             cookie_manager.set('pm_username', user['username'],  key='set_uname')
#                         except:
#                             pass
#                         st.success(f"Welcome, {user['username']}!")
#                         st.rerun()
#                     else:
#                         st.error(message)

#         with tab_signup:
#             st.markdown("#### Create Account")
#             signup_username = st.text_input("Username", placeholder="Choose a username", key="signup_user")
#             signup_email    = st.text_input("Email",    placeholder="Enter your email",   key="signup_email")
#             signup_password = st.text_input("Password", placeholder="Choose a strong password",
#                                             type="password", key="signup_pass")
#             signup_confirm  = st.text_input("Confirm Password", placeholder="Confirm your password",
#                                             type="password", key="signup_confirm")
#             if st.button("Create Account", use_container_width=True, type="primary", key="signup_btn"):
#                 if not all([signup_username, signup_email, signup_password, signup_confirm]):
#                     st.error("Please fill all fields!")
#                 elif len(signup_password) < 6:
#                     st.error("Password must be at least 6 characters!")
#                 elif signup_password != signup_confirm:
#                     st.error("Passwords do not match!")
#                 elif '@' not in signup_email:
#                     st.error("Please enter a valid email!")
#                 else:
#                     with st.spinner("Creating account..."):
#                         success, message = signup_user(
#                             signup_username, signup_email, signup_password)
#                     if success:
#                         st.success(message)
#                         st.info("Account created! Please login now.")
#                     else:
#                         st.error(message)











import streamlit as st
from auth.auth_handler import signup_user, login_user

def show_auth_page():
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

      .stApp, html, body {
          background-color: #060A14 !important;
          color: #E2E8F0 !important;
          font-family: 'DM Sans', sans-serif !important;
      }
      * { color-scheme: dark !important; }
      section[data-testid="stSidebar"] { display: none !important; }
      footer { visibility: hidden; }
      button[aria-label="Use system theme"],
      button[aria-label="Use light theme"] { display: none !important; }

      .block-container {
          padding-top: 0 !important;
          max-width: 480px !important;
          margin: 0 auto !important;
      }

      /* Full page centering */
      .auth-page-wrap {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 32px 0;
      }

      /* Logo / hero */
      .auth-hero {
          text-align: center;
          margin-bottom: 28px;
      }
      .auth-icon-wrap {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 60px; height: 60px;
          background: linear-gradient(135deg, #6366F1, #8B5CF6);
          border-radius: 18px;
          font-size: 26px;
          margin-bottom: 16px;
          box-shadow: 0 8px 32px rgba(99,102,241,0.35);
      }
      .auth-title {
          font-size: 1.75rem;
          font-weight: 800;
          color: #F1F5F9;
          letter-spacing: -0.03em;
          margin-bottom: 6px;
      }
      .auth-subtitle {
          font-size: 0.85rem;
          color: #64748B;
          font-weight: 400;
      }

      /* Card */
      .auth-card {
          background: #0D1424;
          border: 1px solid rgba(255,255,255,0.08);
          border-radius: 20px;
          padding: 32px 28px 28px;
          width: 100%;
      }

      /* Tabs */
      div[data-testid="stTabs"] [data-baseweb="tab-list"] {
          background: #060A14 !important;
          border-radius: 12px !important;
          padding: 4px !important;
          gap: 2px !important;
          border: 1px solid rgba(255,255,255,0.07) !important;
          margin-bottom: 20px !important;
      }
      div[data-testid="stTabs"] [data-baseweb="tab"] {
          background: transparent !important;
          color: #64748B !important;
          border-radius: 9px !important;
          font-size: 0.85rem !important;
          font-weight: 600 !important;
          padding: 9px 24px !important;
          font-family: 'DM Sans', sans-serif !important;
          transition: color 0.2s !important;
      }
      div[data-testid="stTabs"] [aria-selected="true"] {
          background: #1A2540 !important;
          color: #F1F5F9 !important;
      }
      div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }

      /* Form labels */
      .stTextInput label {
          color: #94A3B8 !important;
          font-size: 0.75rem !important;
          font-weight: 700 !important;
          text-transform: uppercase !important;
          letter-spacing: 0.08em !important;
          margin-bottom: 4px !important;
      }

      /* Inputs */
      .stTextInput input {
          background-color: #060A14 !important;
          color: #F1F5F9 !important;
          border: 1px solid rgba(255,255,255,0.1) !important;
          border-radius: 10px !important;
          font-family: 'DM Sans', sans-serif !important;
          font-size: 0.95rem !important;
          padding: 11px 14px !important;
          transition: border-color 0.2s, box-shadow 0.2s !important;
      }
      .stTextInput input::placeholder { color: #334155 !important; }
      .stTextInput input:focus {
          border-color: rgba(99,102,241,0.55) !important;
          box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
          outline: none !important;
      }

      /* Section heading inside form */
      .form-heading {
          font-size: 1.05rem;
          font-weight: 700;
          color: #F1F5F9;
          margin-bottom: 2px;
          letter-spacing: -0.01em;
      }
      .form-subheading {
          font-size: 0.8rem;
          color: #64748B;
          margin-bottom: 18px;
      }

      /* Primary button */
      .stButton > button[kind="primary"] {
          background: linear-gradient(135deg, #6366F1 0%, #7C3AED 100%) !important;
          border: none !important;
          color: #FFFFFF !important;
          font-family: 'DM Sans', sans-serif !important;
          font-size: 0.92rem !important;
          font-weight: 700 !important;
          letter-spacing: 0.01em !important;
          border-radius: 11px !important;
          padding: 12px 0 !important;
          margin-top: 4px !important;
          transition: all 0.2s ease !important;
          box-shadow: 0 4px 16px rgba(99,102,241,0.3) !important;
      }
      .stButton > button[kind="primary"]:hover {
          transform: translateY(-1px) !important;
          box-shadow: 0 8px 24px rgba(99,102,241,0.45) !important;
      }
      .stButton > button[kind="primary"]:active {
          transform: translateY(0) !important;
      }

      /* Alert / success / error boxes */
      .stAlert {
          border-radius: 10px !important;
          font-size: 0.85rem !important;
          margin-top: 12px !important;
      }
    </style>
    """, unsafe_allow_html=True)

    # ── Hero section (always visible above the card) ──
    st.markdown("""
    <div style="text-align:center; padding: 48px 0 24px;">
        <div style="
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 62px; height: 62px;
            background: linear-gradient(135deg, #6366F1, #8B5CF6);
            border-radius: 18px;
            font-size: 28px;
            margin-bottom: 16px;
            box-shadow: 0 8px 32px rgba(99,102,241,0.35);
        ">📈</div>
        <div style="
            font-size: 1.8rem;
            font-weight: 800;
            color: #F1F5F9;
            letter-spacing: -0.03em;
            margin-bottom: 6px;
            font-family: 'DM Sans', sans-serif;
        ">Portfolio Manager</div>
        <div style="
            font-size: 0.85rem;
            color: #64748B;
            font-family: 'DM Sans', sans-serif;
        ">Real-time investment tracking & analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Card wrap ──
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["Login", "Create Account"])

    with tab_login:
        st.markdown('<div class="form-heading">Welcome back</div>', unsafe_allow_html=True)
        st.markdown('<div class="form-subheading">Login to your portfolio</div>', unsafe_allow_html=True)

        login_email    = st.text_input("Email Address", placeholder="you@email.com", key="login_email")
        login_password = st.text_input("Password", placeholder="••••••••", type="password", key="login_pass")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Login →", use_container_width=True, type="primary", key="login_btn"):
            if not login_email or not login_password:
                st.error("Please fill in all fields.")
            else:
                with st.spinner(""):
                    success, message, user = login_user(login_email, login_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user      = user
                    st.session_state.user_id   = user['id']
                    st.session_state.username  = user['username']
                    try:
                        import extra_streamlit_components as stx
                        cm = stx.CookieManager(key='login_cookies')
                        cm.set('pm_user_id',  user['id'],      key='set_uid')
                        cm.set('pm_username', user['username'], key='set_uname')
                    except:
                        pass
                    st.rerun()
                else:
                    st.error(message)

    with tab_signup:
        st.markdown('<div class="form-heading">Create account</div>', unsafe_allow_html=True)
        st.markdown('<div class="form-subheading">Get started in seconds — free forever</div>', unsafe_allow_html=True)

        signup_username = st.text_input("Username", placeholder="johndoe", key="signup_user")
        signup_email    = st.text_input("Email Address", placeholder="you@email.com", key="signup_email")

        c1, c2 = st.columns(2)
        with c1:
            signup_password = st.text_input("Password", placeholder="••••••••", type="password", key="signup_pass")
        with c2:
            signup_confirm  = st.text_input("Confirm", placeholder="••••••••", type="password", key="signup_confirm")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Create Account →", use_container_width=True, type="primary", key="signup_btn"):
            if not all([signup_username, signup_email, signup_password, signup_confirm]):
                st.error("Please fill in all fields.")
            elif len(signup_password) < 6:
                st.error("Password must be at least 6 characters.")
            elif signup_password != signup_confirm:
                st.error("Passwords do not match.")
            elif '@' not in signup_email:
                st.error("Please enter a valid email address.")
            else:
                with st.spinner("Creating account..."):
                    success, message = signup_user(signup_username, signup_email, signup_password)
                if success:
                    st.success(message)
                    st.info("Account created! Please Login.")
                else:
                    st.error(message)

    st.markdown('</div>', unsafe_allow_html=True)