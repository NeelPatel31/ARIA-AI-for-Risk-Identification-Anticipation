from langchain.agents import create_agent

from .checkpointers import checkpointer
from .llms import llm
from .middlewares import DebugMiddleware, summarization_middleware
from .prompts import (
    MAIN_AGENT_INSTRUCTION,
    SEPERATOR,
    TODO_INSTRUCTION,
)
from .state import DeepAgentState
from .tools import (
    read_todos,
    write_todos,
)


built_in_tools = [
    write_todos,
    read_todos
]

# task_tool = _create_task_tool(
#     sub_agent_tools, [visual_designer_sub_agent], llm, DeepAgentState
# )


INSTRUCTION = (
    MAIN_AGENT_INSTRUCTION
    + SEPERATOR
    + TODO_INSTRUCTION
)

deep_agent = create_agent(
    model=llm,
    tools=built_in_tools,
    system_prompt=INSTRUCTION,
    state_schema=DeepAgentState,
    checkpointer=checkpointer,
    middleware=[
        summarization_middleware,
        DebugMiddleware(),
    ],
)

