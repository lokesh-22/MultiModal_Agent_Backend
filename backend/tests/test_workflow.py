import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.graph.workflow import build_graph


class WorkflowTests(unittest.TestCase):
    def test_graph_runs_end_to_end_for_multifile_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "doc.pdf"
            image_path = Path(temp_dir) / "image.png"
            audio_path = Path(temp_dir) / "audio.mp3"

            for path in (pdf_path, image_path, audio_path):
                path.write_bytes(b"test")

            graph = build_graph()

            with patch("app.graph.nodes.intent_detector.invoke_groq_text", return_value="SUMMARY"), \
                patch("app.graph.nodes.ambiguity_checker.invoke_groq_text", return_value="NO_FOLLOWUP"), \
                patch("app.graph.nodes.planner.invoke_groq_text", return_value='["summarizer"]'), \
                patch("app.graph.nodes.response_generator.invoke_gemini_text", return_value="final answer"), \
                patch("app.graph.nodes.content_extractor.extract_pdf_text", return_value={"text": "pdf text", "page_count": 1, "native_pages_count": 1, "ocr_pages_count": 0, "pages": [], "extraction_method": "native", "source_path": str(pdf_path)}), \
                patch("app.graph.nodes.content_extractor.extract_image_text", return_value="image text"), \
                patch("app.graph.nodes.content_extractor.transcribe_audio", return_value={"text": "audio text", "segments": [], "language": "en", "duration": 1.0, "model": "small", "source_path": str(audio_path)}), \
                patch("app.tools.summarizer_tool.invoke_gemini_text", return_value="summary result"):
                result = graph.invoke(
                    {
                        "user_query": "summarize these files",
                        "uploaded_files": [str(pdf_path), str(image_path), str(audio_path)],
                        "reasoning_trace": [],
                    }
                )

            self.assertEqual(result["intent"], "SUMMARY")
            self.assertEqual(result["execution_plan"], ["summarizer"])
            self.assertIn("Source: ", result["combined_context"])
            self.assertEqual(result["tool_results"]["summarizer"]["summary"], "summary result")
            self.assertEqual(result["final_response"], "final answer")


if __name__ == "__main__":
    unittest.main()