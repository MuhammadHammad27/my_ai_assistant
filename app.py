import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from duckduckgo_search import DDGS

st.set_page_config(page_title="My AI", page_icon="🚀", layout="centered")
st.title("🤖 My Personal AI Assistant")
st.caption("Web Search • Smart AI")

# ====================== LLM ======================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    api_key=st.secrets.get("GROQ_API_KEY") or "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"
)

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("About")
    st.write("Built in 14 Days")
    if st.button("Clear Chat"):
        st.session_state.messages = []

# ====================== CHAT ======================
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Kya poochna hai?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Soch raha hoon..."):
            response = llm.invoke([
                SystemMessage(content="You are a helpful AI assistant."),
                HumanMessage(content=prompt)
            ])
            answer = response.content
            st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
