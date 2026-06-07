from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Agentic Multimodal Assistant"
    ENVIRONMENT: str = "development"

    DEBUG: bool = True

    API_V1_PREFIX: str = "/api/v1"

    GEMINI_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None

    LLM_PROVIDER: str = "hybrid"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    WHISPER_MODEL: str = "small"

    OCR_PROVIDER: str = "easyocr"
    OCR_TEXT_MIN_CHARS: int = 60
    OCR_RENDER_ZOOM: float = 2.5

    MAX_UPLOAD_SIZE_MB: int = 50

    class Config:
        env_file = ".env"


settings = Settings()