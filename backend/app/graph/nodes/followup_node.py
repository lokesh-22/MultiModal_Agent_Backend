
from app.graph.state import AgentState
from app.graph.nodes.event_utils import add_reasoning, emit_event

from app.services.groq_service import invoke_groq_text


def followup_node(
    state: AgentState
):

    prompt = f"""
Write one concise follow-up question to clarify the user's request.

User Query: {state.get('user_query', '')}
Intent: {state.get('intent', 'UNKNOWN')}
Current Hint: {state.get('followup_question', '')}
"""

    try:
        followup_question = invoke_groq_text(prompt).strip()
    except Exception:
        followup_question = state.get("followup_question", "Could you clarify your request?")

    state["execution_plan"] = []

    state["final_response"] = followup_question
    state["needs_followup"] = True

    emit_event(
        state,
        "followup_required",
        {
            "question": followup_question,
            "reason": "followup_node",
            "missing": [],
        },
    )
    emit_event(
        state,
        "final_response",
        {
            "content": followup_question,
            "followup_question": followup_question,
            "needs_followup": True,
            "citations": [],
            "tool_results_summary": {
                "tools_used": [],
            },
            "finish_reason": "followup",
        },
    )
    add_reasoning(state, "Followup requested", node="followup_node")

    return state
