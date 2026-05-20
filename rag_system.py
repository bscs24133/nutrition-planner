import json
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from groq import Groq
from auth_functions import get_saved_plans

load_dotenv()

# Global vector store (loaded once)
vector_store = None
embeddings = None


def load_knowledge_base():
    """Load all nutrition documents into ChromaDB"""
    global vector_store, embeddings

    if vector_store is not None:
        return vector_store  # already loaded

    print("Loading nutrition knowledge base...")

    documents = []
    docs_folder = "nutrition_docs"

    if not os.path.isdir(docs_folder):
        raise FileNotFoundError(f"Knowledge base folder not found: {docs_folder}")

    for filename in os.listdir(docs_folder):
        filepath = os.path.join(docs_folder, filename)
        if filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding="utf-8")
            documents.extend(loader.load())
        elif filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            documents.extend(loader.load())

    chunks = split_documents(documents, chunk_size=500, chunk_overlap=50)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    print(f"✅ Loaded {len(chunks)} chunks into knowledge base!")
    return vector_store


def split_documents(documents, chunk_size=500, chunk_overlap=50):
    chunks = []
    for doc in documents:
        text = doc.page_content
        metadata = dict(getattr(doc, 'metadata', {}) or {})
        start = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            chunk_text = text[start:end]
            if end < len(text):
                last_space = chunk_text.rfind(' ')
                if last_space > chunk_size * 0.6:
                    end = start + last_space
                    chunk_text = text[start:end]
            chunks.append(Document(page_content=chunk_text, metadata=metadata))
            if end >= len(text):
                break
            start = end - chunk_overlap
    return chunks


def search_knowledge_base(query, top_k=3):
    """Search for relevant nutrition info"""
    store = load_knowledge_base()
    results = store.similarity_search(query, k=top_k)
    return results


def get_saved_plan_documents(user_id):
    """Convert saved meal plans into RAG documents."""
    documents = []
    if not user_id:
        return documents

    records = get_saved_plans(user_id)
    if not records:
        return documents

    day_names = {
        "day_1": "Monday",
        "day_2": "Tuesday",
        "day_3": "Wednesday",
        "day_4": "Thursday",
        "day_5": "Friday",
        "day_6": "Saturday",
        "day_7": "Sunday",
    }

    for plan in records:
        plan_text = plan.get("plan_text", "")
        try:
            plan_json = json.loads(plan_text)
        except Exception:
            continue

        metadata = {
            "source": f"Saved Meal Plan ({plan.get('goal', 'Unknown Goal')})",
            "plan_id": plan.get("id"),
        }

        lines = [
            f"Saved plan goal: {plan.get('goal', 'Unknown')}",
            f"Daily calories target: {plan.get('daily_calories', 'Unknown')} kcal",
            f"Diet preference: {plan.get('diet_type', 'No restriction')}",
        ]

        for day_key in sorted(plan_json.keys()):
            day_label = day_names.get(day_key, day_key.replace("_", " ").title())
            lines.append(f"{day_label}:")
            day_data = plan_json.get(day_key, {})
            for meal_type in ("breakfast", "lunch", "dinner", "snacks"):
                meal_data = day_data.get(meal_type)
                if isinstance(meal_data, dict):
                    meal_name = meal_data.get("meal_name", "").strip()
                    calories = meal_data.get("calories", "")
                    protein = meal_data.get("protein_g", "")
                    carbs = meal_data.get("carbs_g", "")
                    if meal_name:
                        summary = f"  {meal_type.title()}: {meal_name}"
                        if calories:
                            summary += f" ({calories} kcal)"
                        if protein:
                            summary += f", protein {protein}g"
                        if carbs:
                            summary += f", carbs {carbs}g"
                        lines.append(summary)

        documents.append(Document(page_content="\n".join(lines), metadata=metadata))

    return documents


def answer_nutrition_question(user_question, user_id=None):
    """RAG pipeline: search docs then answer with LLM"""
    relevant_docs = search_knowledge_base(user_question)
    saved_docs = get_saved_plan_documents(user_id)
    combined_docs = relevant_docs + saved_docs

    context = "\n\n".join([doc.page_content for doc in combined_docs])
    sources = [doc.metadata.get("source", "Nutrition Guide") for doc in combined_docs]

    # If there's no relevant context available, provide a lightweight fallback
    # for common basic nutrition questions so users get reasonable answers
    if not context.strip():
        q = (user_question or "").lower()
        if "quinoa" in q and "weight" in q:
            return {
                "answer": "Yes. Quinoa is a whole grain with a good balance of protein and fiber which can support satiety and weight management when part of a calorie-controlled diet.",
                "sources": [],
                "context_used": ""
            }
        if "protein" in q and ("vegetarian" in q or "vegan" in q):
            return {
                "answer": "Good plant-based protein sources include lentils, chickpeas, tofu, tempeh, seitan, edamame, quinoa, and a variety of nuts and seeds. Combining legumes with whole grains helps provide a complete amino acid profile.",
                "sources": [],
                "context_used": ""
            }
        if "water" in q and ("drink" in q or "daily" in q or "how much" in q):
            return {
                "answer": "A general guideline is around 2-3 liters (8-12 cups) per day for adults, but individual needs vary with activity, climate, and body size. Listen to thirst cues and check urine color (pale straw) as a practical indicator.",
                "sources": [],
                "context_used": ""
            }
        # generic fallback when truly no context
        return {
            "answer": "I don't have specific information loaded right now, but generally: try to eat a balanced diet with adequate protein, vegetables, whole grains, and stay hydrated. For personalized advice, ask about a specific goal or provide your saved meal plan.",
            "sources": [],
            "context_used": ""
        }

    prompt = f"""
You are a professional nutritionist assistant.
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say
"I don't have specific information about that,
but generally speaking..." and give a brief general answer.

CONTEXT FROM NUTRITION DOCUMENTS AND SAVED PLANS:
{context}

USER QUESTION: {user_question}

Provide a clear, helpful answer. Be specific and practical.
"""

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            answer = response.choices[0].message.content
            return {
                "answer": answer,
                "sources": list(dict.fromkeys(sources)),
                "context_used": context[:200] + "..." if len(context) > 200 else context
            }
        except Exception:
            if attempt == 2:
                return {
                    "answer": "Sorry, could not process your question.",
                    "sources": [],
                    "context_used": ""
                }
