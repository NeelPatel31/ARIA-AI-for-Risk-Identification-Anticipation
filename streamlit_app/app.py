import os
import queue
import sys
import threading
import uuid
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

from streamlit_app.api_client import iter_stream_chat
from streamlit_app.render import (
    format_tool_result_event,
    render_ai_text,
    render_message,
)

API_BASE = os.getenv("API_BASE", "http://localhost:4000")
POLL_INTERVAL_SECONDS = 0.25


def _init_state() -> None:
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "active_run" not in st.session_state:
        st.session_state.active_run = None


def _new_session() -> None:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.active_run = None


def _consume_events(
    api_base: str,
    session_id: str,
    user_query: str,
    events: queue.Queue,
) -> None:
    try:
        for packet in iter_stream_chat(api_base, session_id, user_query):
            events.put(packet)
    except Exception as exc:
        events.put({"event": "error", "data": {"message": str(exc)}})
        events.put({"event": "stream.end", "data": {}})


def _flush_ai_text(run: dict) -> None:
    text = run["ai_text_buffer"]
    if text:
        run["turn_messages"].append({"type": "ai_text", "content": text})
        run["ai_text_buffer"] = ""


def _apply_packet(run: dict, packet: dict) -> bool:
    event = packet.get("event")
    data = packet.get("data", {})

    if event == "user.message":
        run["user_message"]["text"] = data.get("text", run["user_message"]["text"])
    elif event == "ai.tool_call":
        streamed_text = run["ai_text_buffer"]
        _flush_ai_text(run)
        run["turn_messages"].append(
            {
                "type": "ai_tool_call",
                "text": None if streamed_text else data.get("text"),
                "tool_calls": data.get("tool_calls", []),
            }
        )
    elif event == "tool.result":
        _flush_ai_text(run)
        run["turn_messages"].append(format_tool_result_event(data))
    elif event == "ai.token":
        run["ai_text_buffer"] += data.get("text", "")
    elif event == "error":
        run["error"] = data.get("message", "Unknown error")
    elif event == "stream.end":
        _flush_ai_text(run)
        return True
    return False


@st.fragment(run_every=POLL_INTERVAL_SECONDS)
def _render_active_run() -> None:
    run = st.session_state.active_run
    if run is None:
        return

    ended = False
    while True:
        try:
            packet = run["events"].get_nowait()
        except queue.Empty:
            break
        ended = _apply_packet(run, packet) or ended

    with st.chat_message("assistant"):
        if run["error"]:
            st.error(run["error"])

        for message in run["turn_messages"]:
            render_message(message)
        if run["ai_text_buffer"]:
            render_ai_text(run["ai_text_buffer"])

    if ended:
        st.session_state.messages.extend(run["turn_messages"])
        st.session_state.active_run = None
        st.rerun()


def _start_run(user_text: str) -> None:
    user_message = {"type": "user", "text": user_text}
    events: queue.Queue = queue.Queue()
    worker = threading.Thread(
        target=_consume_events,
        args=(API_BASE, st.session_state.session_id, user_text, events),
        daemon=True,
    )
    st.session_state.messages.append(user_message)
    st.session_state.active_run = {
        "events": events,
        "worker": worker,
        "user_message": user_message,
        "turn_messages": [],
        "ai_text_buffer": "",
        "error": None,
    }
    worker.start()


def main() -> None:
    st.set_page_config(page_title="ARIA", layout="wide")
    _init_state()

    col_title, col_action = st.columns([4, 1])
    with col_title:
        st.title("ARIA")
        st.caption(f"Session ID: {st.session_state.session_id}")
    with col_action:
        if st.button(
            "New Session",
            use_container_width=True,
            disabled=st.session_state.active_run is not None,
        ):
            _new_session()
            st.rerun()

    for message in st.session_state.messages:
        role = "user" if message["type"] == "user" else "assistant"
        with st.chat_message(role):
            render_message(message)

    active = st.session_state.active_run
    prompt = st.chat_input(
        "Message ARIA",
        disabled=active is not None,
    )

    if prompt and prompt.strip():
        try:
            _start_run(prompt.strip())
            st.rerun()
        except Exception as exc:
            st.error(str(exc))

    if st.session_state.active_run is not None:
        _render_active_run()


if __name__ == "__main__":
    main()
