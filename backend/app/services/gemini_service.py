from functools import lru_cache
from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


@lru_cache(maxsize=4)
def get_gemini_model(model_name: str | None = None) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=model_name or settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0,
    )


def invoke_gemini_text(prompt: str, model_name: str | None = None) -> str:
    response = get_gemini_model(model_name).invoke(prompt)
    return getattr(response, "content", str(response)).strip()


def invoke_gemini(prompt: str, model_name: str | None = None) -> Any:
    return get_gemini_model(model_name).invoke(prompt)


def stream_gemini_text(prompt: str, model_name: str | None = None):
    for chunk in get_gemini_model(model_name).stream(prompt):
        text = _chunk_to_text(chunk)
        if text:
            yield text


def _chunk_to_text(chunk: Any) -> str:
    content = getattr(chunk, "content", "")

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
            else:
                text = getattr(item, "text", "")
                if text:
                    parts.append(str(text))
        return "".join(parts)

    return str(content) if content else ""