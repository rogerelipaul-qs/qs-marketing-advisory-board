import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(page_title="QuickStart Marketing Advisory Board", layout="wide")
st.title("🏛️ QuickStart Marketing Advisory Board")

# 1. Check API Key
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing `GEMINI_API_KEY` in Streamlit Secrets. Please add it under Settings > Secrets.")
    st.stop()

# 2. Resilient file reader
@st.cache_data
def load_context():
    def read_file(filename):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        return f"[Missing {filename}]"

    agent = read_file("advisory_board_agent.md")
    company = read_file("company_context.md")
    memory = read_file("board_memory.md")
    return f"{agent}\n\n=== COMPANY CONTEXT ===\n{company}\n\n=== SESSION MEMORY ===\n{memory}"

# 3. Chat session initialization
if "chat" not in st.session_state:
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.chat = client.chats.create(
            model="gemini-2.5-pro",
            config=types.GenerateContentConfig(
                system_instruction=load_context(),
                temperature=0.7,
            )
        )
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Failed to initialize Gemini client: {e}")
        st.stop()

# 4. Render message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. User prompt input
if prompt := st.chat_input("Submit a strategic proposal or asset brief for board review..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error querying board: {e}")