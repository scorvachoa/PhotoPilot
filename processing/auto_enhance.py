from PIL import Image, ImageEnhance, ImageFilter, ImageStat


class AutoEnhancer:
    def __init__(self) -> None:
        self._analysis: dict[str, float] = {}

    def analyze(self, image: Image.Image) -> dict[str, float]:
        gray = image.convert("L")
        stat = ImageStat.Stat(gray)
        mean_brightness = stat.mean[0]
        stat_rgb = ImageStat.Stat(image)
        r, g, b = stat_rgb.mean
        color_temp = r / (g + 0.001)
        extrema = stat.extrema
        contrast = extrema[0][1] - extrema[0][0]
        stat_hsv = ImageStat.Stat(image.convert("HSV"))
        saturation = stat_hsv.mean[1]
        self._analysis = {
            "brightness": mean_brightness,
            "contrast": contrast,
            "saturation": saturation,
            "color_temp": color_temp,
            "exposure": mean_brightness / 255.0,
        }
        return self._analysis

    def apply(self, image: Image.Image) -> Image.Image:
        self.analyze(image)
        img = image.copy()
        b = self._analysis.get("brightness", 128)
        c = self._analysis.get("contrast", 128)
        s = self._analysis.get("saturation", 64)
        ct = self._analysis.get("color_temp", 1.0)
        brightness_factor = 1.0
        if b < 90:
            brightness_factor = 1.0 + (90 - b) / 300
        elif b > 200:
            brightness_factor = 1.0 - (b - 200) / 400
        if brightness_factor != 1.0:
            img = ImageEnhance.Brightness(img).enhance(brightness_factor)
        if c < 60:
            img = ImageEnhance.Contrast(img).enhance(1.15)
        if s < 40:
            img = ImageEnhance.Color(img).enhance(1.1)
        if ct < 0.9 or ct > 1.1:
            img = self._balance_white(img)
        img = img.filter(ImageFilter.UnsharpMask(radius=0.5, percent=50, threshold=2))
        return img

    def _balance_white(self, image: Image.Image) -> Image.Image:
        stat = ImageStat.Stat(image)
        r, g, b = stat.mean
        avg = (r + g + b) / 3
        if r > 0 and g > 0 and b > 0:
            r_gain = avg / r
            g_gain = avg / g
            b_gain = avg / b
            bands = list(image.split())
            bands[0] = bands[0].point(lambda x: min(255, int(x * r_gain)))
            bands[1] = bands[1].point(lambda x: min(255, int(x * g_gain)))
            bands[2] = bands[2].point(lambda x: min(255, int(x * b_gain)))
            return Image.merge("RGB", bands)
        return image
