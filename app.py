import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from duckduckgo_search import DDGS
import json
from datetime import datetime

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="⚡ NexusAI — Smart Assistant",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ====================== CUSTOM CSS ======================
st.markdown("""
<style>
    /* ---------- Import Google Font ---------- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ---------- Global Styles ---------- */
    *, .stApp {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
    }

    /* ---------- Header ---------- */
    .hero-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }

    .hero-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #00d2ff, #7b2ff7, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        animation: glow 3s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from { filter: brightness(1); }
        to { filter: brightness(1.3); }
    }

    .hero-subtitle {
        color: #8b8fa3;
        font-size: 1rem;
        font-weight: 400;
        letter-spacing: 2px;
    }

    /* ---------- Mode Cards ---------- */
    .mode-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
        letter-spacing: 0.5px;
    }

    .mode-chat { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
    .mode-search { background: linear-gradient(135deg, #f093fb, #f5576c); color: white; }
    .mode-creative { background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; }
    .mode-precise { background: linear-gradient(135deg, #43e97b, #38f9d7); color: #1a1a2e; }
    .mode-pdf { background: linear-gradient(135deg, #fa709a, #fee140); color: #1a1a2e; }

    /* ---------- Sidebar Styling ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a3e 0%, #16213e 100%) !important;
        border-right: 1px solid rgba(123, 47, 247, 0.3);
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e0ff !important;
    }

    /* ---------- Chat Messages ---------- */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(123, 47, 247, 0.15) !important;
        border-radius: 16px !important;
        padding: 1rem !important;
        margin-bottom: 0.8rem !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stChatMessage"]:hover {
        border-color: rgba(123, 47, 247, 0.4) !important;
        box-shadow: 0 4px 20px rgba(123, 47, 247, 0.1) !important;
    }

    /* ---------- Chat Input ---------- */
    [data-testid="stChatInput"] textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(123, 47, 247, 0.3) !important;
        border-radius: 12px !important;
        color: #e0e0ff !important;
        font-size: 1rem !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: #7b2ff7 !important;
        box-shadow: 0 0 15px rgba(123, 47, 247, 0.3) !important;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        letter-spacing: 0.5px !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(118, 75, 162, 0.4) !important;
    }

    /* ---------- Radio Buttons ---------- */
    .stRadio > div {
        gap: 0.5rem !important;
    }

    /* ---------- Expander ---------- */
    .streamlit-expanderHeader {
        background: rgba(123, 47, 247, 0.1) !important;
        border-radius: 10px !important;
        color: #c0c0ff !important;
    }

    /* ---------- Divider ---------- */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(123, 47, 247, 0.5), transparent);
        margin: 1rem 0;
    }

    /* ---------- Stats Card ---------- */
    .stats-card {
        background: rgba(123, 47, 247, 0.1);
        border: 1px solid rgba(123, 47, 247, 0.2);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }

    .stats-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #7b2ff7;
    }

    .stats-label {
        font-size: 0.8rem;
        color: #8b8fa3;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ---------- Search Result Cards ---------- */
    .search-result {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 210, 255, 0.2);
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }

    .search-result:hover {
        border-color: rgba(0, 210, 255, 0.5);
    }

    /* ---------- File Uploader ---------- */
    [data-testid="stFileUploader"] {
        background: rgba(123, 47, 247, 0.05) !important;
        border: 1px dashed rgba(123, 47, 247, 0.3) !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stFileUploader"] section {
        padding: 0 !important;
    }

    /* ---------- Footer ---------- */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #4a4a6a;
        font-size: 0.75rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ====================== HEADER ======================
st.markdown("""
<div class="hero-header">
    <h1>⚡ NexusAI</h1>
    <p class="hero-subtitle">YOUR INTELLIGENT AI COMPANION</p>
</div>
""", unsafe_allow_html=True)

# ====================== API KEY ======================
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = "AIzaSy..." # Fallback won't work in prod, user must provide via secrets

# ====================== SIDEBAR ======================
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # AI Mode Selection
    st.markdown("### 🎯 AI Mode")
    mode = st.radio(
        "Select mode:",
        ["💬 Chat", "🔍 Web Search", "🎨 Creative", "🎯 Precise"],
        label_visibility="collapsed"
    )

    # Temperature based on mode
    mode_configs = {
        "💬 Chat": {"temp": 0.4, "system": "You are a helpful, friendly AI assistant. Give clear and concise answers."},
        "🔍 Web Search": {"temp": 0.3, "system": "You are a research assistant. Analyze the provided web search results carefully and give a comprehensive, well-structured answer based on them. Cite sources when possible."},
        "🎨 Creative": {"temp": 0.9, "system": "You are a creative genius AI. Be imaginative, poetic, and think outside the box. Use metaphors, analogies, and creative language."},
        "🎯 Precise": {"temp": 0.1, "system": "You are a precise, factual AI assistant. Give exact, concise, and technically accurate answers. No fluff, just facts."},
    }

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Model Selection
    st.markdown("### 🤖 Model")
    model_choice = st.selectbox(
        "Select model:",
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.0-pro"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # PDF Upload
    st.markdown("### 📄 PDF Upload")
    uploaded_file = st.file_uploader("Upload a PDF to chat with it", type=["pdf"], label_visibility="collapsed")

    pdf_text = ""
    if uploaded_file is not None:
        try:
            import PyPDF2
            import io
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() or ""
            st.success(f"✅ PDF loaded! ({len(pdf_reader.pages)} pages)")
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Chat Stats
    st.markdown("### 📊 Chat Stats")
    msg_count = len([m for m in st.session_state.get("messages", []) if m["role"] == "user"])
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{msg_count}</div>
            <div class="stats-label">Messages</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-number">{len(st.session_state.get("messages", []))}</div>
            <div class="stats-label">Total</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Actions
    st.markdown("### 🛠️ Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("📥 Export Chat", use_container_width=True):
            if st.session_state.get("messages"):
                chat_export = {
                    "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_messages": len(st.session_state.messages),
                    "messages": st.session_state.messages
                }
                st.download_button(
                    "⬇️ Download JSON",
                    json.dumps(chat_export, indent=2, ensure_ascii=False),
                    file_name=f"nexusai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.info("No messages to export!")

    # Footer
    st.markdown("""
    <div class="footer">
        Built with ❤️ by Muhammad Hammad<br>
        Powered by Google Gemini & LangChain
    </div>
    """, unsafe_allow_html=True)

# ====================== ACTIVE MODE BADGE ======================
mode_classes = {
    "💬 Chat": "mode-chat",
    "🔍 Web Search": "mode-search",
    "🎨 Creative": "mode-creative",
    "🎯 Precise": "mode-precise",
}
st.markdown(f"""
<div style="text-align: center; margin-bottom: 1rem;">
    <span class="mode-badge {mode_classes[mode]}">{mode} Mode Active</span>
    {"<span class='mode-badge mode-pdf'>📄 PDF Loaded</span>" if pdf_text else ""}
</div>
""", unsafe_allow_html=True)

# ====================== LLM INIT ======================
config = mode_configs[mode]
llm = ChatGoogleGenerativeAI(
    model=model_choice,
    temperature=config["temp"],
    google_api_key=api_key
)

# ====================== WEB SEARCH FUNCTION ======================
def web_search(query, num_results=5):
    """Search the web using DuckDuckGo and return results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            return results
    except Exception as e:
        return [{"title": "Search Error", "body": str(e), "href": ""}]

def format_search_results(results):
    """Format search results into a readable string for the LLM."""
    formatted = "📊 **Web Search Results:**\n\n"
    for i, r in enumerate(results, 1):
        formatted += f"**{i}. {r.get('title', 'No Title')}**\n"
        formatted += f"{r.get('body', 'No description')}\n"
        formatted += f"🔗 {r.get('href', '')}\n\n"
    return formatted

# ====================== CHAT HISTORY ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ====================== CHAT INPUT ======================
if prompt := st.chat_input("✨ Ask me anything..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build context
    with st.chat_message("assistant"):
        system_content = config["system"]
        extra_context = ""

        # Web Search Mode
        if mode == "🔍 Web Search":
            with st.spinner("🔍 Searching the web..."):
                results = web_search(prompt)
                search_text = format_search_results(results)

                # Show search results in expander
                with st.expander("📋 Search Results", expanded=False):
                    for r in results:
                        st.markdown(f"""
                        <div class="search-result">
                            <strong>{r.get('title', '')}</strong><br>
                            <small>{r.get('body', '')}</small><br>
                            <a href="{r.get('href', '')}" target="_blank">🔗 Source</a>
                        </div>
                        """, unsafe_allow_html=True)

                extra_context = f"\n\nHere are the web search results for the query '{prompt}':\n\n{search_text}\n\nBased on these results, provide a comprehensive answer."

        # PDF Context
        if pdf_text:
            pdf_snippet = pdf_text[:3000]
            extra_context += f"\n\nThe user has uploaded a PDF document. Here is the content:\n\n{pdf_snippet}\n\nAnswer questions based on this document when relevant."

        # Build message history for context (last 10 messages)
        history_messages = []
        history_messages.append(SystemMessage(content=system_content + extra_context))

        for msg in st.session_state.messages[-10:]:
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                from langchain_core.messages import AIMessage
                history_messages.append(AIMessage(content=msg["content"]))

        # Generate response
        with st.spinner("⚡ Generating response..."):
            response = llm.invoke(history_messages)
            answer = response.content
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
