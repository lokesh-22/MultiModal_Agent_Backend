from app.graph.state import AgentState
from app.graph.nodes.event_utils import add_reasoning, emit_event

from app.services.groq_service import invoke_groq_text


def _fallback_intent(query: str, file_count: int) -> str:
    normalized_query = (query or "").lower()

    if any(keyword in normalized_query for keyword in ["compare", "difference", "versus", "vs"]):
        return "COMPARE"
    if any(keyword in normalized_query for keyword in ["summarize", "summary", "overview", "tl;dr"]):
        return "SUMMARY"
    if any(keyword in normalized_query for keyword in ["explain code", "code", "class", "function", "bug"]):
        return "CODE_EXPLAIN"
    if any(keyword in normalized_query for keyword in ["youtube", "video"]):
        return "YOUTUBE_SUMMARY"
    if any(keyword in normalized_query for keyword in ["ocr", "image text", "scan"]):
        return "OCR"
    if file_count and normalized_query:
        return "QA"
    return "UNKNOWN"


def intent_detector(
    state: AgentState
):

    prompt = f"""
Determine the user's intent.

Possible intents:

SUMMARY
SENTIMENT
CODE_EXPLAIN
QA
COMPARE
YOUTUBE_SUMMARY
OCR
UNKNOWN

Return ONLY the intent.

User Query:
{state["user_query"]}
"""

    try:
        intent = invoke_groq_text(prompt).strip().upper()
    except Exception:
        intent = _fallback_intent(state.get("user_query", ""), len(state.get("uploaded_files", [])))

    valid_intents = {
        "SUMMARY",
        "SENTIMENT",
        "CODE_EXPLAIN",
        "QA",
        "COMPARE",
        "YOUTUBE_SUMMARY",
        "OCR",
        "UNKNOWN",
    }

    if intent not in valid_intents:
        intent = _fallback_intent(state.get("user_query", ""), len(state.get("uploaded_files", [])))

    state["intent"] = intent
    state["plan_routing"] = {
        "provider": "groq",
        "fallback_used": intent == "UNKNOWN",
    }

    emit_event(
        state,
        "intent_detected",
        {
            "intent": intent,
            "confidence": 0.8,
            "provider": "groq" if not state["plan_routing"]["fallback_used"] else "fallback_rules",
        },
    )
    add_reasoning(state, f"Intent detected: {state['intent']}", node="intent_detector")

    return state