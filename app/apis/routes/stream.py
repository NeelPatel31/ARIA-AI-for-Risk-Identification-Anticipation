from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.apis.controllers.chat_controller import stream_chat_controller
from app.apis.validation_models import StreamChatRequest
from app.business_logic import ActiveRunError
from app.utils import logger

stream_router = APIRouter(tags=["stream"])


@stream_router.post("/stream-chat")
async def stream_chat_endpoint(request: StreamChatRequest) -> StreamingResponse:
    try:
        return await stream_chat_controller(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ActiveRunError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Failed to start chat stream: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
