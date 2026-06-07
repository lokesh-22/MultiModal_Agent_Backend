from __future__ import annotations

import os
import re
import tempfile

import fitz

from app.core.config import settings
from app.services.ocr_service import get_ocr_engine


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def _has_meaningful_text(text: str, word_count: int = 0) -> bool:
    cleaned_text = _normalize_text(text)
    if len(cleaned_text) < max(20, settings.OCR_TEXT_MIN_CHARS // 2):
        return False

    alpha_numeric_count = len(re.findall(r"[A-Za-z0-9]", cleaned_text))
    computed_word_count = len(re.findall(r"[A-Za-z]{2,}", cleaned_text))
    effective_word_count = max(word_count, computed_word_count)

    return effective_word_count >= 5 and alpha_numeric_count / max(len(cleaned_text), 1) >= 0.2


def _parse_ocr_result(result) -> str:
    extracted_text = []

    for page_result in result or []:
        if isinstance(page_result, dict):
            texts = page_result.get("rec_texts") or page_result.get("texts") or []
            if isinstance(texts, str):
                extracted_text.append(texts)
                continue

            if texts:
                extracted_text.extend(str(text).strip() for text in texts if str(text).strip())
                continue

            if isinstance(page_result.get("res"), list):
                for item in page_result["res"]:
                    if isinstance(item, dict):
                        text = item.get("text") or item.get("rec_text")
                        if text:
                            extracted_text.append(str(text).strip())
                    elif isinstance(item, (list, tuple)) and item:
                        extracted_text.append(str(item[-1]).strip())
                continue

        if isinstance(page_result, (list, tuple)) and page_result:
            extracted_text.append(str(page_result[-1]).strip())

    return "\n".join(text for text in extracted_text if text).strip()


def _quality_score(text: str) -> float:
    cleaned_text = _normalize_text(text)
    length_ratio = min(len(cleaned_text) / max(settings.OCR_TEXT_MIN_CHARS, 1), 1.0)
    alpha_numeric_count = len(re.findall(r"[A-Za-z0-9]", cleaned_text))
    alnum_ratio = alpha_numeric_count / max(len(cleaned_text), 1)
    return round((0.6 * length_ratio) + (0.4 * alnum_ratio), 4)


def _ocr_page(page: fitz.Page, page_number: int) -> str:
    pixmap = page.get_pixmap(
        matrix=fitz.Matrix(settings.OCR_RENDER_ZOOM, settings.OCR_RENDER_ZOOM),
        alpha=False,
    )

    with tempfile.NamedTemporaryFile(suffix=f"_page_{page_number}.png", delete=False) as temp_file:
        temp_file.write(pixmap.tobytes("png"))
        temp_path = temp_file.name

    try:
        result = get_ocr_engine().predict(temp_path)
        return _parse_ocr_result(result)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def extract_pdf_text(pdf_path: str, page_event_callback=None):
    doc = fitz.open(pdf_path)
    pages = []
    native_pages_count = 0
    ocr_pages_count = 0

    try:
        for page_number, page in enumerate(doc, start=1):
            words = page.get_text("words") or []
            native_text = _normalize_text(page.get_text("text") or "")
            native_word_count = len(words) if isinstance(words, list) else 0
            quality_score = _quality_score(native_text)

            if _has_meaningful_text(native_text, native_word_count):
                page_text = native_text
                extraction_method = "native"
                native_pages_count += 1
            else:
                if page_event_callback:
                    page_event_callback(
                        "ocr_started",
                        {
                            "page_number": page_number,
                            "source": "pdf_page",
                        },
                    )
                page_text = _normalize_text(_ocr_page(page, page_number))
                extraction_method = "ocr"
                ocr_pages_count += 1
                if page_event_callback:
                    page_event_callback(
                        "ocr_completed",
                        {
                            "page_number": page_number,
                            "source": "pdf_page",
                            "text_chars": len(page_text),
                        },
                    )

            pages.append(
                {
                    "page_number": page_number,
                    "extraction_method": extraction_method,
                    "text": page_text,
                    "character_count": len(page_text),
                    "quality_score": quality_score,
                }
            )

            if page_event_callback:
                page_event_callback(
                    "pdf_page_processed",
                    {
                        "page_number": page_number,
                        "extraction_method": extraction_method,
                        "text_chars": len(page_text),
                        "quality_score": quality_score,
                    },
                )

        return {
            "text": "\n\n".join(page["text"] for page in pages if page["text"]),
            "page_count": len(doc),
            "native_pages_count": native_pages_count,
            "ocr_pages_count": ocr_pages_count,
            "pages": pages,
            "extraction_method": "hybrid",
            "source_path": pdf_path,
        }
    finally:
        doc.close()
