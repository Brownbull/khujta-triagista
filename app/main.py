from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine
from app.models import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate required config
    if settings.app_env != "development" and not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is required in non-development environments")
    # Startup: create tables (dev convenience — production uses alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="SRE Triage Agent",
    description="AI-powered SRE Incident Intake & Triage Agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sre-triage-agent"}


@app.get("/")
async def root():
    return {"message": "SRE Triage Agent", "docs": "/docs"}
