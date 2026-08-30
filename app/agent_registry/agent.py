from langchain.agents import create_agent

from .checkpointers import checkpointer
from .llms import llm
from .middlewares import DebugMiddleware, summarization_middleware
from .prompts import (
    MAIN_AGENT_INSTRUCTION,
    REPORT_HANDOFF_INSTRUCTION,
    RISK_RUBRIC_INSTRUCTION,
    SEPERATOR,
    TODO_INSTRUCTION,
)
from .state import DeepAgentState
from .subagents import all_subagents
from .tools import (
    _create_task_tool,
    assess_risks,
    knowledge_search,
    news_search,
    present_report,
    read_report,
    read_todos,
    save_report,
    write_todos,
)


sub_agent_tools = [
    write_todos,
    read_todos,
    knowledge_search,
    news_search,
    save_report,
    read_report,
    present_report,
]

task_tool = _create_task_tool(
    sub_agent_tools,
    all_subagents,
    llm,
    DeepAgentState,
)

built_in_tools = [
    write_todos,
    read_todos,
    task_tool,
    save_report,
    read_report,
    present_report,
    assess_risks,
]

INSTRUCTION = (
    MAIN_AGENT_INSTRUCTION
    + SEPERATOR
    + TODO_INSTRUCTION
    + SEPERATOR
    + RISK_RUBRIC_INSTRUCTION
    + SEPERATOR
    + REPORT_HANDOFF_INSTRUCTION
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