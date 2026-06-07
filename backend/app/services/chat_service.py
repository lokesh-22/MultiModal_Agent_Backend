from __future__ import annotations

from collections.abc import Generator
from queue import Empty, Queue
from threading import Thread
from typing import Any
from uuid import uuid4

from app.graph.workflow import build_graph
from app.services.event_bus import EventBus, to_sse


_GRAPH = None


def get_graph():
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = build_graph()
    return _GRAPH


def build_chat_state(
    query: str,
    uploaded_files: list[str],
    uploaded_file_metadata: dict[str, Any] | None = None,
    session_id: str | None = None,
    request_id: str | None = None,
    event_bus: EventBus | None = None,
):
    return {
        "user_query": query,
        "session_id": session_id or str(uuid4()),
        "request_id": request_id or str(uuid4()),
        "uploaded_files": uploaded_files,
        "uploaded_file_metadata": uploaded_file_metadata or {},
        "reasoning_trace": [],
        "event_bus": event_bus,
    }


def run_chat_workflow(query: str, uploaded_files: list[str], uploaded_file_metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    result = get_graph().invoke(build_chat_state(query, uploaded_files, uploaded_file_metadata))
    return {
        "response": result.get("final_response", ""),
        "reasoning_trace": result.get("reasoning_trace", []),
        "tools_used": list(result.get("tool_results", {}).keys()),
        "intent": result.get("intent"),
        "execution_plan": result.get("execution_plan", []),
        "extracted_contents": result.get("extracted_contents", {}),
        "needs_followup": bool(result.get("needs_followup", False)),
        "followup_question": result.get("followup_question"),
        "graph_state": result,
    }


def stream_chat_events(
    query: str,
    uploaded_files: list[str],
    uploaded_file_metadata: dict[str, Any] | None = None,
    session_id: str | None = None,
    request_id: str | None = None,
) -> Generator[str, None, None]:
    stream_queue: Queue = Queue()
    session_id = session_id or str(uuid4())
    request_id = request_id or str(uuid4())
    event_bus = EventBus(stream_queue, session_id=session_id, request_id=request_id)
    state = build_chat_state(
        query,
        uploaded_files,
        uploaded_file_metadata,
        session_id=session_id,
        request_id=request_id,
        event_bus=event_bus,
    )

    def run_graph():
        graph = get_graph()
        try:
            event_bus.emit(
                "agent_started",
                {
                    "query": query,
                    "file_count": len(uploaded_files),
                    "model_routing": {
                        "control_plane": "groq",
                        "reasoning_plane": "gemini",
                    },
                },
            )
            result = graph.invoke(state)
            event_bus.emit(
                "agent_completed",
                {
                    "status": "success",
                    "total_duration_ms": 0,
                    "tools_used": list(result.get("tool_results", {}).keys()),
                    "files_processed": len(uploaded_files),
                },
            )
        except Exception as exc:
            event_bus.emit(
                "error",
                {
                    "code": "GRAPH_EXECUTION_ERROR",
                    "message": str(exc),
                    "stage": "generation",
                    "retriable": True,
                    "details": {},
                },
            )
            event_bus.emit(
                "agent_completed",
                {
                    "status": "failed",
                    "total_duration_ms": 0,
                    "tools_used": [],
                    "files_processed": len(uploaded_files),
                },
            )
        finally:
            stream_queue.put(None)

    worker = Thread(target=run_graph, daemon=True)
    worker.start()

    while True:
        try:
            envelope = stream_queue.get(timeout=0.25)
        except Empty:
            continue

        if envelope is None:
            break

        yield to_sse(envelope)
