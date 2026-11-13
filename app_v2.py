
import streamlit as st
import base64
import textwrap
from pathlib import Path

from game.game_state import create_initial_state
from game.game_engine import (
    process_player_action,
    process_intent
)

from ai.gemini_client import (
    narrate_outcome,
    interpret_player_intent
)


# ==========================================================
# 1. PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="The Forgotten Library",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================================
# 2. LOAD BACKGROUND IMAGE
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

BACKGROUND_PATH = (
    BASE_DIR / "assets" / "Background.png"
)

if not BACKGROUND_PATH.exists():
    st.error(
        f"Background image not found: {BACKGROUND_PATH}"
    )
    st.stop()

with open(BACKGROUND_PATH, "rb") as image_file:
    encoded_image = base64.b64encode(
        image_file.read()
    ).decode("utf-8")


# ==========================================================
# 3. CUSTOM CSS
# ==========================================================

st.markdown(
    f"""
    <style>

    /* FULL SCREEN BACKGROUND */

    .stApp {{
        background:
            linear-gradient(
                rgba(10, 8, 5, 0.48),
                rgba(10, 8, 5, 0.58)
            ),
            url("data:image/png;base64,{encoded_image}");

        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;

        color: #f5ead8;
    }}

    /* HIDE STREAMLIT DEFAULT ELEMENTS */

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
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    /* SIDEBAR */

    section[data-testid="stSidebar"] {{
        background: rgba(15, 11, 7, 0.90);
        border-right: 1px solid rgba(204, 155, 78, 0.65);
    }}

    section[data-testid="stSidebar"] > div {{
        background: transparent;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: #eac77e;
        font-family: Georgia, serif;
    }}

    /* HEADINGS AND TEXT */

    h1, h2, h3 {{
        color: #f0ce88 !important;
        font-family: Georgia, serif !important;
    }}

    p, li, label {{
        color: #f0e5d3;
    }}

    div[data-testid="stCaptionContainer"] {{
        color: #d1b991;
    }}

    hr {{
        border-color: rgba(202, 157, 87, 0.4) !important;
    }}

    /* HERO HEADER */

    .hero {{
        background: rgba(17, 12, 7, 0.82);
        border: 1px solid rgba(204, 155, 78, 0.8);
        border-radius: 16px;
        padding: 28px 30px;
        margin-bottom: 22px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(8px);
    }}

    .hero-subtitle {{
        color: #d5b77e;
        font-size: 13px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }}

    .hero-title {{
        color: #f2d18d;
        font-family: Georgia, serif;
        font-size: 38px;
        font-weight: bold;
        margin-top: 8px;
        margin-bottom: 8px;
    }}

    .hero-description {{
        color: #eee0c9;
        font-size: 15px;
        margin-bottom: 0;
    }}

    /* METRIC CARDS */

    div[data-testid="stMetric"] {{
        background: rgba(20, 15, 9, 0.88);
        border: 1px solid rgba(190, 144, 70, 0.7);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(8px);
    }}

    div[data-testid="stMetricLabel"] {{
        color: #d9c29c;
    }}

    div[data-testid="stMetricValue"] {{
        color: #f0cc80;
    }}

    /* SECTION HEADINGS */

    .section-heading {{
        color: #f0cc80;
        font-family: Georgia, serif;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 12px;
    }}

    /* CHAT AREA */

    div[data-testid="stChatMessage"] {{
        background: rgba(20, 15, 10, 0.90);
        border: 1px solid rgba(174, 127, 62, 0.65);
        border-radius: 13px;
        padding: 16px;
        margin-bottom: 12px;
        backdrop-filter: blur(8px);
    }}

    div[data-testid="stChatMessage"] p {{
        color: #f5ead8;
    }}

    /* CHAT INPUT */

    div[data-testid="stChatInput"] {{
        background: rgba(20, 15, 9, 0.96);
        border: 1px solid #c49a55;
        border-radius: 12px;
        backdrop-filter: blur(8px);
    }}

    div[data-testid="stChatInput"] textarea {{
        color: #fff2dd !important;
    }}

    div[data-testid="stChatInput"] textarea::placeholder {{
        color: #c6ae88 !important;
    }}

    /* INVENTORY */

    .inventory-item {{
        background: rgba(91, 64, 30, 0.45);
        border: 1px solid rgba(194, 148, 76, 0.6);
        border-radius: 8px;
        padding: 10px 12px;
        margin: 7px 0;
        color: #f0d6a6;
    }}

    /* PUZZLE STATUS */

    .puzzle-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(38, 29, 18, 0.88);
        border: 1px solid rgba(151, 116, 66, 0.5);
        border-radius: 8px;
        padding: 9px 11px;
        margin-bottom: 8px;
        color: #f0e4d0;
    }}

    .puzzle-solved {{
        border-color: #8da66c;
        color: #c8e5a7;
    }}

    .puzzle-pending {{
        color: #ddc9a8;
    }}

    /* ROOM OBJECTS */

    .object-row {{
        color: #f0e5d3;
        padding: 7px 2px;
        border-bottom: 1px solid rgba(195, 151, 84, 0.25);
        font-size: 13px;
    }}

    /* MISSION BANNER */

    .status-banner {{
        background: rgba(24, 17, 10, 0.90);
        border: 1px solid #bd904b;
        color: #f0d49b;
        border-radius: 10px;
        padding: 14px 16px;
        margin: 14px 0 22px 0;
        backdrop-filter: blur(8px);
    }}

    /* COMPLETION PANEL */

    .completion {{
        background: rgba(28, 42, 21, 0.93);
        border: 1px solid #9bb779;
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        margin: 20px 0;
    }}

    .completion h2 {{
        color: #d5e9b7 !important;
    }}

    /* BUTTONS */

    .stButton > button {{
        background: linear-gradient(
            135deg,
            #a87935,
            #76501f
        );
        color: #fff5df;
        border: 1px solid #d0a45c;
        border-radius: 9px;
        font-weight: 600;
        transition: 0.2s ease;
    }}

    .stButton > button:hover {{
        background: linear-gradient(
            135deg,
            #c69a50,
            #98703a
        );
        color: white;
        border-color: #f0cf8b;
    }}

    /* PROGRESS BAR */

    div[data-testid="stProgressBar"] > div > div {{
        background: #c69b51;
    }}

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# 4. SESSION STATE
# ==========================================================

if "game_state" not in st.session_state:
    st.session_state.game_state = create_initial_state()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Welcome to The Forgotten Library!\n\n"
                "You wake up in a mysterious library. "
                "Investigate the desk, bookshelf, drawer, "
                "painting and exit door. Discover clues, "
                "solve the puzzles and find your way out.\n\n"
                "Type **look around** to begin."
            )
        }
    ]

state = st.session_state.game_state


# ==========================================================
# 5. HELPER FUNCTIONS
# ==========================================================

def get_object_status(obj, details):

    if obj in ("drawer", "door"):
        return (
            "Unlocked"
            if details["unlocked"]
            else "Locked"
        )

    return (
        "Examined"
        if details.get("examined")
        else "Not examined"
    )


def restart_game():

    st.session_state.game_state = create_initial_state()

    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "A new game begins. You are trapped inside "
                "The Forgotten Library.\n\n"
                "What would you like to investigate?"
            )
        }
    ]


# ==========================================================
# 6. SIDEBAR DASHBOARD
# ==========================================================

with st.sidebar:

    st.markdown(
        textwrap.dedent("""
            <h2 style="font-family:Georgia; color:#f0cc80;">
                🔐 THE LIBRARY
            </h2>
        """),
        unsafe_allow_html=True
    )

    st.caption("YOUR ESCAPE DASHBOARD")

    st.divider()

    # INVENTORY

    st.markdown(
        "<div class='section-heading'>🎒 Inventory</div>",
        unsafe_allow_html=True
    )

    if state["inventory"]:

        for item in state["inventory"]:

            st.markdown(
                f"""
                <div class="inventory-item">
                    ✦ {item.replace('_', ' ').title()}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.caption("Nothing collected yet.")

    st.divider()

    # PUZZLE PROGRESS

    st.markdown(
        "<div class='section-heading'>🧩 Puzzle Progress</div>",
        unsafe_allow_html=True
    )

    puzzles = [
        ("Desk Riddle", "desk_clue"),
        ("Bookshelf Code", "bookshelf"),
        ("Painting Secret", "painting")
    ]

    for label, puzzle in puzzles:

        solved = puzzle in state["solved_puzzles"]

        if solved:
            icon = "✅"
            css_class = "puzzle-solved"
            status = "Solved"
        else:
            icon = "🔒"
            css_class = "puzzle-pending"
            status = "Pending"

        st.markdown(
            f"""
            <div class="puzzle-item {css_class}">
                <span>{icon} {label}</span>
                <small>{status}</small>
            </div>
            """,
            unsafe_allow_html=True
        )

    progress = len(state["solved_puzzles"]) / 3

    st.progress(
        progress,
        text=f"{int(progress * 100)}% completed"
    )

    st.divider()

    # ROOM OBJECTS

    st.markdown(
        "<div class='section-heading'>🏛️ Room Objects</div>",
        unsafe_allow_html=True
    )

    for obj, details in state["objects"].items():

        status = get_object_status(obj, details)

        icon = (
            "🟢"
            if status in ("Unlocked", "Examined")
            else "⚪"
        )

        st.markdown(
            f"""
            <div class="object-row">
                {icon} &nbsp;
                <b>{obj.title()}</b>
                <span style="float:right;color:#d0b58a;">
                    {status}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()

    # GAME STATUS

    st.markdown(
        "<div class='section-heading'>📜 Game Status</div>",
        unsafe_allow_html=True
    )

    if state["escaped"]:
        st.success("Escape completed!")
    else:
        st.info("You are still trapped.")

    st.divider()

    # RESTART BUTTON

    if st.button(
        "🔄 Restart Adventure",
        use_container_width=True
    ):
        restart_game()
        st.rerun()

    st.caption("Version 2 · AI Escape Room")





# ==========================================================
# 7. MAIN HERO HEADER
# ==========================================================

hero_html = """
<div class="hero">
    <div class="hero-subtitle">
        An Interactive Mystery Adventure
    </div>
    <div class="hero-title">
        🔐 The Forgotten Library
    </div>
    <p class="hero-description">
        Five objects. Three puzzles. One way out.
        Explore the library, uncover its secrets and escape.
    </p>
</div>
"""

st.html(hero_html)



# ==========================================================
# 8. GAME OVERVIEW METRICS
# ==========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Puzzles Solved",
        f"{len(state['solved_puzzles'])} / 3"
    )

with col2:
    st.metric(
        "Items Collected",
        len(state["inventory"])
    )

with col3:
    st.metric(
        "Game Status",
        "Escaped" if state["escaped"] else "In Progress"
    )



# ==========================================================
# 9. ESCAPE STATUS
# ==========================================================

if state["escaped"]:

    completion_html = """
    <div class="completion">
        <h2>🎉 YOU ESCAPED!</h2>

        <p>
            The ancient library has released you.
            You solved its mysteries and discovered the way out.
        </p>

        <p>
            <strong>Congratulations, Explorer!</strong>
        </p>
    </div>
    """

    st.html(completion_html)

    # Show balloons only once per completed game.
    if not st.session_state.get("escape_celebrated", False):
        st.balloons()
        st.session_state.escape_celebrated = True

else:

    st.session_state.escape_celebrated = False

    mission_html = """
    <div class="status-banner">
        🕯️ <strong>Current Mission:</strong>
        Investigate the library and discover how to unlock the exit.
    </div>
    """

    st.html(mission_html)



# ==========================================================
# 10. GAME MASTER CHAT
# ==========================================================

st.markdown(
    "<div class='section-heading'>📖 Game Master — Your Adventure</div>",
    unsafe_allow_html=True
)

st.caption(
    "Describe your actions naturally. "
    "The Game Master will guide the story."
)

# DISPLAY CHAT HISTORY

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ==========================================================
# 11. PLAYER INPUT AND ACTION PROCESSING
# ==========================================================

if not state["escaped"]:

    player_input = st.chat_input(
        "What would you like to do? e.g. Examine the desk..."
    )

    if player_input is not None and player_input.strip():

        # STEP 1: STORE PLAYER MESSAGE

        st.session_state.messages.append(
            {
                "role": "user",
                "content": player_input
            }
        )

        # STEP 2: IDENTIFY AND VALIDATE ACTION

        try:

            with st.spinner("🔍 Understanding your action..."):

                intent = interpret_player_intent(player_input)

            if (
                isinstance(intent, dict)
                and intent.get("action") not in (None, "unknown")
            ):

                success, approved_result = process_intent(
                    state,
                    intent
                )

            else:

                success, approved_result = process_player_action(
                    state,
                    player_input
                )

        except Exception as error:

            print(f"Intent recognition error: {error}")

            # FALLBACK TO PYTHON ENGINE

            success, approved_result = process_player_action(
                state,
                player_input
            )

        # STEP 3: GENERATE GAME MASTER RESPONSE

        if success:

            try:

                with st.spinner("📜 Game Master is responding..."):

                    game_response = narrate_outcome(
                        approved_result
                    )

                if not game_response:
                    game_response = str(approved_result)

            except Exception as error:

                print(f"Narration error: {error}")

                game_response = str(approved_result)

        else:

            game_response = str(approved_result)

        # STEP 4: STORE ASSISTANT RESPONSE

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": game_response
            }
        )

        # STEP 5: REFRESH APPLICATION

        st.rerun()
