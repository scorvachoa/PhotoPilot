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
        self._lazy_init()
        h, w = image.shape[:2]
        abs_cx = int(w * center_x)
        abs_cy = int(h * center_y)
        result = self._detector.detect(image)
        if result.has_faces:
            crop = self._crop_faces(image, result.faces, target_w, target_h,
                                    abs_cx, abs_cy)
        else:
            crop = self._crop_center(image, target_w, target_h, abs_cx, abs_cy)
        return self._cv2.resize(crop, (target_w, target_h),
                                interpolation=self._cv2.INTER_LANCZOS4)

    def _crop_faces(self, image, faces, target_w, target_h, cx, cy):
        h, w = image.shape[:2]
        xs = [x for (x, y, wf, hf) in faces]
        ys = [y for (x, y, wf, hf) in faces]
        max_x = max(x + wf for (x, y, wf, hf) in faces)
        max_y = max(y + hf for (x, y, wf, hf) in faces)
        face_cx = int((min(xs) + max_x) // 2)
        face_cy = int((min(ys) + max_y) // 2)
        blend_cx = int(cx * 0.4 + face_cx * 0.6)
        blend_cy = int(cy * 0.4 + face_cy * 0.6)
        return self._extract_region(image, blend_cx, blend_cy, target_w, target_h, w, h)

    def _crop_center(self, image, target_w, target_h, cx, cy):
        h, w = image.shape[:2]
        return self._extract_region(image, cx, cy, target_w, target_h, w, h)

    def _extract_region(self, image, cx, cy, tw, th, img_w, img_h):
        aspect_target = tw / th
        if img_w / img_h > aspect_target:
            crop_h = img_h
            crop_w = int(crop_h * aspect_target)
        else:
            crop_w = img_w
            crop_h = int(crop_w / aspect_target)
        x1 = max(0, cx - crop_w // 2)
        y1 = max(0, cy - crop_h // 2)
        x2 = min(img_w, x1 + crop_w)
        y2 = min(img_h, y1 + crop_h)
        if x2 - x1 < crop_w:
            x1 = max(0, x2 - crop_w)
        if y2 - y1 < crop_h:
            y1 = max(0, y2 - crop_h)
        return image[y1:y2, x1:x2]
