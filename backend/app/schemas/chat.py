from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(default="user")
    content: str = Field(default="")


class ChatRequest(BaseModel):
    query: str = Field(default="")
    uploaded_files: list[str] = Field(default_factory=list)


class FileMetadata(BaseModel):
    file_name: str
    file_path: str
    file_type: str
    size_bytes: int
    content_type: str | None = None


class ReasoningEvent(BaseModel):
    event: str
    message: str
    data: Any | None = None


class ChatResponse(BaseModel):
    response: str
    reasoning_trace: list[str] = Field(default_factory=list)
    tools_used: list[str] = Field(default_factory=list)
    intent: str | None = None
    execution_plan: list[str] = Field(default_factory=list)
    extracted_contents: dict[str, Any] = Field(default_factory=dict)
    needs_followup: bool = False
    followup_question: str | None = None


class StreamEvent(BaseModel):
    event: str
    data: Any
