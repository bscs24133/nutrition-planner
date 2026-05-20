import streamlit as st
from rag_system import answer_nutrition_question

st.set_page_config(page_title="Nutrition Q&A", page_icon="🔬")

if "user" not in st.session_state:
    st.warning("Please login first!")
    st.stop()

st.title("🔬 Nutrition Knowledge Base")
st.markdown("Ask any nutrition question and get answers from our knowledge base!")
st.divider()

st.markdown("**💡 Try asking:**")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Is quinoa good for weight loss?"):
        st.session_state.question = "Is quinoa good for weight loss?"
with col2:
    if st.button("Best protein sources for vegetarians?"):
        st.session_state.question = "Best protein sources for vegetarians?"
with col3:
    if st.button("How much water should I drink daily?"):
        st.session_state.question = "How much water should I drink daily?"

question = st.text_input(
    "Ask your nutrition question:",
    value=st.session_state.get("question", ""),
    placeholder="e.g. What foods are high in protein?"
)

if st.button("🔍 Get Answer", type="primary"):
    if question:
        with st.spinner("Searching knowledge base..."):
            result = answer_nutrition_question(question)

        st.success("✅ Answer found!")
        st.subheader("📝 Answer:")
        st.write(result["answer"])

        if result["sources"]:
            st.subheader("📚 Sources:")
            for source in result["sources"]:
                st.caption(f"📄 {source}")

        with st.expander("🔍 View retrieved context"):
            st.text(result["context_used"])

        st.session_state.last_answer = result["answer"]
        st.session_state.qa_history = st.session_state.get("qa_history", [])
        st.session_state.qa_history.append({
            "q": question,
            "a": result["answer"]
        })
    else:
        st.warning("Please enter a question!")

st.divider()
st.subheader("💬 Previous Questions")
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

for item in reversed(st.session_state.qa_history[-5:]):
    with st.expander(f"Q: {item['q'][:50]}..."):
        st.write(item["a"])
