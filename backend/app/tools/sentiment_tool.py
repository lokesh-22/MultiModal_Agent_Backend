from app.services.gemini_service import invoke_gemini_text


def analyze_sentiment(text: str) -> dict:
    prompt = f"""
Analyze the sentiment of the text below.

Return a compact JSON object with these keys:
- label: one of POSITIVE, NEGATIVE, NEUTRAL, or MIXED
- confidence: a number from 0 to 1
- summary: one short sentence explaining why

Text:
{text}
"""

    response_text = invoke_gemini_text(prompt)
    return {
        "tool": "sentiment",
        "input": text,
        "result": response_text,
    }


def sentiment_state(state):
    combined_context = state.get("combined_context", "")
    tool_results = state.get("tool_results", {})
    segments = [combined_context]

    if tool_results:
        segments.append(str(tool_results))

    return analyze_sentiment("\n\n".join(segment for segment in segments if segment))
