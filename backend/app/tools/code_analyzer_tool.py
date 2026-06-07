from app.services.gemini_service import invoke_gemini_text


def explain_code(
    code_text: str
):

    prompt = f"""
Explain the following code.

Return:

1. Purpose

2. Step-by-step explanation

3. Time complexity

4. Space complexity

Code:

{code_text}
"""

    return invoke_gemini_text(prompt)


def analyze_code_state(state):
    combined_context = state.get("combined_context", "")
    return {
        "tool": "code_analyzer",
        "code_analysis": explain_code(combined_context),
    }