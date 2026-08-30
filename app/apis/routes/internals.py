import time

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app.apis.controllers import (
    generate_answer_controller,
    retrieve_chunks_controller,
    train_product_chunks_controller,
)
from app.apis.validation_models import QueryRequest
from app.utils import logger

internals_router = APIRouter(tags=["internals"])


@internals_router.get("/health")
async def health_check(response: Response):
    start_time = time.time()
    health_status = {
        "status": "healthy",
        "timestamp": start_time,
        "services": {},
    }
    health_status["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

    is_healthy = all(health_status["services"].values())
    health_status["status"] = "healthy" if is_healthy else "unhealthy"
    response.status_code = 200 if is_healthy else 503

    logger.info(f"Health check returned {health_status['status']} status: {health_status}")
    return health_status


@internals_router.post("/train-products")
async def train_products():
    try:
        result = train_product_chunks_controller()
        logger.info(f"Product training completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in /train-products endpoint: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Training failed", "detail": str(e)},
            status_code=500,
        )


@internals_router.post("/retrieve")
async def retrieve(request: QueryRequest):
    try:
        result = await retrieve_chunks_controller(request)
        logger.info(f"/retrieve completed for query: {request.user_query}")
        return result
    except Exception as e:
        logger.error(f"Error in /retrieve endpoint: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Retrieval failed", "detail": str(e)},
            status_code=500,
        )


@internals_router.post("/query")
async def query(request: QueryRequest):
    try:
        result = await generate_answer_controller(request)
        logger.info(f"/query completed for query: {request.user_query}")
        return result
    except Exception as e:
        logger.error(f"Error in /query endpoint: {e}", exc_info=True)
        return JSONResponse(
            content={"error": "Answer generation failed", "detail": str(e)},
            status_code=500,
        )