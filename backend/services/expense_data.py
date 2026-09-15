import json
from typing import Any

from sqlalchemy.orm import Session

from backend.models.receipt import Receipt


def get_stored_expenses(
    db: Session,
) -> list[dict[str, Any]]:
    """Convert stored receipts into expense records for Part 2."""

    receipts = (
        db.query(Receipt)
        .order_by(Receipt.created_at.asc())
        .all()
    )

    expenses = []

    for receipt in receipts:
        extracted = json.loads(receipt.extracted_json)

        expenses.append({
            "agent": (
                receipt.category.lower()
                if receipt.category
                else "other"
            ),
            "category": receipt.category or "Other",
            "merchant_name": receipt.merchant_name,
            "date": receipt.date,
            "total_amount": receipt.total_amount,
            "tax": extracted.get("tax"),
            "tip": extracted.get("tip"),
            "line_items": extracted.get("line_items", []),
        })

    return expenses