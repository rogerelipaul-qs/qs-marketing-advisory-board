import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(
    page_title="QuickStart Marketing Advisory Board",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 10px; margin-bottom: 12px; }
    .board-header {
        padding: 1.5rem;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 1.5rem;
    }
    .board-title { color: #f8fafc; font-size: 1.8rem; font-weight: 700; margin: 0; }
    .board-subtitle { color: #94a3b8; font-size: 0.95rem; margin-top: 0.35rem; }
    .member-badge {
        background-color: #1e293b;
        border-left: 3px solid #38bdf8;
        padding: 6px 12px;
        margin-bottom: 6px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #cbd5e1;
    }
    </style>
""", unsafe_allow_html=True)

# 1. API Key Validation
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing `GEMINI_API_KEY` in Streamlit Secrets. Please add it under Settings > Secrets.")
    st.stop()

# 2. File Context Reader
@st.cache_data
def load_context():
    def read_file(filename):
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        return ""

    agent = read_file("advisory_board_agent.md")
    company = read_file("company_context.md")
    memory = read_file("board_memory.md")
    return f"{agent}\n\n=== COMPANY CONTEXT ===\n{company}\n\n=== SESSION MEMORY ===\n{memory}"

# 3. Sidebar UI
with st.sidebar:
    st.image("https://www.quickstart.com/wp-content/uploads/2021/04/qs-logo.svg", width=180)
    st.markdown("### Active Advisory Board")
    
    members = [
        ("Marcus Vance", "Enterprise B2B & Corporate L&D"),
        ("Janet Kowalski", "Bootstrapper / P&L Hawk"),
        ("Elena Rostova", "Admissions & Field Reality"),
        ("Dr. Arthur Bell", "Higher-Ed & University Dean"),
        ("Sam Delgado", "Paid Media & Performance"),
        ("Nate Briggs", "Technical SEO & Topical Authority"),
        ("Priya Sharma", "Content Strategy & Storytelling"),
        ("Devon Reed", "RevOps & Data Attribution")
    ]
    for name, role in members:
        st.markdown(f"<div class='member-badge'><strong>{name}</strong><br><span style='color:#64748b;'>{role}</span></div>", unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Reset Deliberation", use_container_width=True):
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        st.rerun()

# 4. Header Banner
st.markdown("""
    <div class="board-header">
        <h1 class="board-title">🏛️ QuickStart Marketing Advisory Board</h1>
        <p class="board-subtitle">Autonomous strategic deliberation panel • 8 specialized perspectives • Mode 1 (Strategy) & Mode 2 (Document Review)</p>
    </div>
""", unsafe_allow_html=True)

# 5. Initialize Chat Client
if "chat" not in st.session_state:
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        st.session_state.chat = client.chats.create(
            model="gemini-3.1-pro-preview",
            config=types.GenerateContentConfig(
                system_instruction=load_context(),
                temperature=0.7,
            )
        )
        st.session_state.messages = []
    except Exception as e:
        st.error(f"Failed to initialize Gemini client: {e}")
        st.stop()

# 6. Render Message Thread
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 7. Starter Quick Prompts (if chat is fresh)
if not st.session_state.messages:
    st.markdown("##### Select a strategic dilemma to deliberate:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Paid Search vs. Enterprise ABM Budget Allocation", use_container_width=True):
            st.session_state.user_prompt_override = "We are debating allocating $40k between non-brand Google Ads for Cyber Bootcamp vs. a dedicated LinkedIn ABM push for enterprise cloud training. How should we allocate?"
            st.rerun()
    with col2:
        if st.button("🔍 Audit: 100% Job Guarantee Campaign Copy", use_container_width=True):
            st.session_state.user_prompt_override = "Please review this proposed ad headline: 'Get a Guaranteed 6-Figure Cybersecurity Job in 16 Weeks or 100% Tuition Refund.' Run a complete board review."
            st.rerun()

# Check for starter button click or chat input
prompt = st.session_state.pop("user_prompt_override", None) or st.chat_input("Submit a strategic proposal or asset for board review...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Board Chair triaging panel & convening advisors..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error querying board: {e}")