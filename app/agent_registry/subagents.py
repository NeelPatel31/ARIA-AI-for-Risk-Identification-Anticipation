from .prompts import (
    DISRUPTION_SCOUT_INSTRUCTION,
    MITIGATION_STRATEGIST_INSTRUCTION,
    PRODUCT_CARTOGRAPHER_INSTRUCTION,
)

product_cartographer_sub_agent = {
    "name": "product_cartographer",
    "description": (
        "Compile a structured product supply-chain dossier covering Demand, "
        "Sourcing, Manufacturing, and Delivery, plus the entity list needed "
        "for disruption linking. Use for product or supply-chain context questions."
    ),
    "system_prompt": PRODUCT_CARTOGRAPHER_INSTRUCTION,
    "tools": [
        "write_todos",
        "read_todos",
        "knowledge_search",
    ],
}

disruption_scout_sub_agent = {
    "name": "disruption_scout",
    "description": (
        "Find and compile news and disruption events tied to a product's "
        "entities and supply-chain stages. Prefer grounding searches in a "
        "saved product_dossier when one exists."
    ),
    "system_prompt": DISRUPTION_SCOUT_INSTRUCTION,
    "tools": [
        "write_todos",
        "read_todos",
        "news_search",
        "read_report",
    ],
}

mitigation_strategist_sub_agent = {
    "name": "mitigation_strategist",
    "description": (
        "Trace scored supply-chain risks to root causes and propose cited, "
        "actionable mitigations using saved reports and targeted product/news search."
    ),
    "system_prompt": MITIGATION_STRATEGIST_INSTRUCTION,
    "tools": [
        "write_todos",
        "read_todos",
        "read_report",
        "knowledge_search",
        "news_search",
    ],
}

all_subagents = [
    product_cartographer_sub_agent,
    disruption_scout_sub_agent,
    mitigation_strategist_sub_agent,
]
