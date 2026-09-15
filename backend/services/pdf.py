import pymupdf
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO


def preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert("L")

    width, height = image.size
    image = image.resize((width * 2, height * 2))

    image = ImageEnhance.Contrast(image).enhance(1.5)
    image = ImageEnhance.Sharpness(image).enhance(1.5)
    image = image.filter(ImageFilter.SHARPEN)

    return image


def ocr_image(image: Image.Image) -> str:
    image = preprocess_image(image)

    primary = pytesseract.image_to_string(
        image,
        config="--psm 6",
    )

    secondary = pytesseract.image_to_string(
        image,
        config="--psm 11",
    )

    return (
        "PRIMARY OCR:\n"
        + primary.strip()
        + "\n\nSECONDARY OCR:\n"
        + secondary.strip()
    )


def extract_text_from_pdf(file_path: str) -> str:
    document = pymupdf.open(file_path)
    text_pages = []

    for page in document:
        # First try the PDF's native text layer.
        text = page.get_text().strip()

        if text:
            text_pages.append(text)
            continue

        # For scanned/image-only PDFs, OCR the embedded images directly.
        page_images = page.get_images(full=True)

        if page_images:
            image_texts = []

            for image_info in page_images:
                xref = image_info[0]
                extracted = document.extract_image(xref)

                image_bytes = extracted["image"]

                image = Image.open(
                    BytesIO(image_bytes)
                )

                ocr_text = ocr_image(image)

                if ocr_text.strip():
                    image_texts.append(ocr_text)

            if image_texts:
                text_pages.append("\n\n".join(image_texts))
                continue

        # Final fallback: render the complete page and OCR it.
        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(2, 2),
            alpha=False,
        )

        image = Image.frombytes(
            "RGB",
            [pixmap.width, pixmap.height],
            pixmap.samples,
        )

        ocr_text = ocr_image(image)

        if ocr_text.strip():
            text_pages.append(ocr_text)

    document.close()

    return "\n\n".join(text_pages).strip()