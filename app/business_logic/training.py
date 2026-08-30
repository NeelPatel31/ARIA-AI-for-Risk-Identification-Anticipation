import re

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


def _build_embeddings() -> AzureOpenAIEmbeddings:
    return AzureOpenAIEmbeddings(
        api_key=settings.AZURE_OPENAI_EMBEDDING_API_KEY,
        api_version=settings.AZURE_OPENAI_EMBEDDING_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_EMBEDDING_API_ENDPOINT,
        azure_deployment=settings.AZURE_OPENAI_EMBEDDING_API_DEPLOYMENT,
        model=settings.AZURE_OPENAI_EMBEDDING_MODEL_NAME,
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

        body = re.sub(r"^---\n.*?\n---\n", "", raw_md, count=1, flags=re.DOTALL)

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


def train_product_chunks() -> dict:
    chunks, file_count = load_and_split_documents()

    if not chunks:
        logger.warning("No chunks produced; skipping vector store ingestion.")
        return {"chunks": 0, "files": file_count, "message": "No chunks to ingest"}

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
