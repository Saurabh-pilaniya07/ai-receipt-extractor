from typing import Any

from backend.agents.base import ExpenseAgent
from backend.schemas.receipt import ReceiptExtraction


class OfficeExpenseAgent(ExpenseAgent):
    """Handles office supplies and business equipment."""

    name = "office"

    KEYWORDS = {
        "office",
        "stationery",
        "stationary",
        "notebook",
        "paper",
        "pen",
        "pencil",
        "printer",
        "ink",
        "toner",
        "keyboard",
        "mouse",
        "monitor",
        "laptop",
        "computer",
        "usb",
        "cable",
        "electronics",
        "equipment",
        "supplies",
    }

    def can_handle(
        self,
        receipt: ReceiptExtraction,
    ) -> bool:
        text = self._receipt_text(receipt)
        return any(
            keyword in text
            for keyword in self.KEYWORDS
        )

    def process(
        self,
        receipt: ReceiptExtraction,
    ) -> dict[str, Any]:
        return {
            "agent": self.name,
            "category": "Office",
            "merchant_name": receipt.merchant_name,
            "date": receipt.date,
            "total_amount": receipt.total_amount,
            "tax": receipt.tax,
            "tip": receipt.tip,
            "line_items": [
                item.model_dump()
                for item in receipt.line_items
            ],
        }

    @staticmethod
    def _receipt_text(
        receipt: ReceiptExtraction,
    ) -> str:
        values = [
            receipt.merchant_name or "",
            *[
                item.item_name
                for item in receipt.line_items
            ],
        ]

        return " ".join(values).lower()