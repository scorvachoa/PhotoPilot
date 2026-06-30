import numpy as np
from PIL import Image

from core.state import AppState
from opencv.smart_crop import SmartCrop
from processing.auto_enhance import AutoEnhancer
from processing.manual_adjustments import ManualAdjustments
from utils.aspect_ratio import get_preset_size


class ProcessingPipeline:
    def __init__(self) -> None:
        self._smart_crop = SmartCrop()
        self._enhancer = AutoEnhancer()

    def process(self, state: AppState) -> Image.Image | None:
        if state.original_image is None:
            return None
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
        adjustments = ManualAdjustments(img, state.processing)
        img = adjustments.apply()
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
