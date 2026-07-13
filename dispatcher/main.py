from contextlib import asynccontextmanager
import asyncio
import structlog
from fastapi import FastAPI
from shared.config import settings
from dispatcher.api.jobs import router as jobs_router
from dispatcher.api.nodes import router as nodes_router
from dispatcher.background import check_node_heartbeats

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting HERD dispatcher", log_level=settings.log_level)
    # We will initialize Redis and Database connections here in subsequent steps
    monitor_task = asyncio.create_task(check_node_heartbeats())
    yield
    logger.info("Shutting down HERD dispatcher")
    monitor_task.cancel()
    # We will close connections here

app = FastAPI(
    title="HERD Dispatcher",
    description="AI-powered task orchestration system",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(jobs_router)
app.include_router(nodes_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
