import streamlit as st
import datetime
from auth_functions import get_profile, get_saved_plans
try:
    import plotly.express as px
    _HAS_PLOTLY = True
except Exception:
    _HAS_PLOTLY = False
import pandas as pd


# ---------- Design system and global CSS ----------
st.markdown(
    """
    <style>
    :root{
      --primary-green: #16A34A;
      --primary-dark: #0F6E56;
      --bg-light: #F0FDF4;
      --card-white: #FFFFFF;
      --text-dark: #1A2E1A;
      --muted: #6B7280;
      --sidebar-width: 220px;
    }
    html, body, [data-testid="stAppViewContainer"] { background: var(--bg-light) !important; }
    * { font-family: system-ui, -apple-system, 'Inter', Roboto, 'Helvetica Neue', Arial; color: var(--text-dark); }
    .main .block-container { max-width: 1100px; padding: 24px 32px !important; }

    /* Sidebar */
    [data-testid="stSidebar"]{ width: var(--sidebar-width) !important; min-width: var(--sidebar-width) !important; background: #FFFFFF !important; border-right: 1px solid #E5E7EB !important; box-shadow: 0 1px 6px rgba(16,24,40,0.04); }
    [data-testid="stSidebar"] .css-1d391kg, [data-testid="stSidebar"] .css-1awws6m { background: transparent !important; }

    /* Hero banner */
    .hero { background: linear-gradient(90deg, var(--primary-green), var(--primary-dark)); color: white; border-radius: 12px; padding: 40px; display:flex; align-items:center; justify-content:space-between; gap:20px; }
    .hero .title { font-size: 2.2rem; font-weight: 800; margin: 0; }
    .hero .subtitle { color: rgba(255,255,255,0.9); margin-top:6px; font-size:1rem; }
    .hero .adherence { font-size: 2.4rem; font-weight:800; }

    /* Cards */
    .card-row { display:flex; gap:16px; margin-top:20px; }
    .stat-card{ background: var(--card-white); border-radius:12px; padding:18px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); border:1px solid #E5E7EB; flex:1; }
    .stat-value{ font-size:1.6rem; font-weight:700; color: var(--text-dark); }
    .stat-sub{ color: var(--muted); font-size:0.9rem; margin-top:6px }

    /* Quick action cards as buttons */
    .action-row{ display:flex; gap:16px; margin-top:24px }
    .action-btn{ background:var(--card-white); border:1px solid #E5E7EB; border-radius:12px; padding:18px; flex:1; text-align:left; cursor:pointer }
    .action-title{ font-weight:700; color:var(--text-dark); margin-top:8px }
    .action-desc{ color:var(--muted); margin-top:6px }

    /* Streak grid */
    .streak-grid{ display:grid; grid-template-columns: repeat(7, 28px); gap:8px; margin-top:12px }
    .sq{ width:28px; height:28px; border-radius:6px }
    .sq.green{ background:#16A34A }
    .sq.yellow{ background:#F59E0B }
    .sq.gray{ background:#E5E7EB }

    /* Responsive */
    @media (max-width:900px){ .hero{flex-direction:column; align-items:flex-start} .card-row{flex-direction:column} .action-row{flex-direction:column} }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Data helpers ----------
def _friendly_name():
    try:
        p = get_profile(st.session_state.user.id)
        return p.get("full_name") if p and p.get("full_name") else st.session_state.get("user_email", "User")
    except Exception:
        return st.session_state.get("user_email", "User")


def _load_week_data(user_id):
    # Try to build a Mon-Sun calories list from saved plans or fallback sample
    try:
        plans = get_saved_plans(user_id)
        # If there is a recent plan with day calorie totals, attempt to use it
        if plans and isinstance(plans, list):
            latest = plans[0]
            # prefer a 'daily_calories' field
            target = latest.get("daily_calories") or 1540
            # create sample consumed values based on target
            import random
            consumed = [int(target * (0.6 + random.random() * 0.8)) for _ in range(7)]
            return target, consumed
    except Exception:
        pass
    # fallback
    target = 1540
    consumed = [1200, 1480, 1390, 1520, 1600, 900, 1100]
    return target, consumed


# ---------- Render UI ----------
name = _friendly_name()
target_cal, week_consumed = _load_week_data(st.session_state.user.id if "user" in st.session_state and st.session_state.user else None)

# Hero
adherence_pct = int(min(100, max(40, sum(1 for v in week_consumed if abs(v - target_cal) <= target_cal*0.05)/7*100)))
st.markdown(f"<div class='hero'><div><div class='title'>Good morning, {name}!</div><div class='subtitle'>Active plan — Day 5 · Stay on track today</div></div><div class='adherence'>{adherence_pct}%</div></div>", unsafe_allow_html=True)

# Stat cards
st.markdown("<div class='card-row'>", unsafe_allow_html=True)
cols = st.columns(4, gap="small")
today_consumed = week_consumed[datetime.datetime.today().weekday() % 7]
today_remaining = max(0, target_cal - today_consumed)
stats = [
    ("Today's target", f"{target_cal} kcal", "Daily calorie goal"),
    ("Consumed so far", f"{today_consumed} kcal", f"{today_remaining} kcal remaining"),
    ("Protein today", "54g", "of 112g"),
    ("Streak", "5", "days on target"),
]
for c, (title, value, sub) in zip(cols, stats):
    with c:
        st.markdown(f"<div class='stat-card'><div style='color:var(--muted); font-weight:600'>{title}</div><div class='stat-value'>{value}</div><div class='stat-sub'>{sub}</div></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)


# Weekly calorie adherence chart (plotly)
days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
df = pd.DataFrame({"day": days, "calories": week_consumed})
df["target"] = target_cal
if _HAS_PLOTLY:
    fig = px.bar(df, x="day", y="calories", text="calories", height=260, labels={"calories":"Calories"})
    fig.update_traces(marker_color=[('#16A34A' if abs(v-target_cal)<=target_cal*0.05 else '#f97316' if v<target_cal*0.88 else '#ef4444') for v in df['calories']])
    fig.update_layout(margin=dict(l=0,r=0,t=10,b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.markdown('<div style="margin-top:22px">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div style="font-size:13px; color:#6B7280; margin-top:6px">Legend: <span style="color:#16A34A">● On target</span> <span style="margin-left:12px; color:#f97316">● Under</span> <span style="margin-left:12px; color:#ef4444">● Over</span></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Polished HTML/CSS fallback bar chart when plotly is not installed
    st.markdown('<div style="margin-top:22px">', unsafe_allow_html=True)
    # compute pct values (may be >100 when over target)
    pcts = [(v/target_cal)*100 for v in week_consumed]
    max_pct = max(100, max(pcts))
    bar_rows = ['<div style="display:flex;flex-direction:column;gap:12px">']
    for day, v, pct in zip(days, week_consumed, pcts):
        pct_clamped = int(min(100, pct))
        # color rules
        color = '#16A34A' if abs(v-target_cal)<=target_cal*0.05 else ('#f97316' if v<target_cal*0.88 else '#ef4444')
        diff = int(round((v-target_cal)/target_cal*100))
        diff_label = f"{diff:+d}%"
        diff_color = '#16A34A' if diff>=0 and abs(diff)<=5 else ('#ef4444' if diff>5 else '#f97316')

        bar_rows.append("<div style='display:flex;align-items:center;gap:14px'>")
        bar_rows.append(f"<div style='width:44px;color:var(--muted);font-weight:600'>{day}</div>")
        # bar container with target marker (positioned at 100% of container)
        bar_rows.append(
            "<div style='flex:1; position:relative; padding-right:8px'>"
            "<div style='background:#E5E7EB;border-radius:8px;height:16px;overflow:visible;position:relative'>"
            f"<div title='{v} kcal' style='width:{pct_clamped}%;background:{color};height:100%;border-radius:8px;'></div>"
            # overhang indicator when pct > 100
            + (f"<div style='position:absolute;right:0;top:-6px;background:#111827;color:white;padding:2px 6px;border-radius:8px;font-size:11px'>{int(pct)}%'</div>" if pct>100 else "")
            "</div>"
            # target marker line
            f"<div style='position:absolute;left:calc(100%);top:0;height:16px;width:2px;background:rgba(0,0,0,0.12);transform:translateX(-1px);border-radius:1px'></div>"
            "</div>"
        )
        bar_rows.append(f"<div style='width:110px;text-align:right;font-size:13px;color:var(--muted);font-weight:600'>{v} kcal</div>")
        bar_rows.append(f"<div style='width:64px;text-align:right;font-size:12px;color:{diff_color};font-weight:700'>{diff_label}</div>")
        bar_rows.append("</div>")

    bar_rows.append('</div>')
    st.markdown('\n'.join(bar_rows), unsafe_allow_html=True)
    st.markdown('<div style="font-size:13px; color:#6B7280; margin-top:10px">Legend: <span style="color:#16A34A">● On target</span> <span style="margin-left:12px; color:#f97316">● Under</span> <span style="margin-left:12px; color:#ef4444">● Over</span> — <span style="margin-left:12px; font-weight:600">Target</span> is shown as a vertical marker.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# Monthly streak grid
st.markdown('<div style="margin-top:22px"><div style="display:flex; justify-content:space-between; align-items:center"><div style="font-weight:700">This month — streak</div><div style="color:var(--muted)">18 / 30 days on target</div></div><div class="streak-grid">', unsafe_allow_html=True)
import random
for i in range(35):
    cls = random.choice(['green']*18 + ['yellow']*6 + ['gray']*11)
    st.markdown(f"<div class='sq {cls}'></div>", unsafe_allow_html=True)
st.markdown('</div></div>', unsafe_allow_html=True)


# Quick action cards (buttons)
st.markdown('<div class="action-row">', unsafe_allow_html=True)
col_a, col_b, col_c = st.columns(3, gap='small')
with col_a:
    if st.button('🍽️ Meal Planner', key='goto_meal'):
        st.session_state.page = 'Meal Planner'
        st.experimental_rerun()
    st.markdown('<div class="action-desc">Generate a 7-day AI meal plan</div>', unsafe_allow_html=True)
with col_b:
    if st.button('📸 Food Analyser', key='goto_food'):
        st.session_state.page = 'Food Analyser'
        st.experimental_rerun()
    st.markdown('<div class="action-desc">Identify food from a photo</div>', unsafe_allow_html=True)
with col_c:
    if st.button('🔬 Nutrition Q&A', key='goto_qa'):
        st.session_state.page = 'Nutrition Q&A'
        st.experimental_rerun()
    st.markdown('<div class="action-desc">Ask any nutrition question</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


