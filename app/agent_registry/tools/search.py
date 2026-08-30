from langchain.tools import tool
from pydantic import BaseModel, Field

from ...utils import logger
from .tool_descriptions import KNOWLEDGE_SEARCH_DESCRIPTION, NEWS_SEARCH_DESCRIPTION


def _format_chunks(chunks: list[dict], *, news: bool = False) -> str:
    if not chunks:
        return "No matching results found."

    parts: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata") or {}
        text = chunk.get("text") or ""
        header_lines = [f"### Result {i}"]
        if news:
            for key in (
                "event_id",
                "published_date",
                "event_type",
                "entities",
                "source",
            ):
                if key in metadata and metadata[key] is not None:
                    header_lines.append(f"- {key}: {metadata[key]}")
        else:
            for key in ("product", "source", "H1", "H2", "entities"):
                if key in metadata and metadata[key] is not None:
                    header_lines.append(f"- {key}: {metadata[key]}")
        parts.append("\n".join(header_lines) + "\n\n" + text)
    return "\n\n---\n\n".join(parts)


class KnowledgeSearchInput(BaseModel):
    query: str = Field(description="Search query for product / supply-chain knowledge")


class NewsSearchInput(BaseModel):
    query: str = Field(description="Search query for disruption / news events")


@tool(
    description=KNOWLEDGE_SEARCH_DESCRIPTION,
    parse_docstring=True,
    args_schema=KnowledgeSearchInput,
)
async def knowledge_search(query: str) -> str:
    """Search product and supply-chain knowledge for relevant chunks.

    Args:
        query: Natural-language search query

    Returns:
        Formatted retrieval results with metadata
    """
    try:
        # Lazy import avoids circular import with agent_registry <-> business_logic.chat
        from ...business_logic.rag import retrieve_chunks

        chunks = await retrieve_chunks(query)
        return _format_chunks(chunks, news=False)
    except Exception as exc:
        logger.error("Error in knowledge_search: %s", exc)
        return f"Error searching knowledge base: {exc}"


@tool(
    description=NEWS_SEARCH_DESCRIPTION,
    parse_docstring=True,
    args_schema=NewsSearchInput,
)
async def news_search(query: str) -> str:
    """Search news and disruption events for relevant articles.

    Args:
        query: Natural-language search query

    Returns:
        Formatted news retrieval results with metadata
    """
    try:
        # Lazy import avoids circular import with agent_registry <-> business_logic.chat
        from ...business_logic.rag import retrieve_news_chunks

        chunks = await retrieve_news_chunks(query)
        return _format_chunks(chunks, news=True)
    except Exception as exc:
        logger.error("Error in news_search: %s", exc)
        return f"Error searching news: {exc}"
