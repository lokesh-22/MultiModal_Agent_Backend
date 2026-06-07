from app.graph.state import AgentState
from app.graph.nodes.event_utils import add_reasoning, emit_event

from app.services.tool_registry import get_tool


def tool_executor(
    state: AgentState
):

    results = {}

    execution_plan = state.get(
        "execution_plan",
        []
    )

    for step in execution_plan:
        tool = get_tool(step)

        emit_event(
            state,
            "tool_started",
            {
                "step_index": len(results),
                "tool_name": step,
                "input_summary": f"Executing {step}",
            },
        )

        if tool is None:
            results[step] = {
                "tool": step,
                "error": f"Unknown tool: {step}",
            }
            emit_event(
                state,
                "tool_completed",
                {
                    "step_index": len(results) - 1,
                    "tool_name": step,
                    "status": "failed",
                    "duration_ms": 0,
                    "output_summary": "Unknown tool",
                },
            )
            continue

        try:
            result = tool(state)
        except Exception as exc:
            result = {
                "tool": step,
                "error": str(exc),
            }

        results[step] = result
        emit_event(
            state,
            "tool_completed",
            {
                "step_index": len(results) - 1,
                "tool_name": step,
                "status": "failed" if "error" in result else "success",
                "duration_ms": 0,
                "output_summary": str(result)[:300],
            },
        )

    state["tool_results"] = results

    add_reasoning(state, f"Tools executed: {list(results.keys())}", node="tool_executor")

    return state