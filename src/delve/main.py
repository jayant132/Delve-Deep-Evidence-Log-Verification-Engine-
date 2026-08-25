import logging

from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

from delve.config import settings
from delve.logging_config import configure_logging
from delve.routers.incidents import router as incidents_router

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="DELVE", version="0.1.0")
app.include_router(incidents_router)


@app.on_event("startup")
async def startup() -> None:
    logger.info("DELVE starting up | environment=%s", settings.environment)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "environment": settings.environment}