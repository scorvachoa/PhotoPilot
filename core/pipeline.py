import numpy as np
from PIL import Image

from core.state import AppState
from opencv.smart_crop import SmartCrop
from processing.auto_enhance import AutoEnhancer
from processing.manual_adjustments import ManualAdjustments
from utils.aspect_ratio import get_preset_size

PREVIEW_MAX_SIZE = 1800


class ProcessingPipeline:
    """Crop + auto-enhance + manual adjustments.

    The crop/auto-enhance stage is cached so dragging a slider only re-runs
    the (cheap) manual adjustments. For the on-screen preview the cached base
    is downscaled once, which keeps fine adjustments responsive on large
    photos while exports keep working at full resolution.
    """

    def __init__(self) -> None:
        self._smart_crop = SmartCrop()
        self._enhancer = AutoEnhancer()
        self._base_key: tuple | None = None
        self._base_image: Image.Image | None = None
        self._preview_key: tuple | None = None
        self._preview_image: Image.Image | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def process(self, state: AppState,
                max_size: int | None = None) -> Image.Image | None:
        if state.original_image is None:
            return None
        base = self._base(state)
        work = self._scaled(base, max_size)
        img = ManualAdjustments(work, state.processing).apply()
        state.processed_image = img
        return img

    def quick_enhance(self, state: AppState) -> Image.Image | None:
        if state.original_image is None:
            return None
        state.enhance_enabled = True
        return self.process(state)

    def quick_crop(self, state: AppState) -> Image.Image | None:
        if state.original_image is None:
            return None
        state.crop_enabled = True
        return self.process(state)

    def suggest_center(self, image: Image.Image) -> tuple[float, float]:
        """Face-based center suggestion used when a photo is first opened."""
        sample = image
        if max(image.size) > 720:
            sample = image.copy()
            sample.thumbnail((720, 720), Image.BILINEAR)
        cv_img = np.array(sample)[:, :, ::-1].copy()
        try:
            return self._smart_crop.suggest_center(cv_img)
        except Exception:
            return (0.5, 0.5)

    # ------------------------------------------------------------------
    # Cached stages
    # ------------------------------------------------------------------
    def _base(self, state: AppState) -> Image.Image:
        key = (
            id(state.original_image),
            state.crop_enabled,
            state.crop_preset,
            round(state.crop_center_x, 5),
            round(state.crop_center_y, 5),
            state.enhance_enabled,
        )
        if key == self._base_key and self._base_image is not None:
            return self._base_image

        img = state.original_image.copy()
        if state.crop_enabled:
            target = get_preset_size(state.crop_preset)
            cv_img = np.array(img)[:, :, ::-1].copy()
            cropped = self._smart_crop.crop(
                cv_img, target[0], target[1],
                state.crop_center_x, state.crop_center_y,
            )
            img = Image.fromarray(cropped[:, :, ::-1])
        if state.enhance_enabled:
            img = self._enhancer.apply(img)

        self._base_key = key
        self._base_image = img
        self._preview_key = None
        self._preview_image = None
        return img

    def _scaled(self, image: Image.Image,
                max_size: int | None) -> Image.Image:
        if not max_size or max(image.size) <= max_size:
            return image
        key = (self._base_key, max_size)
        if key == self._preview_key and self._preview_image is not None:
            return self._preview_image
        preview = image.copy()
        preview.thumbnail((max_size, max_size), Image.LANCZOS)
        self._preview_key = key
        self._preview_image = preview
        return preview
