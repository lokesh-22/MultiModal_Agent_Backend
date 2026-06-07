import os


def get_file_type(path):

    ext = os.path.splitext(path)[1].lower()

    if ext in [".pdf"]:
        return "pdf"

    if ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg", ".tiff", ".tif"]:
        return "image"

    if ext in [".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"]:
        return "audio"

    return "unknown"


