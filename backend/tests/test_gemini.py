import unittest
from unittest.mock import patch

from app.tools.summarizer_tool import summarize, summarize_state


class GeminiToolTests(unittest.TestCase):
    def test_summarizer_uses_gemini(self):
        with patch("app.tools.summarizer_tool.invoke_gemini_text", return_value="summary output"):
            self.assertEqual(summarize("text"), "summary output")

    def test_summarizer_state_wraps_result(self):
        with patch("app.tools.summarizer_tool.invoke_gemini_text", return_value="summary output"):
            result = summarize_state({"combined_context": "text", "tool_results": {}})

        self.assertEqual(result["tool"], "summarizer")
        self.assertEqual(result["summary"], "summary output")


if __name__ == "__main__":
    unittest.main()