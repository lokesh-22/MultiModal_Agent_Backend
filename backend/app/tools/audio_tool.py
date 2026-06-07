from functools import lru_cache

from faster_whisper import WhisperModel

from app.core.config import settings


@lru_cache(maxsize=1)
def get_whisper_model() -> WhisperModel:
    return WhisperModel(
        settings.WHISPER_MODEL,
        compute_type="int8",
    )


def transcribe_audio(audio_path: str, event_callback=None):
    if event_callback:
        event_callback(
            "audio_transcription_started",
            {
                "model": settings.WHISPER_MODEL,
            },
        )

    model = get_whisper_model()
    segments, info = model.transcribe(audio_path, beam_size=1, vad_filter=True)

    transcript_segments = []
    transcript_text = []

    for segment in segments:
        segment_text = segment.text.strip()
        if not segment_text:
            continue

        transcript_segments.append(
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment_text,
            }
        )
        transcript_text.append(segment_text)

    result = {
        "text": " ".join(transcript_text).strip(),
        "segments": transcript_segments,
        "language": getattr(info, "language", None),
        "duration": getattr(info, "duration", None),
        "model": settings.WHISPER_MODEL,
        "source_path": audio_path,
    }

    if event_callback:
        event_callback(
            "audio_transcription_completed",
            {
                "language": result["language"],
                "duration_sec": result["duration"],
                "transcript_chars": len(result["text"]),
                "segments_count": len(result["segments"]),
            },
        )

    return result