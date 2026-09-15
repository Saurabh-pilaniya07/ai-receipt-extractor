from abc import ABC, abstractmethod
from typing import Any

from backend.schemas.receipt import ReceiptExtraction


class ExpenseAgent(ABC):
    """
    Base interface for specialized expense agents.

    Each agent determines whether it can handle a receipt
    and processes the receipt when selected.
    """

    name: str = "base"

    @abstractmethod
    def can_handle(
        self,
        receipt: ReceiptExtraction,
    ) -> bool:
        """
        Return True when this agent can handle the receipt.
        """
        raise NotImplementedError

    @abstractmethod
    def process(
        self,
        receipt: ReceiptExtraction,
    ) -> dict[str, Any]:
        """
        Process the receipt and return structured agent output.
        """
        raise NotImplementedError