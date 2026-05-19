import streamlit as st
import json, os, re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

ACTIVITY_MULTIPLIERS = {
    "Sedentary (little or no exercise)": 1.2,
    "Lightly Active (1-3 days/week)": 1.375,
    "Moderately Active (3-5 days/week)": 1.55,
    "Very Active (6-7 days/week)": 1.725,
    "Extra Active (physical job + training)": 1.9,
}
GOAL_ADJUSTMENTS = {"Lose Weight": -500, "Maintain Weight": 0, "Gain Muscle": 300, "Gain Weight": 500}


def calculate_bmr(w, h, a, g):
    if g == "Male":
        return 88.362 + 13.397 * w + 4.799 * h - 5.677 * a
    return 447.593 + 9.247 * w + 3.098 * h - 4.330 * a


def daily_calories(bmr, act, goal):
    return max(1200, int(bmr * ACTIVITY_MULTIPLIERS[act] + GOAL_ADJUSTMENTS[goal]))


def build_prompt(p):
    fb = f'\n\nUser feedback on previous plan — incorporate it:\n"{p["feedback"]}"\n' if p.get("feedback") else ""
    diet_str = ", ".join(p['diet_type']) if isinstance(p['diet_type'], list) else p['diet_type']
    return f"""You are an expert registered dietitian. Create a 7-day meal plan for:
- Age: {p['age']}  Gender: {p['gender']}  Weight: {p['weight']}kg  Height: {p['height']}cm
- Activity: {p['activity']}  Goal: {p['goal']}  Diet: {diet_str}
- Allergies: {p['allergies'] or 'None'}  Avoid: {p['avoid'] or 'None'}
- Daily Calorie Target: {p['calories']} kcal
{fb}
Return ONLY valid JSON, no markdown fences. Exact structure:
{{"day_1":{{"breakfast":{{"meal_name":"...","description":"...","ingredients":[{{"item":"eggs","quantity":"2","unit":"whole"}},{{"item":"cheese","quantity":"1","unit":"slice"}}],"calories":0,"protein_g":0,"carbs_g":0,"fat_g":0}},"lunch":{{...}},"dinner":{{...}},"snacks":{{...}}}},"day_2":{{...}},...,"day_7":{{...}}}}

Rules:
- Each day total ≈ {p['calories']} kcal (±100)
- Respect ALL dietary restrictions strictly
- Use realistic calorie/macro values
- Keep meal descriptions under 10 words
- Vary meals across days
- For EACH meal, include an "ingredients" array with {{"item","quantity","unit"}} objects
- Quantity examples: "2", "1/2", "150" (as string). Unit examples: "whole", "slice", "cup", "tbsp", "g", "ml"
- Be specific and practical (e.g., "2 slices" toast, "150g" chicken, "1 cup" rice)"""

def parse_plan(text):
    cleaned = re.sub(r"```(?:json)?", "", text).strip().rstrip("`")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                return None
    return None


def generate_plan(profile):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("🔑 GROQ_API_KEY not found. Add it to your .env file.")
        return None

    # Try up to 3 times
    for attempt in range(3):
        try:
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system",
                     "content": "You are a nutritionist AI. Respond with valid JSON only."},
                    {"role": "user",
                     "content": build_prompt(profile)},
                ],
                temperature=0.7,
                max_tokens=2000,  # reduced from 4096
                timeout=30,       # 30 second timeout
            )
            result = parse_plan(resp.choices[0].message.content)
            if result:
                return result
            # If parse failed, try again
            if attempt < 2:
                st.warning(f"⚠️ Attempt {attempt+1} failed, retrying...")
                continue

        except Exception as e:
            if attempt == 2:
                st.error(f"❌ Failed after 3 attempts: {e}")
                return None
            st.warning(f"⚠️ Attempt {attempt+1} failed, retrying...")

    return None


MEAL_ICONS = {"breakfast": "🌅", "lunch": "☀️", "dinner": "🌙", "snacks": "🍎"}


def render_meal(meal_type, data):
    icon = MEAL_ICONS.get(meal_type, "🍴")
    # Defensive rendering: the AI may return incomplete data, so use .get() with
    # sensible defaults to avoid KeyError and keep the UI stable.
    if not isinstance(data, dict):
        st.warning("Malformed meal data")
        return

    meal_name = data.get("meal_name", "Unknown Meal")
    description = data.get("description", "")
    ingredients = data.get("ingredients", [])

    def fmt(val, suffix):
        if val is None:
            return "—"
        try:
            return f"{int(val):,} {suffix}" if isinstance(val, (int, float)) else f"{val} {suffix}"
        except Exception:
            return str(val)

    cal_text = fmt(data.get("calories"), "kcal")
    prot_text = fmt(data.get("protein_g"), "g")
    carb_text = fmt(data.get("carbs_g"), "g")
    fat_text = fmt(data.get("fat_g"), "g")

    with st.expander(f"{icon}  **{meal_type.capitalize()}** — {meal_name}", expanded=True):
        if description:
            st.caption(description)
        
        # Display ingredients if available
        if ingredients and isinstance(ingredients, list) and len(ingredients) > 0:
            st.markdown("**🥘 Ingredients:**")
            ing_text = ""
            for ing in ingredients:
                if isinstance(ing, dict):
                    item = ing.get("item", "")
                    quantity = ing.get("quantity", "")
                    unit = ing.get("unit", "")
                    if item:
                        ing_text += f"• {quantity} {unit} {item}\n" if quantity and unit else f"• {item}\n"
            if ing_text:
                st.markdown(ing_text)
        
        # Display macros
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Calories", cal_text)
        c2.metric("Protein", prot_text)
        c3.metric("Carbs", carb_text)
        c4.metric("Fat", fat_text)


