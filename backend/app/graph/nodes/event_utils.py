from __future__ import annotations

from app.graph.state import AgentState


def emit_event(state: AgentState, event_type: str, payload: dict):
    event_bus = state.get("event_bus")
    if event_bus:
        event_bus.emit(event_type, payload)


def add_reasoning(state: AgentState, message: str, node: str | None = None, level: str = "info"):
    state.setdefault("reasoning_trace", []).append(message)
    emit_event(
        state,
        "reasoning_update",
        {
            "node": node or "unknown",
            "message": message,
            "level": level,
        },
    )
