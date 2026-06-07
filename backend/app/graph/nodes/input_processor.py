from app.graph.state import AgentState
from app.graph.nodes.event_utils import add_reasoning, emit_event


def input_processor(
    state: AgentState
):

    state.setdefault("uploaded_files", [])
    state.setdefault("uploaded_file_metadata", {})
    state.setdefault("extracted_contents", {})
    state.setdefault("source_documents", [])
    state.setdefault("tool_results", {})
    state["reasoning_trace"] = []
    add_reasoning(state, "Input processed", node="input_processor")
    emit_event(
        state,
        "reasoning_update",
        {
            "node": "input_processor",
            "message": "Input processor initialized state",
            "level": "info",
        },
    )

    return state