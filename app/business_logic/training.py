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


def _product_chunks_from_markdown(raw_md: str, *, source: str | None = None) -> list[Document]:
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    frontmatter = parse_frontmatter(raw_md)
    body = _strip_frontmatter(raw_md)
    chunks = splitter.split_text(body)
    for chunk in chunks:
        chunk.metadata["product"] = frontmatter.get("product")
        chunk.metadata["entities"] = frontmatter.get("entities")
        if source:
            chunk.metadata["source"] = source
    return chunks


def _news_document_from_markdown(raw_md: str, *, source: str) -> Document:
    frontmatter = parse_frontmatter(raw_md)
    body = _strip_frontmatter(raw_md)
    metadata = {
        key: _serialize_metadata_value(value)
        for key, value in frontmatter.items()
    }
    metadata["source"] = source
    return Document(page_content=body, metadata=metadata)


def _normalize_markdown_filename(filename: str) -> str:
    if not filename or "/" in filename or "\\" in filename:
        raise ValueError("filename must be a bare file name without directories")
    if filename in {".", ".."}:
        raise ValueError("filename must be a bare file name without directories")
    if not filename.endswith(".md"):
        raise ValueError("filename must end with .md")
    return filename


def _get_vectorstore(collection_name: str) -> Chroma:
    return Chroma(
        persist_directory=str(constants.CHROMA_PERSIST_DIR),
        collection_name=collection_name,
        embedding_function=_build_embeddings(),
    )


def _add_documents_to_collection(
    documents: list[Document],
    *,
    collection_name: str,
) -> int:
    shredded_documents = list(ShreddingTransformer().transform_documents(documents))
    vectorstore = _get_vectorstore(collection_name)
    vectorstore.add_documents(shredded_documents)
    return len(documents)


def load_and_split_documents() -> tuple[list[Document], int]:
    all_chunks: list[Document] = []
    product_files = sorted(constants.PRODUCT_DATA_DIR.glob("*.md"))

    if not product_files:
        logger.warning(
            "No markdown files found in %s", constants.PRODUCT_DATA_DIR
        )
        return all_chunks, 0
    for file_path in product_files:
        raw_md = file_path.read_text(encoding="utf-8")
        chunks = _product_chunks_from_markdown(raw_md, source=file_path.name)
        all_chunks.extend(chunks)
        logger.info(
            "Split %s into %s chunks (product=%s)",
            file_path.name,
            len(chunks),
            chunks[0].metadata.get("product") if chunks else None,
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
        document = _news_document_from_markdown(raw_md, source=file_path.name)
        documents.append(document)
        logger.info(
            "Loaded news document %s (event_id=%s, published_date=%s)",
            file_path.name,
            document.metadata.get("event_id"),
            document.metadata.get("published_date"),
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


def insert_product_document(*, markdown: str, filename: str) -> dict:
    name = _normalize_markdown_filename(filename)
    destination = constants.PRODUCT_DATA_DIR / name
    if destination.exists():
        raise FileExistsError(f"Product file already exists: {name}")

    chunks = _product_chunks_from_markdown(markdown, source=name)
    if not chunks:
        raise ValueError("No product chunks produced from markdown")

    constants.PRODUCT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown, encoding="utf-8")

    inserted = _add_documents_to_collection(
        chunks,
        collection_name=constants.CHROMA_COLLECTION_NAME,
    )

    from .rag import get_retriever

    get_retriever(force_reload=True)

    logger.info(
        "Inserted product '%s' as %s chunks into collection '%s'",
        name,
        inserted,
        constants.CHROMA_COLLECTION_NAME,
    )
    return {
        "filename": name,
        "chunks": inserted,
        "product": chunks[0].metadata.get("product"),
        "message": "Product inserted into collection successfully",
    }


def insert_news_document(*, markdown: str, filename: str) -> dict:
    name = _normalize_markdown_filename(filename)
    destination = constants.NEWS_DATA_DIR / name
    if destination.exists():
        raise FileExistsError(f"News file already exists: {name}")

    document = _news_document_from_markdown(markdown, source=name)
    if not document.page_content.strip():
        raise ValueError("News markdown body is empty")

    constants.NEWS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    destination.write_text(markdown, encoding="utf-8")

    inserted = _add_documents_to_collection(
        [document],
        collection_name=constants.CHROMA_NEWS_COLLECTION_NAME,
    )

    from .rag import get_news_retriever

    get_news_retriever(force_reload=True)

    logger.info(
        "Inserted news '%s' into collection '%s' (event_id=%s)",
        name,
        constants.CHROMA_NEWS_COLLECTION_NAME,
        document.metadata.get("event_id"),
    )
    return {
        "filename": name,
        "chunks": inserted,
        "event_id": document.metadata.get("event_id"),
        "published_date": document.metadata.get("published_date"),
        "message": "News inserted into collection successfully",
    }
