from typing import Any

import streamlit as st


def render_user_message(text: str) -> None:
    if text.strip():
        st.markdown(text)


def render_ai_tool_call(text: str | None, tool_calls: list[dict[str, Any]]) -> None:
    if text:
        st.markdown(text)
    for tool_call in tool_calls:
        name = tool_call.get("name", "unknown")
        tool_call_id = tool_call.get("id", "unknown")
        with st.expander(f"tool call | {name} | {tool_call_id}", expanded=False):
            st.json(tool_call)


def render_tool_result(payload: dict[str, Any]) -> None:
    name = payload.get("name") or "unknown"
    tool_call_id = payload.get("id") or payload.get("tool_call_id") or "unknown"
    status = payload.get("status", "success")
    status_label = "failed" if status == "error" else "success"
    with st.expander(
        f"ToolMessage | {name} | {tool_call_id} | {status_label}",
        expanded=False,
    ):
        st.json(payload)


def render_ai_text(content: str) -> None:
    if content.strip():
        st.markdown(content)


def render_message(message: dict[str, Any]) -> None:
    msg_type = message["type"]
    if msg_type == "user":
        render_user_message(message.get("text", ""))
    elif msg_type == "ai_tool_call":
        render_ai_tool_call(message.get("text"), message.get("tool_calls", []))
    elif msg_type == "tool_result":
        render_tool_result(message)
    elif msg_type == "ai_text":
        render_ai_text(message.get("content", ""))


def format_tool_result_event(data: dict[str, Any]) -> dict[str, Any]:
    return {"type": "tool_result", **data}
