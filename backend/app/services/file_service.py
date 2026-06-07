import os
import uuid
from pathlib import Path

from fastapi import UploadFile


UPLOAD_DIR = "uploads"

async def save_file(file: UploadFile):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    unique_name = f"{uuid.uuid4()}_{file.filename}"

    path = os.path.join(
        UPLOAD_DIR,
        unique_name
    )

    with open(path, "wb") as f:
        content = await file.read()
        f.write(content)

    return path


def build_file_metadata(path: str, content_type: str | None = None) -> dict:
    file_path = Path(path)
    return {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "file_type": file_path.suffix.lower().lstrip("."),
        "size_bytes": file_path.stat().st_size,
        "content_type": content_type,
    }

