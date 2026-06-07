import tempfile
import unittest
import importlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image, ImageDraw

from app.tools.pdf_tool import extract_pdf_text


class PdfExtractionTests(unittest.TestCase):
    def test_hybrid_pdf_uses_native_and_ocr(self):
        fitz = importlib.import_module("fitz")
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = Path(temp_dir) / "hybrid.pdf"
            image_path = Path(temp_dir) / "scanned.png"

            image = Image.new("RGB", (1200, 600), color="white")
            draw = ImageDraw.Draw(image)
            draw.text((50, 80), "Scanned page content from OCR", fill="black")
            image.save(image_path)

            document = fitz.open()
            page_1 = document.new_page()
            page_1.insert_text(
                (72, 72),
                "This is a native PDF page with enough readable content to avoid OCR.",
            )
            page_2 = document.new_page()
            page_2.insert_image(page_2.rect, filename=str(image_path))
            document.save(pdf_path)
            document.close()

            dummy_engine = SimpleNamespace(
                predict=lambda _: [{"rec_texts": ["Scanned page content from OCR"]}]
            )

            with patch("app.tools.pdf_tool.get_ocr_engine", return_value=dummy_engine):
                result = extract_pdf_text(str(pdf_path))

            self.assertEqual(result["page_count"], 2)
            self.assertEqual(result["native_pages_count"], 1)
            self.assertEqual(result["ocr_pages_count"], 1)
            self.assertIn("native", result["pages"][0]["extraction_method"])
            self.assertIn("ocr", result["pages"][1]["extraction_method"])
            self.assertIn("Scanned page content from OCR", result["text"])


if __name__ == "__main__":
    unittest.main()