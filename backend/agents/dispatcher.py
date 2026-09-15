from typing import Any

from backend.agents.base import ExpenseAgent
from backend.agents.food_agent import FoodExpenseAgent
from backend.agents.office_agent import OfficeExpenseAgent
from backend.agents.travel_agent import TravelExpenseAgent
from backend.schemas.receipt import ReceiptExtraction


class ExpenseDispatcher:
    """
    Routes an extracted receipt to the most appropriate
    specialized expense agent.
    """

    def __init__(
        self,
        agents: list[ExpenseAgent] | None = None,
    ):
        self.agents = agents or [
            TravelExpenseAgent(),
            OfficeExpenseAgent(),
            FoodExpenseAgent(),
        ]

    def dispatch(
        self,
        receipt: ReceiptExtraction,
    ) -> dict[str, Any]:
        """
        Find a suitable agent and process the receipt.

        Raises:
            ValueError: If no specialized agent can handle
            the receipt.
        """

        for agent in self.agents:
            if agent.can_handle(receipt):
                return agent.process(receipt)

        raise ValueError(
            "No expense agent could handle this receipt."
        )