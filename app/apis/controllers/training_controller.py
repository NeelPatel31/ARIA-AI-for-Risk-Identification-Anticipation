from fastapi.responses import JSONResponse

from app.business_logic import train_news_chunks, train_product_chunks
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
