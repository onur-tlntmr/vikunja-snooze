import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import api
from app.config import settings

logger = structlog.get_logger()

app = FastAPI(title="Vikunja Ntfy Webhook Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://ntfy:80",
        "http://server.home.arpa:8080",
        "http://server.home.arpa",
        "https://server.home.arpa",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )
    logger.info(
        "Application starting up",
        settings=settings.model_dump(exclude={"vikunja_api_token"}),
    )


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(api.router)
