import os

from PIL import Image

from config.settings import ExportSettings
from utils.metadata import copy_exif


class Exporter:
    def __init__(self, settings: ExportSettings) -> None:
        self._settings = settings

    def save(self, image: Image.Image, original_path: str,
             output_dir: str, index: int = 0) -> str:
        os.makedirs(output_dir, exist_ok=True)
        base = os.path.basename(original_path)
        name, _ = os.path.splitext(base)
        pattern = self._settings.rename_pattern
        suffix = self._settings.suffix
        if pattern:
            name = pattern.replace("{n}", str(index + 1))
        output_name = f"{name}{suffix}{self._settings.format}"
        output_path = os.path.join(output_dir, output_name)
        if self._settings.keep_exif:
            original = Image.open(original_path)
            image = copy_exif(original, image)
        ext = self._settings.format.lower()
        save_kwargs: dict = {}
        if ext in (".jpg", ".jpeg", ".webp"):
            save_kwargs["quality"] = self._settings.quality
        elif ext == ".png":
            save_kwargs["compress_level"] = max(0, min(9,
                int((100 - self._settings.quality) / 10)))
        image.save(output_path, **save_kwargs)
        return output_path

    def save_all(self, images: list[Image.Image], original_paths: list[str],
                 output_dir: str) -> list[str]:
        paths = []
        for i, (img, orig) in enumerate(zip(images, original_paths)):
            p = self.save(img, orig, output_dir, i)
            paths.append(p)
        return paths
