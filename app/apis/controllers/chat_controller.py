import json
from collections.abc import AsyncGenerator

from fastapi.responses import StreamingResponse

from app.apis.validation_models import StreamChatRequest
from app.business_logic import claim_session, release_session, stream_chat_events
from app.utils import logger


async def _sse_lines(
    session_id: str,
    user_query: str,
) -> AsyncGenerator[str, None]:
    try:
        async for packet in stream_chat_events(session_id, user_query):
            yield f"data: {json.dumps(packet)}\n\n"
    finally:
        release_session(session_id)


async def stream_chat_controller(request: StreamChatRequest) -> StreamingResponse:
    if not request.user_query.strip():
        raise ValueError("user_query must be provided")

    claim_session(request.session_id)
    try:
        logger.info("Starting chat stream for session '%s'", request.session_id)
        return StreamingResponse(
            _sse_lines(request.session_id, request.user_query),
            media_type="text/event-stream",
        )
    except Exception:
        release_session(request.session_id)
        raise
