import time

from fastapi import APIRouter, Response

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