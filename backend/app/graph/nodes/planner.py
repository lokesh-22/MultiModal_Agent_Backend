from app.graph.state import AgentState
from app.graph.nodes.event_utils import add_reasoning, emit_event


AVAILABLE_TOOLS = [
    "summarizer",
    "code_analyzer",
    "compare_documents",
    "qa",
    "youtube_transcript",
    "pdf_extractor",
    "ocr",
    "audio_transcriber",
    "sentiment",
]


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
    return kinds


def _fallback_plan(intent: str, files: list[str]):
    kinds = _detect_file_kinds(files)

    if intent == "COMPARE" and len(files) >= 2:
        return ["compare_documents"]
    if intent == "CODE_EXPLAIN":
        return ["ocr", "code_analyzer"] if "image" in kinds else ["code_analyzer"]
    if intent == "YOUTUBE_SUMMARY":
        return ["youtube_transcript", "summarizer"]
    if intent == "OCR":
        return ["ocr"]
    if intent == "QA":
        return ["qa"]
    if intent == "SUMMARY":
        if "pdf" in kinds:
            return ["pdf_extractor", "summarizer"]
        if "image" in kinds:
            return ["ocr", "summarizer"]
        if "audio" in kinds:
            return ["audio_transcriber", "summarizer"]
        return ["summarizer"]
    if intent == "SENTIMENT":
        return ["sentiment"]
    return ["summarizer"]


def planner(
    state: AgentState
):

    intent = (
        state.get("intent", "UNKNOWN")
        .strip()
        .upper()
    )

    files = state.get("uploaded_files", [])
    execution_plan = _fallback_plan(intent, files)

    state["execution_plan"] = (
        execution_plan
    )

    emit_event(
        state,
        "plan_generated",
        {
            "steps": execution_plan,
            "planner_provider": "rules",
            "rationale": "Rule-based minimal viable tool chain",
        },
    )
    add_reasoning(state, f"Plan generated: {execution_plan}", node="planner")

    return state
