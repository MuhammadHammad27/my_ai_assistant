import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langgraph.prebuilt import create_react_agent
from duckduckgo_search import DDGS
from datetime import datetime
import tempfile, os, re

# =====================================
# Page Config
# =====================================
st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AI Assistant")
st.caption("PDF + Web Search + Calculator + Memory")

# =====================================
# Sidebar
# =====================================
with st.sidebar:
    st.header("⚙️ Settings")
    openrouter_key = st.text_input("OpenRouter API Key", type="password", placeholder="sk-or-...")
    st.divider()
    uploaded_file = st.file_uploader("📄 PDF Upload karo", type="pdf")
    st.divider()
    if st.button("🗑️ Chat Clear"):
        st.session_state.clear()
        st.rerun()

# =====================================
# Session State
# =====================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# =====================================
# PDF Load
# =====================================
if uploaded_file and st.session_state.vectorstore is None:
    with st.spinner("📄 PDF load ho raha hai..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(uploaded_file.read())
            tmp_path = f.name
        chunks = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=50).split_documents(
            PyPDFLoader(tmp_path).load()
        )
        st.session_state.vectorstore = FAISS.from_documents(
            chunks, HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        )
        os.unlink(tmp_path)
    st.sidebar.success("✅ PDF Ready!")

# =====================================
# Tools
# =====================================
@tool
def pdf_search(query: str) -> str:
    """Search information from uploaded PDF document"""
    if not st.session_state.vectorstore:
        return "PDF upload nahi hua abhi."
    docs = st.session_state.vectorstore.similarity_search(query, k=3)
    return "\n\n".join([d.page_content for d in docs])

@tool
def web_search(query: str) -> str:
    """Search latest information from internet"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            return "\n".join([r["body"] for r in results])
    except:
        return "Web search fail ho gaya."

@tool
def calculator(expression: str) -> str:
    """Calculate math expressions like 2+2, 10*5"""
    try:
        clean = re.findall(r"[\d\+\-\*\/\(\)\. ]+", expression)[0]
        return f"= {eval(clean.strip())}"
    except:
        return "Invalid expression"

@tool
def current_time(query: str) -> str:
    """Get current date and time"""
    return datetime.now().strftime("%d %B %Y, %H:%M:%S")

tools = [pdf_search, web_search, calculator, current_time]

# =====================================
# Chat Display
# =====================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# =====================================
# Chat Input
# =====================================
if prompt := st.chat_input("Kuch poochho..."):

    if not openrouter_key:
        st.error("⚠️ OpenRouter API key daalo sidebar mein!")
        st.stop()

    # LLM — OpenRouter ka free Mistral (tool calling support karta hai)
    llm = ChatOpenAI(
         model="meta-llama/llama-3.3-70b-instruct:free",  # ← yeh try karo
         api_key=openrouter_key,
         base_url="https://openrouter.ai/api/v1"
)


    agent = create_react_agent(llm, tools)

    # User message show
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Agent response
    with st.chat_message("assistant"):
        with st.spinner("Soch raha hoon..."):
            try:
                result = agent.invoke({"messages": [HumanMessage(content=prompt)]})
                response = result["messages"][-1].content
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"❌ Error: {e}")
