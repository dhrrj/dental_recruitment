import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(
    page_title="Dental Appointment Assistant",
    page_icon="🦷",
    layout="centered",
)

st.title("🦷 Dental Appointment Assistant")
st.caption("Ask about appointments, availability, bookings, cancellations, or rescheduling.")

with st.sidebar:
    st.subheader("Chat")
    st.caption(f"Backend API: {API_URL}")
    if st.button("Start a new chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("How can I help with your dental appointment?")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    payload = {"message": prompt}
    if st.session_state.conversation_id:
        payload["conversation_id"] = st.session_state.conversation_id

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json=payload,
                    timeout=120,
                )
                if not response.ok:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    st.error(f"Chat API error ({response.status_code}): {detail}")
                else:
                    data = response.json()
                    reply = data.get("reply")
                    conversation_id = data.get("conversation_id")
                    if not isinstance(reply, str) or not isinstance(conversation_id, str):
                        st.error("The chat API returned an unexpected response.")
                    else:
                        st.markdown(reply)
                        st.session_state.messages.extend(
                            [
                                {"role": "user", "content": prompt},
                                {"role": "assistant", "content": reply},
                            ]
                        )
                        st.session_state.conversation_id = conversation_id
            except requests.RequestException as exc:
                st.error(
                    "Could not reach the chat API. Make sure the FastAPI backend is "
                    f"running at {API_URL}. Details: {exc}"
                )
