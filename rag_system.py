import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from groq import Groq

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

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    print(f"✅ Loaded {len(chunks)} chunks into knowledge base!")
    return vector_store


def search_knowledge_base(query, top_k=3):
    """Search for relevant nutrition info"""
    store = load_knowledge_base()
    results = store.similarity_search(query, k=top_k)
    return results


def answer_nutrition_question(user_question):
    """RAG pipeline: search docs then answer with LLM"""
    relevant_docs = search_knowledge_base(user_question)
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    sources = [doc.metadata.get("source", "Nutrition Guide") for doc in relevant_docs]

    prompt = f"""
You are a professional nutritionist assistant.
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say
"I don't have specific information about that,
but generally speaking..." and give a brief general answer.

CONTEXT FROM NUTRITION DOCUMENTS:
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
