import streamlit as st

from ai.gemini_client import create_game_master, send_message

st.set_page_config(
    page_title="The Forgotten Library",
    page_icon="🔐",
    layout="centered"
)

st.title("🔐 The Forgotten Library")

st.write(
    "You are trapped inside a mysterious library. "
    "Investigate the room, solve puzzles and escape!"
)

if "chat" not in st.session_state:
    st.session_state.chat = create_game_master()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if prompt := st.chat_input("What would you like to do?"):

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        try:
            response = send_message(
                st.session_state.chat,
                prompt
            )

            st.write(response)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

        except Exception as error:
            st.error(f"AI error: {error}")

if st.button("Restart Game"):
    st.session_state.clear()
    st.rerun()