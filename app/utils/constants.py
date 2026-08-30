from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_DATA_DIR = PROJECT_ROOT / "data" / "products"
NEWS_DATA_DIR = PROJECT_ROOT / "data" / "news"

CHROMA_PERSIST_DIR = PROJECT_ROOT / "data" / "chroma_db"

CHROMA_COLLECTION_NAME = "product_chunks"
CHROMA_NEWS_COLLECTION_NAME = "news_chunks"

AI_TOKEN_BATCH_SIZE = 5
