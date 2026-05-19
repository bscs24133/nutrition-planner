import streamlit as st
from auth_functions import get_profile, save_profile

st.markdown(
    '<div class="hero-banner"><h1>👤 My Profile</h1>'
    '<p>Manage your account information and preferences</p></div>',
    unsafe_allow_html=True,
)

# Check if user is logged in
if "user" not in st.session_state or not st.session_state.user:
    st.error("❌ Please log in first.")
    st.stop()

user_id = st.session_state.user.id
user_email = st.session_state.get("user_email", "Unknown")

st.markdown('<p class="section-header">📧 Account Information</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
col1.info(f"**Email:** {user_email}")
col2.info(f"**User ID:** {user_id[:8]}...")

st.divider()

# Load user profile
with st.spinner("Loading your profile..."):
    try:
        profile = get_profile(user_id)
    except Exception as e:
        st.warning(f"⚠️ Could not load profile: {str(e)}")
        profile = None

st.markdown('<p class="section-header">✏️ Profile Information</p>', unsafe_allow_html=True)

with st.form("profile_form"):
    full_name = st.text_input(
        "Full Name",
        value=profile.get("full_name", "") if profile else "",
        placeholder="Your full name"
    )
    
    bio = st.text_area(
        "Bio (optional)",
        value=profile.get("bio", "") if profile else "",
        placeholder="Tell us about yourself...",
        height=100
    )
    
    age = st.number_input(
        "Age",
        min_value=13,
        max_value=120,
        value=int(profile.get("age", 25)) if profile and profile.get("age") else 25
    )
    
    goal = st.selectbox(
        "Fitness Goal",
        ["Lose Weight", "Maintain Weight", "Gain Muscle", "Gain Weight"],
        index=0 if not profile else ["Lose Weight", "Maintain Weight", "Gain Muscle", "Gain Weight"].index(profile.get("goal", "Lose Weight")) if profile.get("goal") in ["Lose Weight", "Maintain Weight", "Gain Muscle", "Gain Weight"] else 0
    )
    
    submitted = st.form_submit_button("💾 Save Profile", use_container_width=True, type="primary")

if submitted:
    if not full_name:
        st.error("❌ Please enter your full name")
    else:
        with st.spinner("Saving profile..."):
            try:
                profile_data = {
                    "full_name": full_name,
                    "bio": bio,
                    "age": age,
                    "goal": goal,
                    "updated_at": "now()"
                }
                success, message = save_profile(user_id, profile_data)
                if success:
                    st.success("✅ Profile updated successfully!")
                else:
                    st.error(f"❌ Error: {message}")
            except Exception as e:
                st.error(f"❌ Error saving profile: {str(e)}")

st.divider()

st.markdown('<p class="section-header">⚙️ Preferences</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.toggle("📧 Email Notifications", value=True)
with col2:
    st.toggle("🔔 Push Notifications", value=False)

st.divider()

st.markdown("💡 **Tip:** Update your profile to get more personalized meal recommendations.")
