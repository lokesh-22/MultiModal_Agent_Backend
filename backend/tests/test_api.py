import unittest
from unittest.mock import patch

from app.graph.workflow import build_graph


class FollowupWorkflowTests(unittest.TestCase):
    def test_followup_path_uses_groq_generated_question(self):
        graph = build_graph()

        with patch("app.graph.nodes.intent_detector.invoke_groq_text", return_value="SUMMARY"), \
            patch("app.graph.nodes.ambiguity_checker.invoke_groq_text", return_value="Could you clarify what you want summarized?"), \
            patch("app.graph.nodes.followup_node.invoke_groq_text", return_value="Could you clarify what you want summarized?"):
            result = graph.invoke(
                {
                    "user_query": "help",
                    "uploaded_files": [],
                    "reasoning_trace": [],
                }
            )

        self.assertTrue(result["needs_followup"])
        self.assertIn("clarify", result["final_response"].lower())


if __name__ == "__main__":
    unittest.main()