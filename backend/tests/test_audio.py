import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.tools.audio_tool import transcribe_audio


class AudioTranscriptionTests(unittest.TestCase):
    def test_audio_transcription_returns_segments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = Path(temp_dir) / "sample.mp3"
            audio_path.write_bytes(b"test")

            dummy_model = SimpleNamespace(
                transcribe=lambda *_args, **_kwargs: (
                    [
                        SimpleNamespace(start=0.0, end=1.0, text="Hello"),
                        SimpleNamespace(start=1.0, end=2.0, text="world"),
                    ],
                    SimpleNamespace(language="en", duration=2.0),
                )
            )

            with patch("app.tools.audio_tool.get_whisper_model", return_value=dummy_model):
                result = transcribe_audio(str(audio_path))

            self.assertEqual(result["text"], "Hello world")
            self.assertEqual(len(result["segments"]), 2)
            self.assertEqual(result["language"], "en")


if __name__ == "__main__":
    unittest.main()