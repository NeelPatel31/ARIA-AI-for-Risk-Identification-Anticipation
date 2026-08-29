import time
import uuid
from contextlib import asynccontextmanager
import importlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

IMPORT_ORDER = [
    "app.config",
    "app.utils",
    "app.agent_registry",
    "app.apis.routes"
]

for module in IMPORT_ORDER:
    importlib.import_module(module)

from app.utils import logger, trace_id_var
from app.apis.routes import routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service Started.")
    yield
    logger.info("Service Closed.")


app = FastAPI(
    title="ARIA - AI for Risk Identification Anticipation",
    description=(
        "ARIA is an AI agent that helps in identifying and anticipating risks in supply chain. "
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    trace_id = f"G-{uuid.uuid4().hex[-8:]}"
    token = trace_id_var.set(trace_id)
    start_time = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Trace-ID"] = trace_id
        return response
    except Exception:
        status_code = 500
        raise
    finally:
        process_time = time.perf_counter() - start_time
        logger.info(
            f"Endpoint: {request.url.path} | Type: {request.method} | "
            f"Time Taken: {process_time:.4f}s | Status Code: {status_code}"
        )
        trace_id_var.reset(token)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for route in routes:
    app.include_router(route)