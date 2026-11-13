
import streamlit as st
import base64
from pathlib import Path

from ai.gemini_client import create_game_master, send_message


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="The Forgotten Library | CBI Investigation",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# 2. LOAD VERSION 1 BACKGROUND IMAGE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

possible_images = [
    ASSETS_DIR / "Version1.png",
    ASSETS_DIR / "Version1.jpg",
    ASSETS_DIR / "Version1.jpeg",
    ASSETS_DIR / "Version1.webp",
]

BACKGROUND_PATH = next(
    (path for path in possible_images if path.exists()),
    None
)

if BACKGROUND_PATH is None:
    st.error(
        "Version 1 background image was not found. "
        "Please check that Version1.png or Version1.jpg "
        "exists inside the assets folder."
    )
    st.stop()

with open(BACKGROUND_PATH, "rb") as image_file:
    encoded_image = base64.b64encode(
        image_file.read()
    ).decode("utf-8")

image_mime = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp"
}.get(BACKGROUND_PATH.suffix.lower(), "image/png")


# ==========================================================
# 3. CUSTOM CSS
# ==========================================================

st.markdown(
    f"""
    <style>

    /* ==============================================
       FULL SCREEN CBI TEAM BACKGROUND
    ============================================== */

    .stApp {{
        background:
            linear-gradient(
                rgba(12, 10, 11, 0.64),
                rgba(12, 10, 11, 0.76)
            ),
            url("data:{image_mime};base64,{encoded_image}");

        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;

        color: #eee5dc;
    }}

    /* HIDE DEFAULT STREAMLIT ELEMENTS */

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    header[data-testid="stHeader"] {{
        background: transparent;
    }}

    /* MAIN CONTENT */

    .block-container {{
        max-width: 1350px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    /* ==============================================
       SIDEBAR
    ============================================== */

    section[data-testid="stSidebar"] {{
        background: rgba(19, 16, 17, 0.94);
        border-right: 1px solid rgba(153, 91, 94, 0.7);
    }}

    section[data-testid="stSidebar"] > div {{
        background: transparent;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: #e4c4aa;
        font-family: Georgia, serif;
    }}

    /* ==============================================
       HEADINGS AND TEXT
    ============================================== */

    h1, h2, h3 {{
        color: #e8c7ac !important;
        font-family: Georgia, serif !important;
    }}

    p, li, label {{
        color: #eee3d8;
    }}

    hr {{
        border-color: rgba(145, 91, 91, 0.5) !important;
    }}

    div[data-testid="stCaptionContainer"] {{
        color: #c7b3a6;
    }}

    /* ==============================================
       HERO SECTION
    ============================================== */

    .detective-hero {{
        background: rgba(25, 19, 20, 0.87);
        border: 1px solid rgba(167, 106, 106, 0.85);
        border-radius: 16px;

        padding: 32px;
        margin-bottom: 24px;

        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.45);
        backdrop-filter: blur(8px);
    }}

    .hero-label {{
        color: #c99488;
        font-size: 12px;
        letter-spacing: 4px;
        text-transform: uppercase;
    }}

    .hero-title {{
        color: #f0d7bd;
        font-family: Georgia, serif;
        font-size: 38px;
        font-weight: bold;
        margin-top: 12px;
        margin-bottom: 8px;
    }}

    .hero-description {{
        color: #e1d0c2;
        font-size: 15px;
        margin-top: 12px;
        margin-bottom: 0;
    }}

    /* ==============================================
       CASE INFORMATION CARDS
    ============================================== */

    .case-card {{
        background: rgba(26, 21, 22, 0.91);
        border: 1px solid rgba(147, 91, 91, 0.75);
        border-radius: 12px;

        padding: 18px;
        min-height: 105px;

        backdrop-filter: blur(8px);
    }}

    .case-label {{
        color: #c5a99a;
        font-size: 12px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}

    .case-value {{
        color: #f0d2b5;
        font-family: Georgia, serif;
        font-size: 23px;
        margin-top: 10px;
    }}

    /* ==============================================
       SECTION HEADINGS
    ============================================== */

    .section-heading {{
        color: #e0bca4;
        font-family: Georgia, serif;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 12px;
    }}

    /* ==============================================
       INVESTIGATION PANEL
    ============================================== */

    .investigation-panel {{
        background: rgba(26, 22, 22, 0.91);
        border: 1px solid rgba(147, 91, 91, 0.7);
        border-radius: 13px;

        padding: 20px;
        margin: 15px 0;

        backdrop-filter: blur(8px);
    }}

    .investigation-panel p {{
        color: #e6d8cc;
    }}

    /* ==============================================
       CHAT MESSAGES
    ============================================== */

    div[data-testid="stChatMessage"] {{
        background: rgba(27, 23, 23, 0.94);
        border: 1px solid rgba(145, 91, 91, 0.7);
        border-radius: 12px;

        padding: 15px;
        margin-bottom: 12px;

        backdrop-filter: blur(8px);
    }}

    div[data-testid="stChatMessage"] p {{
        color: #f0e6dc;
    }}

    /* ==============================================
       CHAT INPUT
    ============================================== */

    div[data-testid="stChatInput"] {{
        background: rgba(26, 22, 22, 0.97);
        border: 1px solid #a56f70;
        border-radius: 12px;

        backdrop-filter: blur(8px);
    }}

    div[data-testid="stChatInput"] textarea {{
        color: #f5e9dc !important;
    }}

    div[data-testid="stChatInput"] textarea::placeholder {{
        color: #c5a99a !important;
    }}

    /* ==============================================
       SIDEBAR CASE NOTES
    ============================================== */

    .sidebar-note {{
        background: rgba(57, 39, 40, 0.7);
        border-left: 3px solid #a36c6d;
        border-radius: 5px;

        padding: 13px;
        margin: 12px 0;

        color: #e4d2c3;
        font-size: 13px;
        line-height: 1.8;
    }}

    /* ==============================================
       BUTTONS
    ============================================== */

    .stButton > button {{
        background: linear-gradient(
            135deg,
            #77464b,
            #4d3034
        );

        color: #fff0df;
        border: 1px solid #a87576;
        border-radius: 8px;

        font-weight: 600;
        transition: 0.2s ease;
    }}

    .stButton > button:hover {{
        background: linear-gradient(
            135deg,
            #965e62,
            #704044
        );

        color: white;
        border-color: #d09a91;
    }}

    /* ==============================================
       FOOTER
    ============================================== */

    .app-footer {{
        text-align: center;
        color: #c4a99b;
        font-size: 12px;
        letter-spacing: 2px;
        padding-top: 20px;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 4. SESSION STATE
# ==========================================================

if "chat" not in st.session_state:
    st.session_state.chat = create_game_master()

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================================
# 5. HELPER FUNCTION
# ==========================================================

def restart_game():

    st.session_state.chat = create_game_master()
    st.session_state.messages = []


# ==========================================================
# 6. SIDEBAR - CBI INVESTIGATION DASHBOARD
# ==========================================================

with st.sidebar:

    st.html("""
        <h2 style="font-family:Georgia;color:#e8c7ac;">
            🕵️ CBI INVESTIGATION
        </h2>
    """)

    st.caption("CONFIDENTIAL CASE FILE")

    st.divider()

    st.markdown(
        "<div class='section-heading'>📁 Case Information</div>",
        unsafe_allow_html=True
    )

    st.html("""
        <div class="sidebar-note">
            <b>CASE:</b> The Forgotten Library<br>
            <b>DIVISION:</b> California Bureau of Investigation<br>
            <b>TYPE:</b> Mystery Investigation<br>
            <b>STATUS:</b> Active<br>
            <b>INVESTIGATOR:</b> You
        </div>
    """)

    st.divider()

    st.markdown(
        "<div class='section-heading'>🔍 Investigation Guide</div>",
        unsafe_allow_html=True
    )

    st.write("• Observe your surroundings")
    st.write("• Question the Game Master")
    st.write("• Investigate suspicious objects")
    st.write("• Discover hidden clues")
    st.write("• Find a way to escape")

    st.divider()

    st.markdown(
        "<div class='section-heading'>📝 Case Notes</div>",
        unsafe_allow_html=True
    )

    st.caption(
        "Every detail could be important. "
        "Pay attention to the information you discover."
    )

    st.divider()

    if st.button(
        "🔄 Restart Investigation",
        use_container_width=True
    ):
        restart_game()
        st.rerun()

    st.caption("THE FORGOTTEN LIBRARY · VERSION 1")


# ==========================================================
# 7. MAIN HERO SECTION
# ==========================================================

hero_html = """
<div class="detective-hero">

    <div class="hero-label">
        A Psychological Mystery Adventure
    </div>

    <div class="hero-title">
        🕵️ THE FORGOTTEN LIBRARY
    </div>

    <p class="hero-description">
        Every room hides a secret. Every object tells a story.
        Trust your instincts, investigate carefully and find the truth.
    </p>

</div>
"""

st.html(hero_html)


# ==========================================================
# 8. CASE OVERVIEW
# ==========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.html("""
        <div class="case-card">
            <div class="case-label">Investigation</div>
            <div class="case-value">ACTIVE</div>
        </div>
    """)

with col2:

    st.html("""
        <div class="case-card">
            <div class="case-label">Environment</div>
            <div class="case-value">Library</div>
        </div>
    """)

with col3:

    st.html(f"""
        <div class="case-card">
            <div class="case-label">Conversation Records</div>
            <div class="case-value">{len(st.session_state.messages)}</div>
        </div>
    """)


# ==========================================================
# 9. INVESTIGATION BRIEF
# ==========================================================

st.markdown(
    "<div class='section-heading'>📂 Investigation Brief</div>",
    unsafe_allow_html=True
)

st.html("""
    <div class="investigation-panel">
        <strong>CASE SUMMARY</strong>

        <p>
            You find yourself trapped inside a mysterious library.
            Something is not right. The room contains objects,
            hidden clues and puzzles that may reveal a way out.
        </p>

        <p>
            Your task is to investigate the environment,
            communicate with the AI Game Master and uncover the truth.
        </p>
    </div>
""")


# ==========================================================
# 10. AI DETECTIVE CONVERSATION
# ==========================================================

st.markdown(
    "<div class='section-heading'>🗣️ Interrogate the Game Master</div>",
    unsafe_allow_html=True
)

st.caption(
    "Ask questions, investigate objects and describe your actions naturally."
)


# DISPLAY CHAT HISTORY

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ==========================================================
# 11. PLAYER INPUT AND GEMINI RESPONSE
# ==========================================================

prompt = st.chat_input(
    "Enter your investigation or question..."
)

if prompt and prompt.strip():

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        try:

            with st.spinner("🔍 Analysing your investigation..."):

                response = send_message(
                    st.session_state.chat,
                    prompt
                )

            st.markdown(response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

        except Exception as error:

            st.error(f"AI error: {error}")


# ==========================================================
# 12. FOOTER
# ==========================================================

st.html("""
    <hr>

    <div class="app-footer">
        THE FORGOTTEN LIBRARY · CBI INVESTIGATION DIVISION
    </div>
""")
