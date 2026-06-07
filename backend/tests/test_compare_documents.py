import unittest
from unittest.mock import patch

from app.tools.compare_documents_tool import compare_documents, compare_documents_state


class CompareDocumentsTests(unittest.TestCase):
    def test_compare_documents_uses_gemini(self):
        with patch("app.tools.compare_documents_tool.invoke_gemini_text", return_value="comparison result"):
            self.assertEqual(compare_documents("doc a\ndoc b"), "comparison result")

    def test_compare_documents_state_wraps_result(self):
        with patch("app.tools.compare_documents_tool.invoke_gemini_text", return_value="comparison result"):
            result = compare_documents_state({"combined_context": "doc a\ndoc b"})

        self.assertEqual(result["tool"], "compare_documents")
        self.assertEqual(result["comparison"], "comparison result")


if __name__ == "__main__":
    unittest.main()