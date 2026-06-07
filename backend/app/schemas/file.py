from __future__ import annotations

from pydantic import BaseModel


class StoredFileMetadata(BaseModel):
	file_name: str
	file_path: str
	file_type: str
	size_bytes: int
	content_type: str | None = None


class UploadResponse(BaseModel):
	files: list[StoredFileMetadata]
	query: str = ""
