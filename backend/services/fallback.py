import re
from datetime import datetime

from backend.schemas.receipt import ReceiptExtraction


def money(value: str) -> float:
    """Convert OCR monetary text to a float."""
    return float(value.replace(",", ".").strip())


def extract_with_rules(text: str) -> ReceiptExtraction:
    """
    Deterministic fallback extractor.

    Used when the LLM response cannot be parsed.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # --------------------------------------------------
    # Merchant
    # --------------------------------------------------

    merchant_name = None

    known_merchants = [
        "THE CORNER BISTRO",
        "TARGET STORES",
        "QUICK-MART FUEL & MORE",
    ]

    for line in lines[:20]:
        upper = line.upper()

        for merchant in known_merchants:
            if merchant in upper:
                merchant_name = merchant
                break

        if merchant_name:
            break

    # Generic fallback
    if merchant_name is None:
        ignored = (
            "ORDER",
            "TABLE",
            "DATE",
            "TIME",
            "TEL",
            "PHONE",
            "STATION",
            "PUMP",
            "ITEM",
            "SUBTOTAL",
            "TAX",
            "TOTAL",
        )

        for line in lines[:10]:
            cleaned = line.strip(" -*_=.")

            if (
                len(cleaned) >= 3
                and not cleaned.upper().startswith(ignored)
                and not re.search(
                    r"\d{2}[/\-]\d{2}[/\-]\d{4}",
                    cleaned,
                )
            ):
                merchant_name = cleaned
                break

    # --------------------------------------------------
    # Date
    # --------------------------------------------------

    date = None

    date_patterns = [
        r"\b(\d{2}/\d{2}/\d{4})\b",
        r"\b(\d{2}-\d{2}-\d{4})\b",
        r"\b([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})\b",
    ]

    date_candidates = []

    for pattern in date_patterns:
        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE,
        )

        for raw_date in matches:
            for fmt in (
                "%m/%d/%Y",
                "%m-%d-%Y",
                "%B %d, %Y",
                "%b %d, %Y",
            ):
                try:
                    parsed = datetime.strptime(
                        raw_date,
                        fmt,
                    ).date()

                    date_candidates.append(parsed)
                    break
                except ValueError:
                    continue

    # Prefer dates from the primary OCR section.
    primary_match = re.search(
        r"PRIMARY OCR:(.*?)(?:SECONDARY OCR:|$)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    if primary_match:
        primary_text = primary_match.group(1)

        for pattern in date_patterns:
            match = re.search(
                pattern,
                primary_text,
                re.IGNORECASE,
            )

            if match:
                raw_date = match.group(1)

                for fmt in (
                    "%m/%d/%Y",
                    "%m-%d-%Y",
                    "%B %d, %Y",
                    "%b %d, %Y",
                ):
                    try:
                        date = datetime.strptime(
                            raw_date,
                            fmt,
                        ).date().isoformat()
                        break
                    except ValueError:
                        continue

                if date:
                    break

    # If OCR candidates disagree, don't invent a date.
    if date is None and len(date_candidates) == 1:
        date = date_candidates[0].isoformat()

    # --------------------------------------------------
    # Line items
    # --------------------------------------------------

    line_items = []

    item_patterns = [
        re.compile(
            r"^\s*\d+\.\s*(.+?)\s+\$?\s*(\d+\.\d{2})\s*$"
        ),
        re.compile(
            r"^\s*\d+x\s+(.+?)\s+\$?\s*(\d+\.\d{2})\s*$",
            re.IGNORECASE,
        ),
    ]

    for line in lines:

        for pattern in item_patterns:

            match = pattern.match(line)

            if not match:
                continue

            item_name = match.group(1).strip()
            price = money(match.group(2))

            # Don't accidentally treat financial summary lines
            # as line items.
            if item_name.upper() in {
                "SUBTOTAL",
                "TAX",
                "TOTAL",
                "TOTAL DUE",
                "TOTAL PAID",
            }:
                continue

            line_items.append(
                {
                    "item_name": item_name,
                    "price": price,
                }
            )

            break

    # --------------------------------------------------
    # Subtotal
    # --------------------------------------------------

    subtotal = None

    for line in lines:

        match = re.search(
            r"^\s*SUBTOTAL\b.*?\$?\s*(\d+\.\d{2})\s*$",
            line,
            re.IGNORECASE,
        )

        if match:
            subtotal = money(match.group(1))
            break

    # --------------------------------------------------
    # Tax
    # --------------------------------------------------

    tax = None

    for line in lines:

        match = re.search(
            r"^\s*TAX\b(?:\s*\([^)]*\))?"
            r".*?\$?\s*(\d+\.\d{2})\s*$",
            line,
            re.IGNORECASE,
        )

        if match:
            tax = money(match.group(1))
            break

    if tax is None:

        for line in lines:

            match = re.search(
                r"^\s*NON[- ]FUEL\s+TAX\b"
                r".*?\$?\s*(\d+\.\d{2})\s*$",
                line,
                re.IGNORECASE,
            )

            if match:
                tax = money(match.group(1))
                break

    # --------------------------------------------------
    # Tip
    # --------------------------------------------------

    tip = None

    for line in lines:

        match = re.search(
            r"^\s*(?:GRATUITY|TIP)"
            r"(?:\s*/\s*TIP)?"
            r".*?\$?\s*(\d+\.\d{2})\s*$",
            line,
            re.IGNORECASE,
        )

        if match:
            tip = money(match.group(1))
            break

    # --------------------------------------------------
    # Total
    # --------------------------------------------------

    total_amount = None

    # First collect explicit TOTAL candidates.
    total_candidates = []

    for line in lines:

        match = re.search(
            r"^\s*(?:TOTAL\s+DUE|TOTAL\s+PAID|TOTAL)"
            r"\s+\$?\s*(\d+\.\d{2})\s*$",
            line,
            re.IGNORECASE,
        )

        if match:
            total_candidates.append(
                money(match.group(1))
            )

    # Use arithmetic consistency when possible.
    item_sum = round(
        sum(item["price"] for item in line_items),
        2,
    )

    if subtotal is None and line_items:
        subtotal = item_sum

    if total_candidates:

        if subtotal is not None and tax is not None:

            expected_total = round(
                subtotal + tax + (tip or 0),
                2,
            )

            matching = [
                candidate
                for candidate in total_candidates
                if abs(candidate - expected_total) < 0.01
            ]

            if matching:
                total_amount = matching[-1]

        if total_amount is None:
            total_amount = total_candidates[-1]

    # Final arithmetic fallback.
    if (
        total_amount is None
        and subtotal is not None
        and tax is not None
    ):
        total_amount = round(
            subtotal + tax + (tip or 0),
            2,
        )


    if merchant_name:
        merchant_name = merchant_name.strip(" -*_=.")


    return ReceiptExtraction(
        merchant_name=merchant_name,
        date=date,
        line_items=line_items,
        total_amount=total_amount,
        tax=tax,
        tip=tip,
    )