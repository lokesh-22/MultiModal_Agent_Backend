from app.services.gemini_service import invoke_gemini_text


def answer_question(context: str, question: str):
    prompt = f"""
Answer the user's question using the provided context. If the context is insufficient, say what is missing.

Question:
{question}

Context:
{context}
"""

    return invoke_gemini_text(prompt)


def qa_state(state):
    return {
        "tool": "qa",
        "answer": answer_question(
            state.get("combined_context", ""),
            state.get("user_query", ""),
        ),
    }