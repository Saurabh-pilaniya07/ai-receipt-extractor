from pathlib import Path
import re

from backend.services.llm import extract_receipt_data
from backend.services.ocr import extract_text_from_image
from backend.services.pdf import extract_text_from_pdf
from backend.services.fallback import extract_with_rules


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
PDF_EXTENSIONS = {".pdf"}


def extract_receipt(file_path: str):
    """
    Process a receipt file and return validated structured data.

    The AI extractor is the primary extraction layer.
    Deterministic rules are used as a secondary
    validation/enrichment layer.
    """

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension in IMAGE_EXTENSIONS:
        text = extract_text_from_image(str(path))

    elif extension in PDF_EXTENSIONS:
        text = extract_text_from_pdf(str(path))

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if not text.strip():
        raise ValueError(
            "Could not extract any text from the receipt."
        )

    ai_result = extract_receipt_data(text)

    # --------------------------------------------------
    # Deterministic enrichment
    # --------------------------------------------------

    try:
        fallback_result = extract_with_rules(text)

        if not ai_result.merchant_name:
            ai_result.merchant_name = fallback_result.merchant_name

        if not ai_result.date:
            ai_result.date = fallback_result.date

        if not ai_result.line_items:
            ai_result.line_items = fallback_result.line_items

        if ai_result.total_amount is None:
            ai_result.total_amount = fallback_result.total_amount

        if ai_result.tax is None:
            ai_result.tax = fallback_result.tax

        if ai_result.tip is None:
            ai_result.tip = fallback_result.tip

    except Exception:
        # Keep the AI result if deterministic enrichment fails.
        pass

    # --------------------------------------------------
    # Financial reconciliation
    # --------------------------------------------------

    # If OCR clearly identifies a tax field but loses the
    # numeric tax amount, infer tax from total - line items.
    #
    # This is intentionally done AFTER AI extraction because
    # the AI may have recovered line items that deterministic
    # OCR parsing could not.
    if (
        ai_result.tax is None
        and ai_result.tip is None
        and ai_result.total_amount is not None
        and ai_result.line_items
        and re.search(
            r"\b(?:TAX|NON[- ]FUEL\s+TAX|SALES\s+TAX)\b",
            text,
            re.IGNORECASE,
        )
    ):
        items_total = round(
            sum(item.price for item in ai_result.line_items),
            2,
        )

        inferred_tax = round(
            ai_result.total_amount - items_total,
            2,
        )

        if inferred_tax > 0:
            ai_result.tax = inferred_tax

    return ai_result