from config.constants import FLATTENED_PRESETS


def get_preset_size(preset_key: str) -> tuple[int, int]:
    for platform, name, size in FLATTENED_PRESETS:
        label = f"{platform} - {name}"
        if label == preset_key:
            return size
    return (1080, 1080)


def classify_orientation(width: int, height: int) -> str:
    ratio = width / height
    if ratio > 1.1:
        return "horizontal"
    elif ratio < 0.9:
        return "vertical"
    return "square"


def detect_best_preset(img_w: int, img_h: int) -> str | None:
    img_ratio = img_w / img_h
    best_label = None
    best_diff = float("inf")
    for platform, name, (pw, ph) in FLATTENED_PRESETS:
        preset_ratio = pw / ph
        diff = abs(img_ratio - preset_ratio)
        if diff < best_diff:
            best_diff = diff
            best_label = f"{platform} - {name}"
    return best_label
