from PIL import Image


def get_exif(image: Image.Image) -> dict | None:
    return image.info.get("exif")


def copy_exif(source: Image.Image, target: Image.Image) -> Image.Image:
    exif = get_exif(source)
    if exif:
        target.info["exif"] = exif
    return target
