from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatResponse
from app.services.chat_service import run_chat_workflow, stream_chat_events
from app.services.file_service import build_file_metadata, save_file

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    query: str = Form(default=""),
    files: list[UploadFile] = File(default=[]),
):
    saved_paths = []
    uploaded_file_metadata = {}

    for file in files:
        path = await save_file(file)
        saved_paths.append(path)
        uploaded_file_metadata[path] = build_file_metadata(path, file.content_type)

    result = run_chat_workflow(query, saved_paths, uploaded_file_metadata)

    return ChatResponse(
        response=result["response"],
        reasoning_trace=result["reasoning_trace"],
        tools_used=result["tools_used"],
        intent=result["intent"],
        execution_plan=result["execution_plan"],
        extracted_contents=result["extracted_contents"],
        needs_followup=result["needs_followup"],
        followup_question=result["followup_question"],
    )


@router.post("/chat/stream")
async def chat_stream(
    query: str = Form(default=""),
    files: list[UploadFile] = File(default=[]),
):
    saved_paths = []
    uploaded_file_metadata = {}

    for file in files:
        path = await save_file(file)
        saved_paths.append(path)
        uploaded_file_metadata[path] = build_file_metadata(path, file.content_type)

    return StreamingResponse(
        stream_chat_events(query, saved_paths, uploaded_file_metadata),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
