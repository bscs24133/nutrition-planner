import json
import streamlit as st
from auth_functions import get_saved_plans

st.markdown(
    '<div class="hero-banner"><h1>📊 Saved Meal Plans</h1>'
    '<p>View and manage your previously generated meal plans</p></div>',
    unsafe_allow_html=True,
)


def fmt(val, suffix):
    if val is None:
        return "—"
    try:
        return f"{int(val):,} {suffix}" if isinstance(val, (int, float)) else f"{val} {suffix}"
    except Exception:
        return str(val)


def render_meal(meal_type, data):
    if not isinstance(data, dict):
        st.warning("Malformed meal entry")
        return
    name = data.get("meal_name", "Unknown Meal")
    desc = data.get("description", "")
    ingredients = data.get("ingredients", [])
    calories = fmt(data.get("calories"), "kcal")
    protein = fmt(data.get("protein_g"), "g")
    carbs = fmt(data.get("carbs_g"), "g")
    fat = fmt(data.get("fat_g"), "g")

    st.markdown(f"### {meal_type.capitalize()} — {name}")
    if desc:
        st.caption(desc)
    if ingredients and isinstance(ingredients, list):
        lines = []
        for ing in ingredients:
            if isinstance(ing, dict):
                item = ing.get("item", "")
                qty = ing.get("quantity", "")
                unit = ing.get("unit", "")
                if item:
                    lines.append(f"• {qty} {unit} {item}".strip())
        if lines:
            st.markdown("**Ingredients:**\n" + "\n".join(lines))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calories", calories)
    c2.metric("Protein", protein)
    c3.metric("Carbs", carbs)
    c4.metric("Fat", fat)


def render_saved_plan(plan_json):
    day_names = {
        "day_1": "Monday",
        "day_2": "Tuesday",
        "day_3": "Wednesday",
        "day_4": "Thursday",
        "day_5": "Friday",
        "day_6": "Saturday",
        "day_7": "Sunday",
    }
    sorted_days = sorted(plan_json)
    tabs = st.tabs([f"📆 {day_names.get(day, day.replace('_', ' ').title())}" for day in sorted_days])
    for tab, day_key in zip(tabs, sorted_days):
        with tab:
            day_data = plan_json.get(day_key, {})
            for meal_type in ("breakfast", "lunch", "dinner", "snacks"):
                if meal_type in day_data:
                    render_meal(meal_type, day_data[meal_type])
                    st.divider()


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
                    
                    plan_text = plan.get('plan_text', '')
                    plan_json = None
                    if plan_text:
                        try:
                            plan_json = json.loads(plan_text)
                        except Exception as e:
                            st.error(f"❌ Could not load saved meal plan JSON: {e}")
                            st.code(plan_text[:10000])

                    if plan_json:
                        render_saved_plan(plan_json)
                    else:
                        st.info("ℹ️ This plan has no structured meal data to display.")

                    if st.button(f"🗑️ Delete Plan {i+1}", key=f"delete_{plan.get('id')}"):
                        st.info("Delete functionality coming soon!")
        else:
            st.info("📭 No saved meal plans yet. Generate your first plan in the Meal Planner!")
    except Exception as e:
        st.error(f"❌ Error loading plans: {str(e)}")

st.divider()
st.markdown("💡 **Tip:** Generate a new meal plan in the **Meal Planner** page and save it here for later reference.")
