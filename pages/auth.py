import streamlit as st
from auth_functions import sign_in, sign_up

st.set_page_config(
    page_title="Login - Nutrition Planner",
    page_icon="🔐"
)

st.title("🥗 AI Nutrition Planner")
st.subheader("Welcome! Please login or create an account.")
st.divider()

tab1, tab2 = st.tabs(["🔐 Login", "✨ Sign Up"])

# LOGIN TAB
with tab1:
    st.subheader("Login to your account")
    login_email = st.text_input(
        "Email", key="login_email",
        placeholder="your@email.com"
    )
    login_password = st.text_input(
        "Password", type="password",
        key="login_pass",
        placeholder="Enter your password"
    )

    if st.button("Login", type="primary",
                 use_container_width=True):
        if login_email and login_password:
            with st.spinner("Logging in..."):
                success, result = sign_in(
                    login_email, login_password)

            if success:
                st.session_state.user = result
                st.session_state.user_email = login_email
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error(f"❌ Login failed: {result}")
        else:
            st.warning("Please enter email and password")

# SIGNUP TAB
with tab2:
    st.subheader("Create a new account")
    full_name = st.text_input(
        "Full Name", placeholder="Ammara Khan"
    )
    signup_email = st.text_input(
        "Email", key="signup_email",
        placeholder="your@email.com"
    )
    signup_password = st.text_input(
        "Password", type="password",
        key="signup_pass",
        placeholder="Min 6 characters"
    )
    confirm_password = st.text_input(
        "Confirm Password", type="password",
        placeholder="Repeat password"
    )

    if st.button("Create Account", type="primary",
                 use_container_width=True):
        if not all([full_name, signup_email,
                    signup_password, confirm_password]):
            st.warning("Please fill in all fields")
        elif signup_password != confirm_password:
            st.error("❌ Passwords do not match!")
        elif len(signup_password) < 6:
            st.error("❌ Password must be at least 6 characters")
        else:
            with st.spinner("Creating account..."):
                success, message = sign_up(
                    signup_email,
                    signup_password,
                    full_name
                )
            if success:
                st.success("✅ Account created! You can now login with your credentials.")
                st.info("Please refresh the page and login to your account.")
            else:
                st.error(f"❌ Error: {message}")