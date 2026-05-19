import streamlit as st

# ── Page Configuration ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI-Powered Nutrition Planner",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global Custom CSS ───────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #12101C 0%, #1A1D29 100%);
        border-right: 1px solid rgba(108, 99, 255, 0.15);
    }

    .hero-banner {
        background: linear-gradient(135deg, #6C63FF 0%, #A855F7 50%, #EC4899 100%);
        padding: 2.5rem 2rem; border-radius: 16px; text-align: center;
        margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(108, 99, 255, 0.25);
    }
    .hero-banner h1 { color: #FFF !important; font-weight: 800; font-size: 2.4rem; margin-bottom: .3rem; }
    .hero-banner p  { color: rgba(255,255,255,.88); font-size: 1.1rem; font-weight: 300; }

    .glass-card {
        background: rgba(255,255,255,.04); border: 1px solid rgba(108,99,255,.18);
        border-radius: 14px; padding: 1.6rem; backdrop-filter: blur(12px);
        transition: transform .25s ease, box-shadow .25s ease;
    }
    .glass-card:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(108,99,255,.18); }
    .glass-card h3 { color: #A78BFA; margin-bottom: .5rem; }
    .glass-card p  { color: rgba(250,250,250,.72); font-size: .95rem; line-height: 1.55; }

    [data-testid="stMetric"] {
        background: rgba(108,99,255,.08); border: 1px solid rgba(108,99,255,.18);
        border-radius: 12px; padding: 1rem 1.2rem;
    }
    [data-testid="stMetricLabel"] { color: #A78BFA !important; }
    [data-testid="stMetricValue"] { color: #FAFAFA !important; font-weight: 700; }

    .stButton > button {
        background: linear-gradient(135deg, #6C63FF, #A855F7); color: white;
        border: none; border-radius: 10px; padding: .6rem 1.8rem; font-weight: 600;
        transition: all .3s ease;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(108,99,255,.35); }

    hr { border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(108,99,255,.3), transparent); margin: 1.5rem 0; }

    .section-header {
        color: #A78BFA; font-weight: 700; font-size: 1.35rem; margin-bottom: .6rem;
        padding-bottom: .3rem; border-bottom: 2px solid rgba(108,99,255,.2); display: inline-block;
    }
    .app-footer { text-align: center; color: rgba(250,250,250,.35); font-size: .82rem; padding: 2rem 0 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Navigation ──────────────────────────────────────────────────────
home_page = st.Page("pages/home.py", title="Home", icon="🏠")
meal_planner_page = st.Page("pages/meal_planner.py", title="Meal Planner", icon="🍽️")
food_analyzer_page = st.Page("pages/food_analyzer.py", title="Food Analyzer", icon="📸")

pg = st.navigation([home_page, meal_planner_page, food_analyzer_page])
pg.run()
