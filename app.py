import streamlit as st
from pathlib import Path

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
    html, body { background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%) !important; }
    * { font-family: 'Inter', sans-serif; color: #1f2937; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); }
    [data-testid="stBaseLayer"] { background: transparent; }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f0fdf4 0%, #f9fafb 100%);
        border-right: 2px solid rgba(16, 185, 129, 0.2);
    }
    [data-testid="stSidebar"] * { color: #1f2937; }

    .hero-banner {
        background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
        padding: 2.5rem 2rem; border-radius: 16px; text-align: center;
        margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(16, 185, 129, 0.25);
    }
    .hero-banner h1 { color: #FFF !important; font-weight: 800; font-size: 2.4rem; margin-bottom: .3rem; }
    .hero-banner p  { color: rgba(255,255,255,.88); font-size: 1.1rem; font-weight: 300; }

    .glass-card {
        background: #ffffff; border: 1px solid rgba(16, 185, 129, 0.18);
        border-radius: 14px; padding: 1.6rem; backdrop-filter: blur(12px);
        transition: transform .25s ease, box-shadow .25s ease;
    }
    .glass-card:hover { transform: translateY(-4px); box-shadow: 0 12px 28px rgba(16, 185, 129, 0.18); }
    .glass-card h3 { color: #10b981; margin-bottom: .5rem; }
    .glass-card p  { color: rgba(31, 41, 55, 0.72); font-size: .95rem; line-height: 1.55; }

    [data-testid="stMetric"] {
        background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.18);
        border-radius: 12px; padding: 1rem 1.2rem;
    }
    [data-testid="stMetricLabel"] { color: #10b981 !important; }
    [data-testid="stMetricValue"] { color: #1f2937 !important; font-weight: 700; }

    .stButton > button {
        background: linear-gradient(135deg, #10b981, #059669); color: white;
        border: none; border-radius: 14px; padding: .9rem 1.8rem; font-weight: 700;
        transition: all .3s ease;
    }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(16, 185, 129, 0.3); }
    .stButton>button[disabled] { opacity: .65; cursor: not-allowed; }

    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div>div {
        background: #f9fafb !important;
        color: #1f2937 !important;
        border: 1px solid rgba(16, 185, 129, 0.18) !important;
        border-radius: 12px !important;
    }
    .stTextInput>div>label, .stSelectbox>div>label, .stButton>label {
        color: #1f2937 !important;
    }
    .streamlit-expanderHeader {
        background: #f0fdf4;
        border: 1px solid rgba(16, 185, 129, 0.12);
        border-radius: 14px;
    }
    .css-1d391kg, .css-1awws6m { background: transparent; }
    [data-testid="stMarkdownContainer"], [data-testid="stVerticalBlock"] { background: transparent !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { background-color: #e0f2fe; color: #1f2937; }
    .stTabs [aria-selected="true"] { background-color: #10b981 !important; color: white !important; }

    hr { border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.3), transparent); margin: 1.5rem 0; }

    .section-header {
        color: #10b981; font-weight: 700; font-size: 1.35rem; margin-bottom: .6rem;
        padding-bottom: .3rem; border-bottom: 2px solid rgba(16, 185, 129, 0.2); display: inline-block;
    }
    .app-footer { text-align: center; color: rgba(31, 41, 55, 0.35); font-size: .82rem; padding: 2rem 0 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Initialize Session State ────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None

# ── Navigation ──────────────────────────────────────────────────────
base_path = Path(__file__).resolve().parent

if st.session_state.user:
    # User is authenticated — show all app pages
    home_page = st.Page(str(base_path / "pages" / "home.py"), title="Home", icon="🏠")
    meal_planner_page = st.Page(str(base_path / "pages" / "meal_planner.py"), title="Meal Planner", icon="🍽️")
    food_analyzer_page = st.Page(str(base_path / "pages" / "food_analyzer.py"), title="Food Analyzer", icon="📸")
    nutrition_qa_page = st.Page(str(base_path / "pages" / "nutrition_qa.py"), title="Nutrition Q&A", icon="🔬")
    saved_plans_page = st.Page(str(base_path / "pages" / "saved_plans.py"), title="Saved Plans", icon="📊")
    profile_page = st.Page(str(base_path / "pages" / "profile.py"), title="My Profile", icon="👤")
    
    pages = [home_page, meal_planner_page, food_analyzer_page, nutrition_qa_page, saved_plans_page, profile_page]
    
    # Add logout button in sidebar
    with st.sidebar:
        st.title("🥗 Nutrition Planner")
        email = st.session_state.get("user_email", "User")
        st.success(f"👤 {email}")
        st.divider()
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            try:
                from auth_functions import sign_out
                sign_out()
            except Exception:
                pass
            st.session_state.user = None
            st.session_state.user_email = None
            st.rerun()
else:
    # User is not authenticated — show only auth page
    auth_page = st.Page(str(base_path / "pages" / "auth.py"), title="Login", icon="🔐")
    pages = [auth_page]

pg = st.navigation(pages)
pg.run()

