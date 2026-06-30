from dataclasses import dataclass, field


@dataclass
class ProcessingSettings:
    brightness: float = 0.0
    contrast: float = 0.0
    saturation: float = 0.0
    exposure: float = 0.0
    sharpness: float = 0.0
    temperature: float = 0.0
    shadows: float = 0.0
    highlights: float = 0.0
    gamma: float = 1.0
    noise_reduction: float = 0.0
    auto_crop: bool = True
    auto_enhance: bool = True


@dataclass
class ExportSettings:
    format: str = ".jpg"
    quality: int = 95
    keep_exif: bool = True
    rename_pattern: str = ""
    suffix: str = ""


@dataclass
class AppSettings:
    last_input_dir: str = ""
    last_output_dir: str = ""
    theme: str = "light"
    language: str = "es"
    processing: ProcessingSettings = field(default_factory=ProcessingSettings)
    export: ExportSettings = field(default_factory=ExportSettings)
