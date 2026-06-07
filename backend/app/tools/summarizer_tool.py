from app.services.gemini_service import invoke_gemini_text


def summarize(
    text: str
):

    prompt = f"""
Summarize the following document.

Return:

1. One-line summary

2. Three bullet points

3. Five sentence summary

Document:

{text}
"""

    return invoke_gemini_text(prompt)


def summarize_state(state):
    combined_context = state.get("combined_context", "")
    tool_results = state.get("tool_results", {})
    context_segments = [combined_context]

    if tool_results:
        context_segments.append(str(tool_results))

    return {
        "tool": "summarizer",
        "summary": summarize("\n\n".join(segment for segment in context_segments if segment)),
    }