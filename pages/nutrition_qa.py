import streamlit as st
from rag_system import answer_nutrition_question
from auth_functions import save_qa_entry, get_qa_history

st.set_page_config(page_title="Nutrition Q&A", page_icon="🔬", layout="wide")

if "user" not in st.session_state:
    st.warning("Please login first!")
    st.stop()


# Load persisted QA history for logged in users (only once)
if "qa_history" not in st.session_state:
    try:
        loaded = get_qa_history(st.session_state.user.id)
        # convert supabase rows to simple {'q','a'} items
        st.session_state.qa_history = [
            {"q": r.get("question", ""), "a": r.get("answer", "")} for r in (loaded or [])
        ]
    except Exception:
        st.session_state.qa_history = []

st.markdown(
    """
    <style>
    <style>
    .qa-hero { padding: 2rem 1.6rem; border-radius: 24px; background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 24px 60px rgba(16, 185, 129, 0.4); margin-bottom: 2rem; }
    .qa-hero h1 { margin: 0; color: #ffffff; font-size: 2.6rem; }
    .qa-hero p { color: #f0fdf4; margin: 1rem 0 0; font-size: 1.05rem; }
    .qa-button-row .stButton>button { border-radius: 16px; padding: 0.9rem 1rem; font-weight: 700; }
    .qa-button-row .stButton>button:hover { transform: translateY(-1px); }
    .qa-panel { background: #ffffff; border: 1px solid rgba(16, 185, 129, 0.12); border-radius: 24px; padding: 1.8rem; }
    .stTextInput>div>div>input { background: #f9fafb !important; color: #1f2937 !important; border: 1px solid rgba(16, 185, 129, 0.16) !important; }
    .stTextInput>div>label { color: #1f2937 !important; }
    .stButton>button { border-radius: 14px; padding: 0.85rem 1.4rem; }
    </style>
    <div class="qa-hero">
      <h1>🔬 Nutrition Q&A</h1>
      <p>Ask questions about nutrition, your knowledge base, and your saved meal plans.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("**💡 Try asking:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Is quinoa good for weight loss?", key="qa_quinoa"):
        st.session_state.question = "Is quinoa good for weight loss?"
with col2:
    if st.button("Best protein sources for vegetarians?", key="qa_protein"):
        st.session_state.question = "Best protein sources for vegetarians?"
with col3:
    if st.button("How much water should I drink daily?", key="qa_water"):
        st.session_state.question = "How much water should I drink daily?"

question = st.text_input(
    "Ask your nutrition question:",
    value=st.session_state.get("question", ""),
    placeholder="e.g. What foods are high in protein?",
    key="qa_input",
)

if st.button("🔍 Get Answer", type="primary", key="qa_get_answer"):
    if question:
        with st.spinner("Searching knowledge base..."):
            result = answer_nutrition_question(question, user_id=st.session_state.user.id)

        st.success("✅ Answer found!")
        st.subheader("📝 Answer:")
        st.write(result["answer"])

        if result.get("sources"):
            st.subheader("📚 Sources:")
            for source in result["sources"]:
                st.caption(f"📄 {source}")

        if any("Saved Meal Plan" in source for source in result.get("sources", [])):
            st.info("🔎 Answer used your saved meal plans as additional context.")

        with st.expander("🔍 View retrieved context"):
            st.text(result.get("context_used", "No context available."))

        st.session_state.qa_history = st.session_state.get("qa_history", [])
        entry = {"q": question, "a": result["answer"]}
        st.session_state.qa_history.append(entry)
        # persist to database for the logged-in user
        try:
            ok, msg = save_qa_entry(st.session_state.user.id, question, result["answer"])
            if not ok:
                st.warning("Could not save your question to the server. It will remain in this session.")
        except Exception as e:
            st.warning("Could not save your question to the server. It will remain in this session.")
            print("QA save error:", e)
    else:
        st.warning("Please enter a question!")

st.divider()

st.subheader("💬 Previous Questions")
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

for idx, item in enumerate(reversed(st.session_state.qa_history[-5:])):
    with st.expander(f"Q: {item['q'][:50]}...", expanded=False):
        st.write(item["a"])
