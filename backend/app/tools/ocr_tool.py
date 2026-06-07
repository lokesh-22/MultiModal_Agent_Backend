from app.services.ocr_service import get_ocr_engine
from app.tools.pdf_tool import _parse_ocr_result


def extract_image_text(image_path: str):
    result = get_ocr_engine().predict(image_path)
    return _parse_ocr_result(result)