def render_weekly(plan):
    tc = tp = tca = tf = 0
    dc = 0
    for dk in sorted(plan):
        dc += 1
        for m in ("breakfast", "lunch", "dinner", "snacks"):
            if m in plan[dk]:
                tc += plan[dk][m].get("calories", 0)
                tp += plan[dk][m].get("protein_g", 0)
                tca += plan[dk][m].get("carbs_g", 0)
                tf += plan[dk][m].get("fat_g", 0)
    st.markdown('<p class="section-header">📊 Weekly Nutritional Summary</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Calories", f"{tc:,} kcal", f"~{tc//max(dc,1):,}/day")
    c2.metric("Total Protein", f"{tp:,} g", f"~{tp//max(dc,1)} g/day")
    c3.metric("Total Carbs", f"{tca:,} g", f"~{tca//max(dc,1)} g/day")
    c4.metric("Total Fat", f"{tf:,} g", f"~{tf//max(dc,1)} g/day")


# ── Page UI ─────────────────────────────────────────────────────────
st.markdown(
    '<div class="hero-banner"><h1>🍽️ Meal Planner</h1>'
    '<p>Generate a personalised 7-day meal plan powered by AI</p></div>',
    unsafe_allow_html=True,
)

st.markdown('<p class="section-header">📝 Your Profile</p>', unsafe_allow_html=True)

with st.form("meal_planner_form"):
    r1c1, r1c2, r1c3, r1c4 = st.columns(4)
    age = r1c1.number_input("Age", 10, 100, 25)
    gender = r1c2.selectbox("Gender", ["Male", "Female"])
    weight = r1c3.number_input("Weight (kg)", 20.0, 300.0, 70.0, 0.5)
    height = r1c4.number_input("Height (cm)", 100.0, 250.0, 170.0, 0.5)

    r2c1, r2c2, r2c3 = st.columns(3)
    activity = r2c1.selectbox("Activity Level", list(ACTIVITY_MULTIPLIERS))
    goal = r2c2.selectbox("Fitness Goal", list(GOAL_ADJUSTMENTS))
    diet_type = r2c3.multiselect("Dietary Type (select 1 or more)", [
        "No Restriction", "Vegetarian", "Vegan", "Pescatarian", "Keto",
        "Paleo", "Mediterranean", "Gluten-Free", "Halal", "Kosher",
    ], default=["No Restriction"])

    r3c1, r3c2 = st.columns(2)
    allergies = r3c1.text_input("Allergies", placeholder="e.g. peanuts, shellfish")
    avoid = r3c2.text_input("Foods to Avoid", placeholder="e.g. broccoli, tofu")
    feedback = st.text_area("Feedback for Regeneration (optional)", height=80,
                            placeholder="e.g. more high-protein breakfasts")
    submitted = st.form_submit_button("🚀 Generate Meal Plan", use_container_width=True)

if submitted:
    errs = []
    if not 10 <= age <= 100: errs.append("Age must be 10-100.")
    if not 20 <= weight <= 300: errs.append("Weight must be 20-300 kg.")
    if not diet_type or len(diet_type) == 0: errs.append("Please select at least one dietary type.")
    for e in errs: st.error(e)
    if not errs:
        bmr = calculate_bmr(weight, height, age, gender)
        cals = daily_calories(bmr, activity, goal)
        profile = dict(age=age, gender=gender, weight=weight, height=height,
                       activity=activity, goal=goal, diet_type=diet_type,
                       allergies=allergies, avoid=avoid, feedback=feedback.strip(), calories=cals, bmr=bmr)

        st.divider()
        st.markdown('<p class="section-header">👤 Your Profile Summary</p>', unsafe_allow_html=True)
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("BMR", f"{bmr:.0f} kcal"); p2.metric("Daily Target", f"{cals:,} kcal")
        p3.metric("Goal", goal); p4.metric("Diet Types", ", ".join(diet_type) if diet_type else "None")
        st.divider()

        with st.spinner("🧠 Generating your personalised meal plan…"):
            plan = generate_plan(profile)
        if plan:
            st.session_state["meal_plan"] = plan
            st.success("✅ Your 7-day meal plan is ready!")
        else:
            st.error("Could not parse the meal plan. Please try again.")

if "meal_plan" in st.session_state:
    plan = st.session_state["meal_plan"]
    st.divider()
    st.markdown('<p class="section-header">📅 Your 7-Day Meal Plan</p>', unsafe_allow_html=True)
    day_names = {"day_1":"Monday","day_2":"Tuesday","day_3":"Wednesday",
                 "day_4":"Thursday","day_5":"Friday","day_6":"Saturday","day_7":"Sunday"}
    sorted_days = sorted(plan)
    tabs = st.tabs([f"📆 {day_names.get(d, d.replace('_',' ').title())}" for d in sorted_days])
    for tab, dk in zip(tabs, sorted_days):
        with tab:
            for m in ("breakfast", "lunch", "dinner", "snacks"):
                if m in plan[dk]: render_meal(m, plan[dk][m])
    st.divider()
    render_weekly(plan)

st.markdown('<div class="app-footer">Powered by Groq · Llama 3.3 70B Versatile</div>', unsafe_allow_html=True)
