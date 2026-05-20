import streamlit as st
from auth_functions import sign_in, sign_up

st.set_page_config(
    page_title="Login - Nutrition Planner",
    page_icon="🔐",
    layout="centered"
)

st.markdown(
    """
    <style>
    html, body { background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%) !important; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); padding-top: 2rem; }
    [data-testid="stBaseLayer"] { background: transparent; }
    * { color: #1f2937; }
    
    .auth-container { max-width: 420px; margin: 0 auto; }
    .auth-box { background: #ffffff; border-radius: 20px; padding: 2.5rem; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); border: 1px solid rgba(16, 185, 129, 0.12); }
    .auth-box h1 { text-align: center; font-size: 1.8rem; font-weight: 700; color: #1f2937; margin: 0 0 0.3rem; }
    .auth-box .subtitle { text-align: center; color: #6b7280; font-size: 0.9rem; margin: 0 0 2rem; line-height: 1.5; }
    .auth-link { color: #10b981; text-decoration: none; font-weight: 600; cursor: pointer; }
    .auth-link:hover { text-decoration: underline; }
    
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; border-bottom: 2px solid #e5e7eb; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; color: #6b7280; padding: 0.75rem 1rem; font-weight: 600; border-bottom: 3px solid transparent !important; }
    .stTabs [aria-selected="true"] { color: #10b981 !important; border-bottom: 3px solid #10b981 !important; background-color: transparent !important; }
    
    .stTextInput>div>div>input { background: #f9fafb !important; color: #1f2937 !important; border: 1px solid #e5e7eb !important; border-radius: 8px !important; padding: 0.65rem 0.75rem !important; font-size: 0.95rem !important; }
    .stTextInput>div>div>input:focus { border-color: #10b981 !important; box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.08) !important; }
    .stTextInput>div>label { color: #374151 !important; font-weight: 600 !important; font-size: 0.85rem !important; margin-bottom: 0.4rem !important; }
    
    .stButton>button { border-radius: 8px !important; padding: 0.65rem 1.2rem !important; font-weight: 700 !important; width: 100% !important; }
    .stButton>button[kind="primary"] { background: linear-gradient(135deg, #10b981, #059669) !important; color: white !important; border: none !important; }
    .stButton>button[kind="primary"]:hover { box-shadow: 0 6px 18px rgba(16, 185, 129, 0.28) !important; }
    
    .auth-footer { text-align: center; font-size: 0.85rem; color: #6b7280; margin-top: 1.5rem; }
    .auth-error { background: #fef2f2; color: #991b1b; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #ef4444; font-size: 0.9rem; }
    .auth-success { background: #f0fdf4; color: #166534; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #22c55e; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="auth-container"><div class="auth-box">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<h1>🥗 Nutrition Planner</h1>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    st.markdown('<p class="subtitle">Sign in to access your personalized nutrition plans</p>', unsafe_allow_html=True)
    
    login_email = st.text_input("Email", key="login_email", placeholder="you@example.com")
    login_password = st.text_input("Password", type="password", key="login_pass", placeholder="Your password")

    if st.button("Log In", type="primary", use_container_width=True, key="login_btn"):
        if login_email and login_password:
            with st.spinner("Signing in..."):
                success, result = sign_in(login_email, login_password)

            if success:
                st.session_state.user = result
                st.session_state.user_email = login_email
                st.markdown('<div class="auth-success">✅ Login successful! Redirecting...</div>', unsafe_allow_html=True)
                st.rerun()
            else:
                st.markdown(f'<div class="auth-error">❌ {result}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="auth-error">❌ Please enter both email and password</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<p class="subtitle">Create a new account to get started</p>', unsafe_allow_html=True)
    
    full_name = st.text_input("Full Name", key="signup_name", placeholder="Your full name")
    signup_email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
    signup_password = st.text_input("Password", type="password", key="signup_pass", placeholder="Min 6 characters")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Repeat password")

    if st.button("Create Account", type="primary", use_container_width=True, key="signup_btn"):
        if not all([full_name, signup_email, signup_password, confirm_password]):
            st.markdown('<div class="auth-error">❌ Please fill in all fields</div>', unsafe_allow_html=True)
        elif signup_password != confirm_password:
            st.markdown('<div class="auth-error">❌ Passwords do not match!</div>', unsafe_allow_html=True)
        elif len(signup_password) < 6:
            st.markdown('<div class="auth-error">❌ Password must be at least 6 characters</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Creating your account..."):
                success, message = sign_up(signup_email, signup_password, full_name)
            if success:
                st.markdown('<div class="auth-success">✅ Account created! Please log in with your credentials.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="auth-error">❌ {message}</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)
