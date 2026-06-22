import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from duckduckgo_search import DDGS
from datetime import datetime

st.set_page_config(page_title="My AI Assistant", page_icon="🚀")
st.title("🤖 My Personal AI Assistant")

# ====================== SETUP ======================
GROQ_API_KEY = "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"

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    api_key=GROQ_API_KEY
)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("AI Assistant")
    st.write("Web Search + Calculator + Time")
    if st.button("Clear Chat History"):
        st.session_state.messages = []

# ====================== CHAT HISTORY ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ====================== CHAT INPUT ======================
if prompt := st.chat_input("Kya poochna hai?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Soch raha hoon..."):

            # Simple Prompt (No bind_tools)
            system_prompt = SystemMessage(content="""
You are a helpful AI assistant. 
You can search the web, do calculations, and tell current time.
Give direct and clear answers.
""")

            response = llm.invoke([system_prompt] + 
                                [HumanMessage(content=prompt)])

            answer = response.content
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
