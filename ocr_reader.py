# ocr_reader.py
import pytesseract
from PIL import Image, ImageOps, ImageFilter
import io
import numpy as np

class OCRReader:
    def __init__(self, config=None):
        self.config = config or {}
        cmd = ""
        if config:
            cmd = config.get("ocr", {}).get("tesseract_cmd", "")
        if cmd:
            pytesseract.pytesseract.tesseract_cmd = cmd

    def image_to_text(self, pil_image):
        # preprocess: grayscale, sharpen, threshold
        img = pil_image.convert("L")
        img = img.filter(ImageFilter.SHARPEN)
        # simple binarization
        img = ImageOps.autocontrast(img)
        txt = pytesseract.image_to_string(img, lang="por", config="--psm 6")
        return txt.strip()
