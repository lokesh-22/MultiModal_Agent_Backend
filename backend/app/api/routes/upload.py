from typing import List

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.file import UploadResponse, StoredFileMetadata
from app.services.file_service import build_file_metadata, save_file

router = APIRouter()

@router.post("/upload")
async def upload_files(
    query: str = Form(""),
    files: List[UploadFile] = File(default=[])
):
    saved_files: list[StoredFileMetadata] = []

    for file in files:
        path = await save_file(file)
        metadata = build_file_metadata(path, file.content_type)
        saved_files.append(StoredFileMetadata(**metadata))

    return UploadResponse(
        files=saved_files,
        query=query,
    )

