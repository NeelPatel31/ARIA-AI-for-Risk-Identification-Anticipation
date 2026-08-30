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
from langchain_openai import AzureOpenAIEmbeddings

from app.agent_registry import SIMPLE_RAG_PROMPT, llm
from app.config import settings
from app.utils import constants, logger
from .training import _build_embeddings

_retriever: GraphRetriever | None = None
_retriever_lock = threading.Lock()


def _build_retriever() -> GraphRetriever:
    embeddings = _build_embeddings()
    vectorstore = Chroma(
        persist_directory=str(constants.CHROMA_PERSIST_DIR),
        collection_name=constants.CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
    )
    return GraphRetriever(
        store=vectorstore,
        strategy=Eager(select_k=9, start_k=4, max_depth=4),
    )


def get_retriever() -> GraphRetriever:
    global _retriever
    if _retriever is None:
        with _retriever_lock:
            if _retriever is None:
                _retriever = _build_retriever()
                logger.info("Initialized shared GraphRetriever instance")
    return _retriever


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

