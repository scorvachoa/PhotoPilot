import os

from config.constants import SUPPORTED_EXTENSIONS


def is_supported_image(filepath: str) -> bool:
    ext = os.path.splitext(filepath)[1].lower()
    return ext in SUPPORTED_EXTENSIONS


def get_image_files(directory: str) -> list[str]:
    if not os.path.isdir(directory):
        return []
    files = []
    for f in os.listdir(directory):
        full = os.path.join(directory, f)
        if os.path.isfile(full) and is_supported_image(full):
            files.append(full)
    return sorted(files)
