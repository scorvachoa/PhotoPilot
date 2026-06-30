CROP_PRESETS: dict[str, dict[str, tuple[int, int]]] = {
    "Facebook": {
        "Feed horizontal": (1200, 630),
        "Feed vertical": (1080, 1350),
        "Feed cuadrado": (1080, 1080),
        "Historia / Reels": (1080, 1920),
        "Portada": (820, 312),
        "Perfil": (180, 180),
    },
    "Instagram": {
        "Feed cuadrado": (1080, 1080),
        "Retrato": (1080, 1350),
        "Paisaje": (1080, 566),
        "Historia / Reels": (1080, 1920),
        "IGTV": (420, 654),
    },
    "LinkedIn": {
        "Feed horizontal": (1200, 627),
        "Feed cuadrado": (1080, 1080),
        "Feed vertical": (1080, 1350),
        "Portada": (1584, 396),
        "Perfil": (400, 400),
    },
    "Pinterest": {
        "Pin estandar": (1000, 1500),
        "Pin cuadrado": (1000, 1000),
        "Pin horizontal": (1000, 750),
    },
    "Twitter / X": {
        "Feed horizontal": (1600, 900),
        "Feed cuadrado": (1080, 1080),
        "Feed vertical": (1080, 1350),
        "Banner": (1500, 500),
        "Perfil": (400, 400),
    },
    "YouTube": {
        "Miniatura": (1280, 720),
        "Banner": (2560, 1440),
        "Perfil": (800, 800),
    },
    "Personalizado": {
        "Cuadrado 1:1": (1080, 1080),
        "Horizontal 16:9": (1920, 1080),
        "Vertical 4:5": (1080, 1350),
        "Vertical 9:16": (1080, 1920),
        "Panoramica 3:1": (1800, 600),
    },
}

FLATTENED_PRESETS: list[tuple[str, str, tuple[int, int]]] = [
    (platform, name, size)
    for platform, sizes in CROP_PRESETS.items()
    for name, size in sizes.items()
]

SUPPORTED_EXTENSIONS: tuple[str, ...] = (
    ".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp",
)

EXPORT_FORMATS: tuple[str, ...] = (".jpg", ".png", ".webp")

APP_NAME: str = "PhotoPilot"
APP_VERSION: str = "1.0.0"
APP_GEOMETRY: str = "1400x900"
