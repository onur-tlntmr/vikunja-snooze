import structlog
from fastapi import FastAPI
from app.config import settings
from app import api

logger = structlog.get_logger()

app = FastAPI(title="Vikunja Ntfy Webhook Service")

@app.on_event("startup")
async def startup_event():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )
    logger.info("Application starting up", settings=settings.model_dump(exclude={"vikunja_api_token"}))


@app.get("/health")
def health_check():
    return {"status": "ok"}
app.include_router(api.router)

