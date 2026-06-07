from app.tools.audio_tool import transcribe_audio
from app.tools.code_analyzer_tool import analyze_code_state
from app.tools.compare_documents_tool import compare_documents_state
from app.tools.ocr_tool import extract_image_text
from app.tools.pdf_tool import extract_pdf_text
from app.tools.qa_tool import qa_state
from app.tools.sentiment_tool import sentiment_state
from app.tools.summarizer_tool import summarize_state
from app.tools.youtube_tool import youtube_transcript_state


def _extract_pdf_state(state):
    extracted = state.get("extracted_contents", {})
    documents = []
    for path in state.get("uploaded_files", []):
        record = extracted.get(path)
        if record and record.get("type") == "pdf":
            documents.append(record.get("content", {}))
        else:
            documents.append(extract_pdf_text(path))
    return {
        "documents": documents,
        "tool": "pdf_extractor",
    }


def _extract_image_state(state):
    extracted = state.get("extracted_contents", {})
    documents = []
    for path in state.get("uploaded_files", []):
        record = extracted.get(path)
        if record and record.get("type") == "image":
            documents.append(record.get("content", {}))
        else:
            documents.append(
                {
                    "type": "image",
                    "source_path": path,
                    "text": extract_image_text(path),
                }
            )
    return {
        "documents": documents,
        "tool": "ocr",
    }


def _extract_audio_state(state):
    extracted = state.get("extracted_contents", {})
    documents = []
    for path in state.get("uploaded_files", []):
        record = extracted.get(path)
        if record and record.get("type") == "audio":
            documents.append(record.get("content", {}))
        else:
            documents.append(transcribe_audio(path))
    return {
        "documents": documents,
        "tool": "audio_transcriber",
    }


TOOL_REGISTRY = {
    "summarizer": summarize_state,
    "sentiment": sentiment_state,
    "code_analyzer": analyze_code_state,
    "compare_documents": compare_documents_state,
    "qa": qa_state,
    "youtube_transcript": youtube_transcript_state,
    "pdf_extractor": _extract_pdf_state,
    "ocr": _extract_image_state,
    "audio_transcriber": _extract_audio_state,
}


def get_tool(name):
    return TOOL_REGISTRY.get(name)
