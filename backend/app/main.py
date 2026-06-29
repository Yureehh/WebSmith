import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings
from app.db.session import SessionLocal
from app.services.jobs import recover_stuck_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("websmith")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Any job left 'running' means a previous process died mid-run; fail it so the UI is honest.
    with SessionLocal() as db:
        recover_stuck_jobs(db)
    yield


app = FastAPI(title="WebSmith API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.exception_handler(Exception)
def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) or exc.__class__.__name__,
            "error_type": exc.__class__.__name__,
        },
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
