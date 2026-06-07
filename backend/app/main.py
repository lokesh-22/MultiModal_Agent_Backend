from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

from app.api.routes.chat import router as chat_router
from app.api.routes.debug import router as debug_router
from app.api.routes.health import router as health_router
from app.api.routes.upload import router as upload_router
from app.services.ocr_service import warm_ocr_engine
from app.tools.audio_tool import get_whisper_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    warm_ocr_engine()
    get_whisper_model()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    upload_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    chat_router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    health_router,
    prefix="",
)

app.include_router(
    debug_router,
    prefix="",
)

@app.get("/")
async def root():
    return {"status": "running", "env": settings.ENVIRONMENT}
