from config.constants import FLATTENED_PRESETS


def get_preset_size(preset_key: str) -> tuple[int, int]:
    for platform, name, size in FLATTENED_PRESETS:
        label = f"{platform} - {name}"
        if label == preset_key:
            return size
    return (1080, 1080)


def get_crop_box(img_w: int, img_h: int,
                 target_w: int, target_h: int) -> tuple[float, float]:
    """Largest box with the target aspect ratio that fits inside the image."""
    aspect = target_w / target_h
    if img_w / img_h > aspect:
        crop_h = float(img_h)
        crop_w = crop_h * aspect
    else:
        crop_w = float(img_w)
        crop_h = crop_w / aspect
    return crop_w, crop_h


def clamp_crop_center(img_w: int, img_h: int,
                      target_w: int, target_h: int,
                      cx: float, cy: float) -> tuple[float, float]:
    """Keep the requested center inside the range where the crop box fits."""
    crop_w, crop_h = get_crop_box(img_w, img_h, target_w, target_h)
    if crop_w >= img_w:
        cx = 0.5
    else:
        half_x = crop_w / (2 * img_w)
        cx = min(1.0 - half_x, max(half_x, cx))
    if crop_h >= img_h:
        cy = 0.5
    else:
        half_y = crop_h / (2 * img_h)
        cy = min(1.0 - half_y, max(half_y, cy))
    return cx, cy


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
