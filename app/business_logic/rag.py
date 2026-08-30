# Monkey-patch chromadb.api.types to add IncludeEnum which was removed in chromadb 1.x
import chromadb.api.types
from enum import Enum

class IncludeEnum(str, Enum):
    documents = "documents"
    embeddings = "embeddings"
    metadatas = "metadatas"
    distances = "distances"
    uris = "uris"
    data = "data"

chromadb.api.types.IncludeEnum = IncludeEnum

import threading

from graph_retriever.strategies import Eager
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_graph_retriever import GraphRetriever

from app.agent_registry import SIMPLE_RAG_PROMPT, llm
from app.utils import constants, logger
from .training import _build_embeddings

_retriever: GraphRetriever | None = None
_retriever_lock = threading.Lock()

_news_retriever: GraphRetriever | None = None
_news_retriever_lock = threading.Lock()


def _build_retriever(collection_name: str) -> GraphRetriever:
    embeddings = _build_embeddings()
    vectorstore = Chroma(
        persist_directory=str(constants.CHROMA_PERSIST_DIR),
        collection_name=collection_name,
        embedding_function=embeddings,
    )
    return GraphRetriever(
        store=vectorstore,
        strategy=Eager(select_k=9, start_k=4, max_depth=4),
    )


def get_retriever(*, force_reload: bool = False) -> GraphRetriever:
    global _retriever
    if force_reload:
        with _retriever_lock:
            _retriever = _build_retriever(constants.CHROMA_COLLECTION_NAME)
            logger.info("Reloaded product GraphRetriever instance")
            return _retriever

    if _retriever is None:
        with _retriever_lock:
            if _retriever is None:
                _retriever = _build_retriever(constants.CHROMA_COLLECTION_NAME)
                logger.info("Initialized shared GraphRetriever instance")
    return _retriever


def get_news_retriever(*, force_reload: bool = False) -> GraphRetriever:
    global _news_retriever
    if force_reload:
        with _news_retriever_lock:
            _news_retriever = _build_retriever(constants.CHROMA_NEWS_COLLECTION_NAME)
            logger.info("Reloaded news GraphRetriever instance")
            return _news_retriever

    if _news_retriever is None:
        with _news_retriever_lock:
            if _news_retriever is None:
                _news_retriever = _build_retriever(constants.CHROMA_NEWS_COLLECTION_NAME)
                logger.info("Initialized shared news GraphRetriever instance")
    return _news_retriever


def _sort_news_by_published_date_desc(chunks: list[dict]) -> list[dict]:
    return sorted(
        chunks,
        key=lambda chunk: chunk.get("metadata", {}).get("published_date") or "",
        reverse=True,
    )


async def retrieve_chunks(user_query: str) -> list[dict]:
    retriever = get_retriever()
    docs = await retriever.ainvoke(user_query)
    logger.info("Retrieved %s chunks for query: %s", len(docs), user_query)
    return [
        {
            "text": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in docs
    ]


async def retrieve_news_chunks(user_query: str) -> list[dict]:
    retriever = get_news_retriever()
    docs = await retriever.ainvoke(user_query)
    chunks = [
        {
            "text": doc.page_content,
            "metadata": doc.metadata,
        }
        for doc in docs
    ]
    chunks = _sort_news_by_published_date_desc(chunks)
    logger.info("Retrieved %s news chunks for query: %s", len(chunks), user_query)
    return chunks


def _format_docs(docs: list[dict]) -> str:
    return "\n\n".join(doc["text"] for doc in docs)


async def generate_answer(user_query: str) -> str:
    chunks = await retrieve_chunks(user_query)
    context = _format_docs(chunks)

    prompt = ChatPromptTemplate.from_template(SIMPLE_RAG_PROMPT)
    rag_chain = (
        {
            "context": RunnablePassthrough(),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = await rag_chain.ainvoke({"context": context, "question": user_query})
    logger.info("Generated answer for query: %s", user_query)
    return answer


async def generate_news_answer(user_query: str) -> str:
    chunks = await retrieve_news_chunks(user_query)
    context = _format_docs(chunks)

    prompt = ChatPromptTemplate.from_template(SIMPLE_RAG_PROMPT)
    rag_chain = (
        {
            "context": RunnablePassthrough(),
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    answer = await rag_chain.ainvoke({"context": context, "question": user_query})
    logger.info("Generated news answer for query: %s", user_query)
    return answer
