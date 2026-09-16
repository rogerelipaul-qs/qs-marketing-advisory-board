import streamlit as st
import os
from google import genai
from google.genai import types

st.set_page_config(
    page_title="QuickStart | Marketing Advisory Board",
    page_icon="assets/qs_mini_logo_2026.png" if os.path.exists("assets/qs_mini_logo.png") else ("qs_mini_logo.png" if os.path.exists("qs_mini_logo.png") else "🏛️"),
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESCAPE CURRENCY FOR STREAMLIT LATEX PARSER ---
def format_currency_markdown(text: str) -> str:
    """Escapes dollar signs so Streamlit treats amounts as currency rather than inline LaTeX."""
    return text.replace("$", "\\$")

# --- ADAPTIVE QUICKSTART THEME (LIGHT & DARK AUTOMATIC) ---
st.markdown("""
    <style>
    :root {
        --qs-blue: #0066CC;
        --qs-cyan: #00B4D8;
    }

    /* Clean, non-boxed header */
    .header-container {
        padding-bottom: 1.25rem;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid rgba(128, 128, 128, 0.2);
    }

    .board-title {
        color: var(--text-color) !important;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
        padding-top: 0.15rem;
    }

    .board-subtitle {
        color: rgba(128, 128, 128, 0.9) !important;
        font-size: 0.96rem;
        margin-top: 0.25rem;
        margin-bottom: 0;
    }

    /* Sidebar Personas */
    .member-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-left: 4px solid var(--qs-blue);
        padding: 8px 12px;
        margin-bottom: 8px;
        border-radius: 6px;
        transition: transform 0.15s ease-in-out;
    }

    .member-card:hover {
        border-left-color: var(--qs-cyan);
        transform: translateX(3px);
    }

    .member-name {
        font-weight: 600;
        font-size: 0.88rem;
        color: var(--text-color);
    }

    .member-role {
        font-size: 0.78rem;
        color: rgba(128, 128, 128, 0.85);
    }

    /* Chat message polish */
    .stChatMessage {
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid rgba(128, 128, 128, 0.15);
    }
    </style>
""", unsafe_allow_html=True)

# 1. API Key Validation
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Missing `GEMINI_API_KEY` in Streamlit Secrets. Please configure it in Settings > Secrets.")
    st.stop()

# 2. Resilient Context Loader
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

# 3. Sidebar Configuration
with st.sidebar:
    # Sidebar Logo Loader
    sidebar_logo_paths = ["assets/QS_full_logo_2026.png", "assets/quickstart_logo.png", "QS_full_logo_2026.png"]
    logo_displayed = False
    for path in sidebar_logo_paths:
        if os.path.exists(path):
            st.image(path, use_container_width=True)
            logo_displayed = True
            break
    if not logo_displayed:
        st.image("https://www.quickstart.com/wp-content/uploads/2021/04/qs-logo.svg", width=190)

    st.markdown("### Active Advisory Board")
    
    board_members = [
        ("Marcus Vance", "Enterprise B2B & Corporate L&D"),
        ("Janet Kowalski", "Bootstrapper / P&L Hawk"),
        ("Elena Rostova", "VP of Admissions & Field Reality"),
        ("Dr. Arthur Bell", "Higher-Ed & University Dean"),
        ("Sam Delgado", "Paid Media & Performance"),
        ("Nate Briggs", "Technical SEO & Search Authority"),
        ("Priya Sharma", "Content Strategy & Storytelling"),
        ("Devon Reed", "RevOps & Data Attribution")
    ]

    for name, role in board_members:
        st.markdown(f"""
            <div class="member-card">
                <div class="member-name">{name}</div>
                <div class="member-role">{role}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 Reset Board Session", use_container_width=True):
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state.chat
        st.rerun()

# 4. Header Banner with qs_mini_logo.png
mini_logo_paths = ["assets/qs_mini_logo.png", "qs_mini_logo.png"]
mini_logo_found = None
for path in mini_logo_paths:
    if os.path.exists(path):
        mini_logo_found = path
        break

if mini_logo_found:
    col_logo, col_title = st.columns([0.08, 0.92], vertical_alignment="center")
    with col_logo:
        st.image(mini_logo_found, width=65)
    with col_title:
        st.markdown("""
            <div>
                <h1 class="board-title">QuickStart Marketing Advisory Board</h1>
                <p class="board-subtitle">Autonomous Strategic Deliberation • 8 Specialized Personas • Enterprise B2B, B2C Bootcamps, Higher-Ed & B2G</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div>
            <h1 class="board-title">QuickStart Marketing Advisory Board</h1>
            <p class="board-subtitle">Autonomous Strategic Deliberation • 8 Specialized Personas • Enterprise B2B, B2C Bootcamps, Higher-Ed & B2G</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-container"></div>', unsafe_allow_html=True)

# 5. Chat Client Initialization
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
        st.error(f"Initialization error: {e}")
        st.stop()

# 6. Render Message Thread
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(format_currency_markdown(msg["content"]))

# 7. Quick Starter Dilemmas (if chat history is empty)
if not st.session_state.messages:
    st.markdown("##### Deliberate a strategic priority:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Paid Search vs. Enterprise ABM Budget Split", use_container_width=True):
            st.session_state.user_prompt_override = "We are debating allocating $40k between non-brand Google Ads for Cyber Bootcamp vs. a dedicated LinkedIn ABM push for enterprise cloud training. What is the board's recommendation?"
            st.rerun()
    with col2:
        if st.button("🔍 Asset Audit: Job Guarantee Campaign", use_container_width=True):
            st.session_state.user_prompt_override = "Please audit this proposed ad campaign headline: 'Get a Guaranteed 6-Figure Cybersecurity Job in 16 Weeks or 100% Tuition Refund.' Provide an executive assessment."
            st.rerun()

# 8. User Interaction Handler
prompt = st.session_state.pop("user_prompt_override", None) or st.chat_input("Submit a strategic proposal or asset for board review...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(format_currency_markdown(prompt))

    with st.chat_message("assistant"):
        with st.spinner("Board Chair triaging panel & convening advisors..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                formatted_response = format_currency_markdown(response.text)
                st.markdown(formatted_response)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Board query error: {e}")