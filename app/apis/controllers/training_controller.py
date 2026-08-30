from fastapi.responses import JSONResponse

from app.business_logic import (
    insert_news_document,
    insert_product_document,
    train_news_chunks,
    train_product_chunks,
)
from app.utils import logger


def train_product_chunks_controller() -> JSONResponse:
    try:
        result = train_product_chunks()
        return JSONResponse(
            content=result,
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error training product chunks: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Failed to train product chunks", "detail": str(e)},
            status_code=500,
        )


def train_news_chunks_controller() -> JSONResponse:
    try:
        result = train_news_chunks()
        return JSONResponse(
            content=result,
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error training news chunks: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Failed to train news chunks", "detail": str(e)},
            status_code=500,
        )


def insert_product_controller(filename: str, markdown: str) -> JSONResponse:
    try:
        result = insert_product_document(markdown=markdown, filename=filename)
        return JSONResponse(content=result, status_code=200)
    except FileExistsError as e:
        logger.warning(f"Product insert conflict: {e}")
        return JSONResponse(
            content={"error": "Product already exists", "detail": str(e)},
            status_code=409,
        )
    except ValueError as e:
        logger.warning(f"Invalid product insert request: {e}")
        return JSONResponse(
            content={"error": "Invalid product document", "detail": str(e)},
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error inserting product: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Failed to insert product", "detail": str(e)},
            status_code=500,
        )


def insert_news_controller(filename: str, markdown: str) -> JSONResponse:
    try:
        result = insert_news_document(markdown=markdown, filename=filename)
        return JSONResponse(content=result, status_code=200)
    except FileExistsError as e:
        logger.warning(f"News insert conflict: {e}")
        return JSONResponse(
            content={"error": "News already exists", "detail": str(e)},
            status_code=409,
        )
    except ValueError as e:
        logger.warning(f"Invalid news insert request: {e}")
        return JSONResponse(
            content={"error": "Invalid news document", "detail": str(e)},
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Error inserting news: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Failed to insert news", "detail": str(e)},
            status_code=500,
        )
