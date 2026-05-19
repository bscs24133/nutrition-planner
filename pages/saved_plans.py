import streamlit as st
from auth_functions import get_saved_plans

st.markdown(
    '<div class="hero-banner"><h1>📊 Saved Meal Plans</h1>'
    '<p>View and manage your previously generated meal plans</p></div>',
    unsafe_allow_html=True,
)

# Check if user is logged in
if "user" not in st.session_state or not st.session_state.user:
    st.error("❌ Please log in first.")
    st.stop()

user_id = st.session_state.user.id

# Fetch saved plans
with st.spinner("Loading your saved plans..."):
    try:
        plans = get_saved_plans(user_id)
        if plans:
            st.success(f"✅ Found {len(plans)} saved meal plan(s)")
            st.divider()
            
            for i, plan in enumerate(plans):
                with st.expander(f"📅 Plan {i+1} — {plan.get('goal', 'Unknown Goal')} ({plan.get('diet_type', 'No restriction')})"):
                    col1, col2 = st.columns(2)
                    col1.metric("Daily Calories", f"{plan.get('daily_calories', '—')} kcal")
                    col2.metric("Goal", plan.get('goal', 'Unknown'))
                    
                    st.caption(f"Created: {plan.get('created_at', 'Unknown date')}")
                    
                    if st.button(f"🗑️ Delete Plan {i+1}", key=f"delete_{plan.get('id')}"):
                        st.info("Delete functionality coming soon!")
        else:
            st.info("📭 No saved meal plans yet. Generate your first plan in the Meal Planner!")
    except Exception as e:
        st.error(f"❌ Error loading plans: {str(e)}")

st.divider()
st.markdown("💡 **Tip:** Generate a new meal plan in the **Meal Planner** page and save it here for later reference.")
