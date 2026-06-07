from app.graph.state import AgentState
from app.graph.nodes.event_utils import add_reasoning, emit_event

from app.services.gemini_service import invoke_gemini_text, stream_gemini_text


def response_generator(
    state: AgentState
):
    tool_results = state.get("tool_results", {})

    prompt = f"""
You are the final answer synthesizer.

Use the user query, the built context, and any tool results to answer clearly and directly.

User Query:
{state.get('user_query', '')}

Context:
{state.get('combined_context', '')}

Tool Results:
{tool_results}

Reasoning Trace:
{state.get('reasoning_trace', [])}
"""

    try:
        token_index = 0
        token_chunks = []
        for token in stream_gemini_text(prompt):
            token_chunks.append(token)
            emit_event(
                state,
                "token",
                {
                    "text": token,
                    "provider": "gemini",
                    "model": "gemini",
                    "token_index": token_index,
                },
            )
            token_index += 1

        state["final_response"] = "".join(token_chunks).strip()

        if not state["final_response"]:
            state["final_response"] = invoke_gemini_text(prompt)
    except Exception as exc:
        state["final_response"] = str(tool_results) if tool_results else f"Response generation failed: {exc}"

    emit_event(
        state,
        "final_response",
        {
            "content": state["final_response"],
            "citations": [],
            "tool_results_summary": {
                "tools_used": list(tool_results.keys()),
            },
            "finish_reason": "stop",
        },
    )
    add_reasoning(state, "Response generated", node="response_generator")

    return state
