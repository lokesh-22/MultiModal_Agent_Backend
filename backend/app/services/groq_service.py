from functools import lru_cache
from typing import Any

from langchain_groq import ChatGroq

from app.core.config import settings


@lru_cache(maxsize=4)
def get_groq_model(model_name: str | None = None) -> ChatGroq:
    kwargs = {
        "model": model_name or settings.GROQ_MODEL,
        "temperature": 0,
    }

    if settings.GROQ_API_KEY:
        kwargs["groq_api_key"] = settings.GROQ_API_KEY

    return ChatGroq(**kwargs)


def invoke_groq_text(prompt: str, model_name: str | None = None) -> str:
    response = get_groq_model(model_name).invoke(prompt)
    return getattr(response, "content", str(response)).strip()


def invoke_groq(prompt: str, model_name: str | None = None) -> Any:
    return get_groq_model(model_name).invoke(prompt)