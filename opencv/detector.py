from typing import Optional


class DetectorResult:
    def __init__(
        self,
        has_faces: bool = False,
        has_persons: bool = False,
        has_objects: bool = False,
        faces: Optional[list[tuple[int, int, int, int]]] = None,
    ) -> None:
        self.has_faces = has_faces
        self.has_persons = has_persons
        self.has_objects = has_objects
        self.faces = faces or []


class Detector:
    def __init__(self) -> None:
        self._face_cascade = None

    def _lazy_init(self) -> None:
        if self._face_cascade is not None:
            return
        import cv2
        import numpy as np
        self._cv2 = cv2
        self._np = np
        self._face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def detect(self, image) -> DetectorResult:
        self._lazy_init()
        gray = self._cv2.cvtColor(image, self._cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        result = DetectorResult()
        if len(faces) > 0:
            result.has_faces = True
            result.faces = [(int(x), int(y), int(w), int(h)) for (x, y, w, h) in faces]
        return result
