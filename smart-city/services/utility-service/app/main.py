import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_database

SERVICE_NAME = os.getenv("SERVICE_NAME", "utility-service")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    logger.info("%s started", SERVICE_NAME)
    yield


app = FastAPI(title="Utility Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}
