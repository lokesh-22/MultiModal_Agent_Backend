import unittest
from unittest.mock import patch

from app.tools.code_analyzer_tool import analyze_code_state


class CodeAnalyzerTests(unittest.TestCase):
    def test_code_analyzer_wraps_gemini_result(self):
        with patch("app.tools.code_analyzer_tool.invoke_gemini_text", return_value="code explanation"):
            result = analyze_code_state({"combined_context": "print('hello')"})

        self.assertEqual(result["tool"], "code_analyzer")
        self.assertEqual(result["code_analysis"], "code explanation")


if __name__ == "__main__":
    unittest.main()