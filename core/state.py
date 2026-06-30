from dataclasses import dataclass, field
from PIL import Image

from config.settings import ProcessingSettings, ExportSettings
from utils.validators import get_image_files, is_supported_image


@dataclass
class AppState:
    input_dir: str = ""
    output_dir: str = ""
    images: list[str] = field(default_factory=list)
    current_index: int = -1
    original_image: Image.Image | None = None
    processed_image: Image.Image | None = None
    export: ExportSettings = field(default_factory=ExportSettings)
    crop_enabled: bool = True
    enhance_enabled: bool = True
    _crop_presets: dict[int, str] = field(default_factory=dict)
    _crop_centers: dict[int, tuple[float, float]] = field(default_factory=dict)
    _processing_settings: dict[int, ProcessingSettings] = field(default_factory=dict)

    @property
    def crop_preset(self) -> str:
        return self._crop_presets.get(self.current_index, "Facebook - Feed horizontal")

    @crop_preset.setter
    def crop_preset(self, value: str) -> None:
        self._crop_presets[self.current_index] = value

    def set_crop_preset(self, index: int, value: str) -> None:
        self._crop_presets[index] = value

    def apply_preset_to_all(self, value: str) -> None:
        for i in range(len(self.images)):
            self._crop_presets[i] = value

    @property
    def crop_center_x(self) -> float:
        return self._crop_centers.get(self.current_index, (0.5, 0.5))[0]

    @crop_center_x.setter
    def crop_center_x(self, value: float) -> None:
        cx, cy = self._crop_centers.get(self.current_index, (0.5, 0.5))
        self._crop_centers[self.current_index] = (value, cy)

    @property
    def crop_center_y(self) -> float:
        return self._crop_centers.get(self.current_index, (0.5, 0.5))[1]

    @crop_center_y.setter
    def crop_center_y(self, value: float) -> None:
        cx, cy = self._crop_centers.get(self.current_index, (0.5, 0.5))
        self._crop_centers[self.current_index] = (cx, value)

    def set_crop_center(self, index: int, x: float, y: float) -> None:
        self._crop_centers[index] = (x, y)

    def apply_center_to_all(self, x: float, y: float) -> None:
        for i in range(len(self.images)):
            self._crop_centers[i] = (x, y)

    @property
    def processing(self) -> ProcessingSettings:
        if self.current_index not in self._processing_settings:
            self._processing_settings[self.current_index] = ProcessingSettings()
        return self._processing_settings[self.current_index]

    @processing.setter
    def processing(self, value: ProcessingSettings) -> None:
        self._processing_settings[self.current_index] = value

    def set_processing(self, index: int, settings: ProcessingSettings) -> None:
        self._processing_settings[index] = settings

    def apply_processing_to_all(self) -> None:
        current = self.processing
        for i in range(len(self.images)):
            self._processing_settings[i] = ProcessingSettings(
                brightness=current.brightness,
                contrast=current.contrast,
                saturation=current.saturation,
                exposure=current.exposure,
                sharpness=current.sharpness,
                temperature=current.temperature,
                shadows=current.shadows,
                highlights=current.highlights,
                gamma=current.gamma,
                noise_reduction=current.noise_reduction,
                auto_crop=current.auto_crop,
                auto_enhance=current.auto_enhance,
            )

    def load_directory(self, directory: str) -> list[str]:
        self.input_dir = directory
        self.images = get_image_files(directory)
        self.current_index = -1
        self.original_image = None
        self.processed_image = None
        self._crop_presets.clear()
        self._crop_centers.clear()
        self._processing_settings.clear()
        return self.images

    def load_files(self, file_paths: list[str]) -> list[str]:
        self.input_dir = ""
        self.images = [p for p in file_paths
                       if is_supported_image(p)]
        self.current_index = -1
        self.original_image = None
        self.processed_image = None
        self._crop_presets.clear()
        self._crop_centers.clear()
        self._processing_settings.clear()
        return self.images

    def open_image(self, index: int) -> Image.Image | None:
        if 0 <= index < len(self.images):
            self.current_index = index
            self.original_image = Image.open(self.images[index]).convert("RGB")
            self.processed_image = None
            return self.original_image
        return None

    def reset(self) -> None:
        self._crop_presets.clear()
        self._crop_centers.clear()
        self._processing_settings.clear()
        self.crop_enabled = True
        self.enhance_enabled = True

    def current_filename(self) -> str:
        if 0 <= self.current_index < len(self.images):
            import os
            return os.path.basename(self.images[self.current_index])
        return ""
