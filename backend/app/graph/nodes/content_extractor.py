from app.graph.state import AgentState
from app.graph.nodes.event_utils import add_reasoning, emit_event

from app.utils.file_utils import get_file_type

from app.tools.pdf_tool import extract_pdf_text

from app.tools.ocr_tool import (
    extract_image_text
)
from app.tools.audio_tool import transcribe_audio


def _wrap_record(file_path: str, file_type: str, content: dict):
    return {
        "file_path": file_path,
        "type": file_type,
        "content": content,
    }


def content_extractor(
    state: AgentState
):

    extracted_contents = {}
    source_documents = []

    uploaded_files = state.get(
        "uploaded_files",
        []
    )

    for file_path in uploaded_files:

        file_type = get_file_type(
            file_path
        )

        file_meta = state.get("uploaded_file_metadata", {}).get(file_path, {})
        file_id = file_meta.get("file_path", file_path)
        emit_event(
            state,
            "file_processing_started",
            {
                "file_id": file_id,
                "file_name": file_meta.get("file_name", file_path),
                "file_type": file_type,
                "size_bytes": file_meta.get("size_bytes", 0),
            },
        )

        if file_type == "pdf":
            def page_callback(event_type, payload):
                emit_event(
                    state,
                    event_type,
                    {
                        "file_id": file_id,
                        **payload,
                    },
                )

            pdf_result = extract_pdf_text(file_path, page_event_callback=page_callback)
            extracted_contents[file_path] = _wrap_record(file_path, "pdf", pdf_result)
            source_documents.append(pdf_result)
        elif file_type == "image":
            emit_event(
                state,
                "ocr_started",
                {
                    "file_id": file_id,
                    "source": "image",
                },
            )
            image_text = extract_image_text(file_path)
            emit_event(
                state,
                "ocr_completed",
                {
                    "file_id": file_id,
                    "source": "image",
                    "text_chars": len(image_text),
                },
            )
            image_result = {
                "type": "image",
                "text": image_text,
                "source_path": file_path,
            }
            extracted_contents[file_path] = _wrap_record(file_path, "image", image_result)
            source_documents.append(image_result)
        elif file_type == "audio":
            audio_result = transcribe_audio(
                file_path,
                event_callback=lambda event_type, payload: emit_event(
                    state,
                    event_type,
                    {
                        "file_id": file_id,
                        **payload,
                    },
                ),
            )
            extracted_contents[file_path] = _wrap_record(file_path, "audio", audio_result)
            source_documents.append(audio_result)

        else:
            extracted_contents[file_path] = _wrap_record(
                file_path,
                file_type,
                {
                    "type": file_type,
                    "source_path": file_path,
                    "text": "",
                },
            )

        emit_event(
            state,
            "file_processing_completed",
            {
                "file_id": file_id,
                "file_type": file_type,
                "status": "success",
                "extracted_chars": len(extracted_contents[file_path].get("content", {}).get("text", "")),
                "metadata": extracted_contents[file_path].get("content", {}),
            },
        )

    state["extracted_contents"] = (
        extracted_contents
    )
    state["source_documents"] = source_documents

    add_reasoning(state, "Content extracted", node="content_extractor")

    return state