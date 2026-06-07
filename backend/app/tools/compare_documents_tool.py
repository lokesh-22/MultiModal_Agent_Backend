from app.services.gemini_service import invoke_gemini_text


def compare_documents(text: str):
    prompt = f"""
Compare the documents below.

Return:
1. Similarities
2. Differences
3. Key takeaways
4. Recommendation if one document is better suited for the user's query

Documents:

{text}
"""

    return invoke_gemini_text(prompt)


def compare_documents_state(state):
    return {
        "tool": "compare_documents",
        "comparison": compare_documents(state.get("combined_context", "")),
    }