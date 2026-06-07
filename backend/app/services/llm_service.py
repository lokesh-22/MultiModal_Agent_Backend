"""Backward-compatible LLM accessors.

Prefer importing app.services.groq_service or app.services.gemini_service directly.
"""

from app.services.gemini_service import get_gemini_model


llm = get_gemini_model()