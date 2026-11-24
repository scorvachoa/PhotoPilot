from opencv.detector import Detector


class SmartCrop:
    def __init__(self) -> None:
        self._detector = Detector()
        self._cv2 = None

    def _lazy_init(self) -> None:
        if self._cv2 is not None:
            return
        import cv2
        self._cv2 = cv2

    def crop(self, image, target_w: int, target_h: int,
             center_x: float = 0.5, center_y: float = 0.5):
        """Crop around the exact center requested by the user.

        Face detection is only used to propose the initial center
        (``suggest_center``); once the user frames the photo, their center is
        authoritative so the preview and the export always match.
        """
        self._lazy_init()
        h, w = image.shape[:2]
        cx = w * center_x
        cy = h * center_y
        crop = self._extract_region(image, cx, cy, target_w, target_h, w, h)
        return self._cv2.resize(crop, (target_w, target_h),
                                interpolation=self._cv2.INTER_LANCZOS4)

    def suggest_center(self, image) -> tuple[float, float]:
        """Return a normalized center based on the detected faces."""
        self._lazy_init()
        h, w = image.shape[:2]
        result = self._detector.detect(image)
        if not result.has_faces or not result.faces:
            return (0.5, 0.5)
        min_x = min(x for (x, y, fw, fh) in result.faces)
        min_y = min(y for (x, y, fw, fh) in result.faces)
        max_x = max(x + fw for (x, y, fw, fh) in result.faces)
        max_y = max(y + fh for (x, y, fw, fh) in result.faces)
        cx = (min_x + max_x) / 2 / w
        cy = (min_y + max_y) / 2 / h
        return (min(1.0, max(0.0, cx)), min(1.0, max(0.0, cy)))

    def _extract_region(self, image, cx, cy, tw, th, img_w, img_h):
        aspect_target = tw / th
        if img_w / img_h > aspect_target:
            crop_h = float(img_h)
            crop_w = crop_h * aspect_target
        else:
            crop_w = float(img_w)
            crop_h = crop_w / aspect_target
        crop_w = max(1, min(img_w, int(round(crop_w))))
        crop_h = max(1, min(img_h, int(round(crop_h))))

        x1 = int(round(cx - crop_w / 2))
        y1 = int(round(cy - crop_h / 2))
        x1 = max(0, min(x1, img_w - crop_w))
        y1 = max(0, min(y1, img_h - crop_h))
        return image[y1:y1 + crop_h, x1:x1 + crop_w]
