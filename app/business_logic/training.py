import re
from datetime import date, datetime
from typing import Any

import chromadb
import yaml
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_graph_retriever.transformers import ShreddingTransformer
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

from app.config import settings
from app.utils import logger, constants

HEADERS_TO_SPLIT_ON = [
    ("#", "H1"),
    ("##", "H2"),
]


def parse_frontmatter(md_text: str) -> dict:
    match = re.match(r"^---\n(.*?)\n---\n", md_text, re.DOTALL)
    return yaml.safe_load(match.group(1)) if match else {}


def _strip_frontmatter(md_text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", md_text, count=1, flags=re.DOTALL).strip()


def _serialize_metadata_value(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _build_embeddings() -> AzureOpenAIEmbeddings:
    return AzureOpenAIEmbeddings(
        api_key=settings.AZURE_OPENAI_EMBEDDING_API_KEY,
        api_version=settings.AZURE_OPENAI_EMBEDDING_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_EMBEDDING_API_ENDPOINT,
        azure_deployment=settings.AZURE_OPENAI_EMBEDDING_API_DEPLOYMENT,
        model=settings.AZURE_OPENAI_EMBEDDING_MODEL_NAME,
    )


def _delete_collection(collection_name: str) -> None:
    client = chromadb.PersistentClient(path=str(constants.CHROMA_PERSIST_DIR))
    try:
        client.delete_collection(name=collection_name)
        logger.info("Deleted Chroma collection '%s'", collection_name)
    except Exception:
        logger.info(
            "Chroma collection '%s' did not exist; nothing to delete",
            collection_name,
        )


def load_and_split_documents() -> tuple[list[Document], int]:
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )

    all_chunks: list[Document] = []
    product_files = sorted(constants.PRODUCT_DATA_DIR.glob("*.md"))

    if not product_files:
        logger.warning(
            "No markdown files found in %s", constants.PRODUCT_DATA_DIR
        )
        return all_chunks, 0
    for file_path in product_files:
        raw_md = file_path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(raw_md)

        body = _strip_frontmatter(raw_md)

        chunks = splitter.split_text(body)
        for chunk in chunks:
            chunk.metadata["product"] = frontmatter.get("product")
            chunk.metadata["entities"] = frontmatter.get("entities")

        all_chunks.extend(chunks)
        logger.info(
            "Split %s into %s chunks (product=%s)",
            file_path.name,
            len(chunks),
            frontmatter.get("product"),
        )

    return all_chunks, len(product_files)


def load_news_documents() -> tuple[list[Document], int]:
    documents: list[Document] = []
    news_files = sorted(constants.NEWS_DATA_DIR.glob("*.md"))

    if not news_files:
        logger.warning("No markdown files found in %s", constants.NEWS_DATA_DIR)
        return documents, 0

    for file_path in news_files:
        raw_md = file_path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(raw_md)
        body = _strip_frontmatter(raw_md)

        metadata = {
            key: _serialize_metadata_value(value)
            for key, value in frontmatter.items()
        }
        metadata["source"] = file_path.name

        documents.append(Document(page_content=body, metadata=metadata))
        logger.info(
            "Loaded news document %s (event_id=%s, published_date=%s)",
            file_path.name,
            metadata.get("event_id"),
            metadata.get("published_date"),
        )

    return documents, len(news_files)


def train_product_chunks() -> dict:
    chunks, file_count = load_and_split_documents()

    if not chunks:
        logger.warning("No chunks produced; skipping vector store ingestion.")
        return {"chunks": 0, "files": file_count, "message": "No chunks to ingest"}

    _delete_collection(constants.CHROMA_COLLECTION_NAME)

    embeddings = _build_embeddings()
    shredded_documents = list(
        ShreddingTransformer().transform_documents(chunks)
    )
    Chroma.from_documents(
        documents=shredded_documents,
        embedding=embeddings,
        collection_name=constants.CHROMA_COLLECTION_NAME,
        persist_directory=str(constants.CHROMA_PERSIST_DIR),
    )

    logger.info(
        "Ingested %s chunks from %s files into Chroma at %s",
        len(chunks),
        file_count,
        constants.CHROMA_PERSIST_DIR,
    )
    return {
        "chunks": len(chunks),
        "files": file_count,
        "message": "Product chunks ingested successfully",
    }


def train_news_chunks() -> dict:
    documents, file_count = load_news_documents()

    if not documents:
        logger.warning("No news documents produced; skipping vector store ingestion.")
        return {
            "chunks": 0,
            "files": file_count,
            "message": "No news documents to ingest",
        }

    _delete_collection(constants.CHROMA_NEWS_COLLECTION_NAME)

    embeddings = _build_embeddings()
    shredded_documents = list(
        ShreddingTransformer().transform_documents(documents)
    )
    Chroma.from_documents(
        documents=shredded_documents,
        embedding=embeddings,
        collection_name=constants.CHROMA_NEWS_COLLECTION_NAME,
        persist_directory=str(constants.CHROMA_PERSIST_DIR),
    )

    # # Avoid circular import at module load; refresh after collection rebuild.
    # from .rag import get_news_retriever

    # get_news_retriever(force_reload=True)

    logger.info(
        "Ingested %s news documents from %s files into Chroma collection '%s'",
        len(documents),
        file_count,
        constants.CHROMA_NEWS_COLLECTION_NAME,
    )
    return {
        "chunks": len(documents),
        "files": file_count,
        "message": "News documents ingested successfully",
    }
