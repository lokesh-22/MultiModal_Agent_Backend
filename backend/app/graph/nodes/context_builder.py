from app.graph.state import AgentState
from app.graph.nodes.event_utils import add_reasoning


def context_builder(
    state: AgentState
):

    combined_sections = []

    extracted_contents = state.get(
        "extracted_contents",
        {}
    )

    for file_path, data in extracted_contents.items():
        content = data.get("content", {})
        text = content.get("text", "") if isinstance(content, dict) else str(content)

        section_lines = [
            f"Source: {file_path}",
            f"Type: {data.get('type', 'unknown')}",
        ]

        if isinstance(content, dict):
            if content.get("page_count") is not None:
                section_lines.append(f"Pages: {content.get('page_count')}")
            if content.get("native_pages_count") is not None:
                section_lines.append(f"Native pages: {content.get('native_pages_count')}")
            if content.get("ocr_pages_count") is not None:
                section_lines.append(f"OCR pages: {content.get('ocr_pages_count')}")

        section_lines.append("Content:")
        section_lines.append(text)
        combined_sections.append("\n".join(section_lines).strip())

    combined_sections.append(f"USER QUERY:\n{state.get('user_query', '')}")

    state["combined_context"] = (
        "\n\n---\n\n".join(combined_sections).strip()
    )

    add_reasoning(state, "Context built", node="context_builder")

    return state