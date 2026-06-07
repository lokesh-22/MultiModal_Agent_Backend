import re

from youtube_transcript_api import YouTubeTranscriptApi

from app.services.gemini_service import invoke_gemini_text


YOUTUBE_URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{6,})"
)


def extract_youtube_url(text: str):
    match = YOUTUBE_URL_PATTERN.search(text or "")
    return match.group(0) if match else ""


def fetch_youtube_transcript(url: str):
    match = YOUTUBE_URL_PATTERN.search(url or "")
    video_id = match.group(1) if match else ""

    if not video_id:
        return {
            "tool": "youtube_transcript",
            "url": url,
            "text": "",
            "error": "No valid YouTube URL found.",
        }

    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = " ".join(item["text"] for item in transcript if item.get("text"))

    return {
        "tool": "youtube_transcript",
        "url": url,
        "video_id": video_id,
        "text": transcript_text,
        "segments": transcript,
    }


def youtube_transcript_state(state):
    context_text = state.get("combined_context", "")
    url = extract_youtube_url(context_text) or extract_youtube_url(state.get("user_query", ""))
    transcript = fetch_youtube_transcript(url)

    summary = ""
    if transcript.get("text"):
        summary = invoke_gemini_text(
            f"""
Summarize the transcript below.

{transcript.get('text', '')}
"""
        )

    return {
        "tool": "youtube_transcript",
        "transcript": transcript,
        "summary": summary,
    }