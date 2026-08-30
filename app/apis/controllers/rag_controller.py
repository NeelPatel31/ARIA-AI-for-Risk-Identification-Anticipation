from fastapi.responses import JSONResponse

from app.apis.validation_models import QueryRequest
from app.business_logic import (
    generate_answer,
    generate_news_answer,
    retrieve_chunks,
    retrieve_news_chunks,
)
from app.utils import logger


async def retrieve_chunks_controller(request: QueryRequest) -> JSONResponse:
    try:
        chunks = await retrieve_chunks(request.user_query)
        return JSONResponse(
            content={"query": request.user_query, "chunks": chunks},
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error retrieving chunks: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Retrieval failed", "detail": str(e)},
            status_code=500,
        )


async def generate_answer_controller(request: QueryRequest) -> JSONResponse:
    try:
        answer = await generate_answer(request.user_query)
        return JSONResponse(
            content={"query": request.user_query, "answer": answer},
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error generating answer: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Answer generation failed", "detail": str(e)},
            status_code=500,
        )


async def retrieve_news_chunks_controller(request: QueryRequest) -> JSONResponse:
    try:
        chunks = await retrieve_news_chunks(request.user_query)
        return JSONResponse(
            content={"query": request.user_query, "chunks": chunks},
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error retrieving news chunks: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "News retrieval failed", "detail": str(e)},
            status_code=500,
        )


async def generate_news_answer_controller(request: QueryRequest) -> JSONResponse:
    try:
        answer = await generate_news_answer(request.user_query)
        return JSONResponse(
            content={"query": request.user_query, "answer": answer},
            status_code=200,
        )
    except Exception as e:
        logger.error(f"Error generating news answer: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "News answer generation failed", "detail": str(e)},
            status_code=500,
        )
