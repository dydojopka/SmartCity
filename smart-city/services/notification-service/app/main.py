import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_database

SERVICE_NAME = os.getenv("SERVICE_NAME", "notification-service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    logger.info("%s started", SERVICE_NAME)
    yield


app = FastAPI(title="Notification Service", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}
