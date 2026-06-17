import streamlit as st
from dotenv import load_dotenv
from backend import build_rag_components
import re

load_dotenv()

st.set_page_config(
    page_title="YouTube RAG Chat",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CUSTOM CSS — Dark premium theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        html, body, [class*="css"] {
            font-family: 'Sora', sans-serif;
        }

        .stApp {
            background: #0B0D17;
            color: #E2E8F0;
        }

        section[data-testid="stSidebar"] {
            background: #11141F;
            border-right: 1px solid #1E2230;
        }

        h1 {
            font-weight: 800 !important;
            background: linear-gradient(90deg, #818CF8, #C084FC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            color: #94A3B8;
            font-size: 0.95rem;
            margin-top: -6px;
            margin-bottom: 18px;
        }

        [data-testid="stChatMessage"] {
            background: #151926;
            border: 1px solid #232838;
            border-radius: 14px;
            padding: 10px 16px;
            margin-bottom: 10px;
        }

        .stChatInput textarea {
            background-color: #151926 !important;
            color: #E2E8F0 !important;
            border-radius: 12px !important;
        }

        .stButton > button {
            background: linear-gradient(90deg, #6366F1, #818CF8);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            width: 100%;
        }

        .status-badge {
            display: inline-block;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .status-loaded {
            background: rgba(74, 222, 128, 0.12);
            color: #4ADE80;
            border: 1px solid rgba(74, 222, 128, 0.35);
        }

        .status-empty {
            background: rgba(248, 113, 113, 0.10);
            color: #F87171;
            border: 1px solid rgba(248, 113, 113, 0.35);
        }

        .empty-state {
            text-align: center;
            padding: 70px 20px;
            border: 1px dashed #2A2F42;
            border-radius: 16px;
            background: #11141F;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_youtube_thumbnail(url: str):
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return f"https://img.youtube.com/vi/{match.group(1)}/hqdefault.jpg"
    return None


# ---------------------------------------------------------------------------
# Session State
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chain" not in st.session_state:
    st.session_state.chain = None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎬 Video Setup")

    youtube_url = st.text_input(
        "YouTube URL", placeholder="https://youtube.com/watch?v=..."
    )

    col1, col2 = st.columns(2)
    with col1:
        load_clicked = st.button("Load Video", use_container_width=True)
    with col2:
        clear_clicked = st.button("Clear Chat", use_container_width=True)

    if youtube_url:
        thumb = get_youtube_thumbnail(youtube_url)
        if thumb:
            st.image(thumb, use_container_width=True)

    st.markdown("---")

    if st.session_state.chain:
        st.markdown('<span class="status-badge status-loaded">Video Loaded</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-badge status-empty">No Video Loaded</span>', unsafe_allow_html=True)

    st.markdown('<div class="footer-credit">Built by Sadiq Amin</div>', unsafe_allow_html=True)


# Load Video
if load_clicked:
    if not youtube_url:
        st.sidebar.warning("Please enter a YouTube URL first.")
    else:
        try:
            with st.spinner("Building RAG pipeline..."):
                st.session_state.chain = build_rag_components(youtube_url)
                st.session_state.messages = []
            st.sidebar.success("Video loaded successfully!")
        except Exception as e:
            error_msg = str(e)
            # Displaying custom errors in English
            if error_msg == "RATE_LIMIT_ERROR":
                st.sidebar.error("⚠️ You have reached the usage limit for loading video URLs. Please try again in 1 day.")
            elif error_msg == "NO_TRANSCRIPT_ERROR":
                st.sidebar.error("❌ No subtitles or transcripts are available for this video. Please try another link.")
            else:
                st.sidebar.error(error_msg)


# Clear Chat
if clear_clicked:
    st.session_state.messages = []
    st.rerun()


# ---------------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------------
st.title("🎥 YouTube RAG Chat")
st.markdown('<div class="subtitle">Chat with any YouTube video using its transcript</div>', unsafe_allow_html=True)

if st.session_state.chain is None and not st.session_state.messages:
    st.markdown(
        """
        <div class="empty-state">
            <h3>👈 Add a YouTube URL from the sidebar</h3>
            <p>After loading the video, you can ask questions based on its transcript.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Chat history
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
question = st.chat_input("Ask anything about the video...")

if question:
    if st.session_state.chain is None:
        st.warning("Please load a video first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""

        for chunk in st.session_state.chain.stream(question):
            if hasattr(chunk, "content"):
                full_response += chunk.content
                placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )