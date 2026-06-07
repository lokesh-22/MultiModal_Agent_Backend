from app.graph.state import AgentState
from app.graph.nodes.event_utils import add_reasoning, emit_event

from app.services.tool_registry import get_tool


SUPPORTED_TOOL_REQUIREMENTS = {
    "SUMMARY": {"any": ["pdf", "image", "audio", "youtube"]},
    "SENTIMENT": {"any": ["text"]},
    "CODE_EXPLAIN": {"any": ["image", "text"]},
    "QA": {"any": ["text", "pdf", "image", "audio"]},
    "COMPARE": {"min_files": 2},
    "YOUTUBE_SUMMARY": {"any": ["youtube"]},
    "OCR": {"any": ["image", "pdf"]},
}


def _detect_file_kinds(files: list[str]) -> set[str]:
    kinds: set[str] = set()
    for file_path in files:
        lower = file_path.lower()
        if lower.endswith(".pdf"):
            kinds.add("pdf")
        elif any(lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"]):
            kinds.add("image")
        elif any(lower.endswith(ext) for ext in [".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"]):
            kinds.add("audio")
        elif any(lower.endswith(ext) for ext in [".txt", ".md", ".csv", ".json"]):
            kinds.add("text")
    return kinds


def _has_tool(name: str) -> bool:
    return get_tool(name) is not None


def _can_execute(intent: str, files: list[str], query: str) -> bool:
    kinds = _detect_file_kinds(files)
    intent = intent.upper()

    if intent == "UNKNOWN":
        return False

    if intent == "COMPARE":
        return len(files) >= 2 and _has_tool("compare_documents")

    if intent == "YOUTUBE_SUMMARY":
        return _has_tool("youtube_transcript") and _has_tool("summarizer")

    if intent == "OCR":
        return bool(kinds & {"image", "pdf"}) and _has_tool("ocr")

    if intent == "CODE_EXPLAIN":
        return _has_tool("code_analyzer") and (_has_tool("ocr") or "code" in query.lower() or bool(kinds & {"image", "text"}))

    if intent == "SUMMARY":
        if kinds & {"pdf", "image", "audio"} and _has_tool("summarizer"):
            return True
        if "youtube" in query.lower() and _has_tool("youtube_transcript") and _has_tool("summarizer"):
            return True
        return _has_tool("summarizer")

    if intent == "SENTIMENT":
        return _has_tool("sentiment")

    if intent == "QA":
        return _has_tool("qa")

    return False


def _make_followup_question(intent: str, files: list[str], query: str) -> str:
    kinds = _detect_file_kinds(files)
    query_lower = query.lower()

    if not query:
        return "What would you like me to do with the uploaded files?"

    if intent == "UNKNOWN":
        return (
            "I’m not sure what you want me to do. "
            "Should I summarize, compare, answer questions, or extract text?"
        )

    if intent == "COMPARE" and len(files) < 2:
        return "Comparison needs at least two files. Please upload another document."

    if intent == "YOUTUBE_SUMMARY" and "youtube" not in query_lower:
        return "Please provide the YouTube link or a video file to summarize."

    if intent == "OCR" and not (kinds & {"image", "pdf"}):
        return "Please upload an image or scanned PDF for OCR."

    return ""


def ambiguity_checker(
    state: AgentState
):

    state["needs_followup"] = False
    state["followup_question"] = ""

    query = state.get("user_query", "").strip()
    files = state.get("uploaded_files", [])
    intent = state.get("intent", "UNKNOWN").strip().upper()

    followup_question = _make_followup_question(intent, files, query)
    can_execute = _can_execute(intent, files, query)

    if followup_question and not can_execute:
        state["needs_followup"] = True
        state["followup_question"] = followup_question
        emit_event(
            state,
            "followup_required",
            {
                "question": followup_question,
                "reason": "insufficient_information",
                "missing": [],
            },
        )
        add_reasoning(state, f"Follow-up required: {followup_question}", node="ambiguity_checker")
        return state

    if intent == "UNKNOWN":
        state["needs_followup"] = True
        state["followup_question"] = (
            "I’m not sure what you want me to do. Should I summarize, compare, answer questions, or extract text?"
        )
        emit_event(
            state,
            "followup_required",
            {
                "question": state["followup_question"],
                "reason": "intent_unknown",
                "missing": ["clear_task"],
            },
        )
        add_reasoning(state, "Follow-up required: intent unknown", node="ambiguity_checker")
        return state

    add_reasoning(
        state,
        f"Ambiguity checked: intent={intent}, files={len(files)}, can_execute={can_execute}",
        node="ambiguity_checker",
    )

    return state
