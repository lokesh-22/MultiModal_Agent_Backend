import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image, ImageDraw

from app.tools.ocr_tool import extract_image_text


class ImageOcrTests(unittest.TestCase):
    def test_image_ocr_returns_detected_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "sample.png"
            image = Image.new("RGB", (1200, 600), color="white")
            draw = ImageDraw.Draw(image)
            draw.text((50, 80), "Hello OCR world", fill="black")
            image.save(image_path)

            dummy_engine = SimpleNamespace(
                predict=lambda _: [{"rec_texts": ["Hello OCR world"]}]
            )

            with patch("app.tools.ocr_tool.get_ocr_engine", return_value=dummy_engine):
                text = extract_image_text(str(image_path))

            self.assertEqual(text, "Hello OCR world")


if __name__ == "__main__":
    unittest.main()