import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from config.settings import ProcessingSettings


class ManualAdjustments:
    def __init__(self, image: Image.Image, settings: ProcessingSettings) -> None:
        self._original = image
        self._settings = settings

    def apply(self) -> Image.Image:
        img = self._original.copy()
        s = self._settings

        if s.temperature != 0:
            arr = np.array(img, dtype=np.float32)
            arr[:, :, 0] *= 1 + s.temperature * 0.15
            arr[:, :, 2] *= 1 - s.temperature * 0.15
            arr = arr.clip(0, 255).astype(np.uint8)
            img = Image.fromarray(arr)

        if s.exposure != 0:
            factor = 2.0 ** s.exposure
            img = ImageEnhance.Brightness(img).enhance(factor)

        if s.brightness != 0:
            factor = 1 + s.brightness
            img = ImageEnhance.Brightness(img).enhance(factor)

        if s.contrast != 0:
            factor = 1 + s.contrast
            img = ImageEnhance.Contrast(img).enhance(factor)

        if s.shadows != 0 or s.highlights != 0:
            arr = np.array(img, dtype=np.float32)
            gray = arr.mean(axis=2, keepdims=True) / 255.0
            if s.shadows != 0:
                shadow_weight = 1.0 - gray
                arr += shadow_weight * (s.shadows * 60)
            if s.highlights != 0:
                highlight_weight = gray
                arr -= highlight_weight * (s.highlights * 60)
            arr = arr.clip(0, 255).astype(np.uint8)
            img = Image.fromarray(arr)

        if s.saturation != 0:
            factor = 1 + s.saturation
            img = ImageEnhance.Color(img).enhance(factor)

        if s.sharpness != 0:
            factor = 1 + s.sharpness
            img = ImageEnhance.Sharpness(img).enhance(factor)

        if s.gamma != 1.0:
            arr = np.array(img, dtype=np.float32)
            arr = 255.0 * (arr / 255.0) ** (1.0 / s.gamma)
            arr = arr.clip(0, 255).astype(np.uint8)
            img = Image.fromarray(arr)

        if s.noise_reduction > 0:
            img = img.filter(ImageFilter.MedianFilter(size=3))

        return img
