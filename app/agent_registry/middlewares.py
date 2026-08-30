from collections.abc import Awaitable, Callable

from langchain.agents.middleware import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
    SummarizationMiddleware,
    ToolCallRequest,
)
from langchain_core.messages import ToolMessage
from langgraph.config import get_stream_writer
from langgraph.types import Command

from ..utils import logger
from .llms import llm

summarization_middleware = SummarizationMiddleware(
    model=llm,
    trigger=[("fraction", 0.6), ("messages", 100)],
    keep=("messages", 20),
)


class DebugMiddleware(AgentMiddleware):
    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        return await handler(request)

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Awaitable[ToolMessage | Command]],
    ) -> ToolMessage | Command:
        try:
            result = await handler(request)
            writer = get_stream_writer()
            message = result
            if isinstance(result, Command):
                messages = (result.update or {}).get("messages") or []
                message = messages[-1]

            logger.info("\n" + message.pretty_repr())
            kwargs = message.to_json()["kwargs"]
            writer({"kind": "tool.result", "name": request.tool_call["name"], **kwargs})
            return result
        except Exception as exc:
            logger.error("Tool failed: %s", exc)
            raise