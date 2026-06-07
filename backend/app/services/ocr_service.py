from __future__ import annotations

from functools import lru_cache

from paddleocr import PaddleOCR


@lru_cache(maxsize=1)
def get_ocr_engine() -> PaddleOCR:
    return PaddleOCR(
        lang="en",
        use_angle_cls=True,
    )


def warm_ocr_engine() -> None:
    get_ocr_engine()
