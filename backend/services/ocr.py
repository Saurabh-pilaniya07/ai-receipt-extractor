from pathlib import Path

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from streamlit import image


TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if TESSERACT_PATH.exists():
    pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from a receipt image using Tesseract OCR.
    """

    image = Image.open(file_path)

    # Convert to grayscale
    image = image.convert("L")

    # Increase resolution for better OCR
    width, height = image.size
    image = image.resize(
        (width * 2, height * 2)
    )

    # Improve contrast and sharpness
    image = ImageEnhance.Contrast(image).enhance(1.5)
    image = ImageEnhance.Sharpness(image).enhance(1.5)
    image = image.filter(ImageFilter.SHARPEN)

    text_primary = pytesseract.image_to_string(
        image,
        config="--psm 6"
    )

    text_secondary = pytesseract.image_to_string(
        image,
        config="--psm 11"
    )

    text_layout = pytesseract.image_to_string(
        image,
        config="--psm 3"
    )

    return (
        "PRIMARY OCR:\n"
        + text_primary.strip()
        + "\n\nSECONDARY OCR:\n"
        + text_secondary.strip()
        + "\n\nLAYOUT OCR:\n"
        + text_layout.strip()
    )