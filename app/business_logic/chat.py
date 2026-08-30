import contextlib
from collections.abc import AsyncGenerator

from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage

from app.agent_registry import deep_agent
from app.utils import logger
from app.utils.constants import AI_TOKEN_BATCH_SIZE

_active_sessions: set[str] = set()


class ActiveRunError(RuntimeError):
    """Raised when a session already owns a running agent stream."""


class _TokenBatcher:
    def __init__(self, batch_size: int) -> None:
        self._batch_size = batch_size
        self._buffer: list[str] = []

    def add(self, text: str) -> str | None:
        self._buffer.append(text)
        if len(self._buffer) >= self._batch_size:
            return self.flush()
        return None

    def flush(self) -> str | None:
        if not self._buffer:
            return None
        combined = "".join(self._buffer)
        self._buffer.clear()
        return combined


def _ai_tool_call_event(message: AIMessage) -> dict:
    return {
        "text": message.content or None,
        "tool_calls": [
            {
                "id": tool_call["id"],
                "name": tool_call["name"],
                "args": tool_call["args"],
            }
            for tool_call in message.tool_calls
        ],
    }


def _normalize_custom(payload) -> tuple[str, dict] | None:
    if not isinstance(payload, dict):
        return None

    kind = payload.get("kind")
    if kind == "tool.result":
        return "tool.result", {
            "id": payload.get("tool_call_id") or payload.get("id"),
            "name": payload.get("name"),
            "content": payload.get("content"),
            "status": payload.get("status", "success"),
        }
    return None


def claim_session(session_id: str) -> None:
    """Reserve a session for streaming. Raises ActiveRunError if already active."""
    if session_id in _active_sessions:
        raise ActiveRunError(f"A generation is already running for session '{session_id}'")
    _active_sessions.add(session_id)


def release_session(session_id: str) -> None:
    _active_sessions.discard(session_id)


async def stream_chat_events(
    session_id: str,
    user_query: str,
) -> AsyncGenerator[dict, None]:
    """Stream agent events. Caller must claim_session() before iterating and
    release_session() when the SSE response finishes (including early cancel)."""
    stream = None
    config = {"configurable": {"thread_id": session_id}}

    try:
        yield {"event": "user.message", "data": {"text": user_query}}

        hm = HumanMessage(content=user_query)
        logger.debug(hm.pretty_repr())
        input_state = {"messages": [hm]}

        token_batcher = _TokenBatcher(AI_TOKEN_BATCH_SIZE)

        stream = deep_agent.astream(
            input_state,
            config=config,
            stream_mode=["messages", "updates", "custom"],
        )

        async for chunk in stream:
            chunk_type = chunk[0]
            chunk_data = chunk[1]

            if chunk_type == "messages":
                token, _metadata = chunk_data
                if isinstance(token, AIMessageChunk):
                    if token.tool_call_chunks:
                        continue
                    text = token.text
                    if text:
                        batched = token_batcher.add(text)
                        if batched is not None:
                            yield {"event": "ai.token", "data": {"text": batched}}

            elif chunk_type == "updates":
                batched = token_batcher.flush()
                if batched:
                    yield {"event": "ai.token", "data": {"text": batched}}
                for _source, update in chunk_data.items():
                    if not isinstance(update, dict):
                        continue
                    messages = update.get("messages") or []
                    if not messages:
                        continue
                    message = messages[-1]
                    if isinstance(message, AIMessage) and message.tool_calls:
                        yield {
                            "event": "ai.tool_call",
                            "data": _ai_tool_call_event(message),
                        }

            elif chunk_type == "custom":
                batched = token_batcher.flush()
                if batched:
                    yield {"event": "ai.token", "data": {"text": batched}}
                normalized = _normalize_custom(chunk_data)
                if normalized:
                    event_name, event_data = normalized
                    yield {"event": event_name, "data": event_data}

        batched = token_batcher.flush()
        if batched:
            yield {"event": "ai.token", "data": {"text": batched}}
        yield {"event": "stream.end", "data": {}}

    except Exception as exc:
        logger.error("Stream error: %s", exc, exc_info=True)
        yield {"event": "error", "data": {"message": str(exc)}}
        yield {"event": "stream.end", "data": {}}
    finally:
        if stream is not None:
            with contextlib.suppress(Exception):
                await stream.aclose()
