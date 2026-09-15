from typing import Any


class ExpenseSummaryAgent:
    """
    Creates a consolidated summary from processed expense records.
    """

    name = "summary"

    def summarize(
        self,
        expenses: list[dict[str, Any]],
    ) -> dict[str, Any]:
        total_amount = round(
            sum(
                expense.get("total_amount") or 0
                for expense in expenses
            ),
            2,
        )

        category_totals: dict[str, float] = {}

        for expense in expenses:
            category = expense.get("category", "Other")
            amount = expense.get("total_amount") or 0

            category_totals[category] = round(
                category_totals.get(category, 0) + amount,
                2,
            )

        return {
            "agent": self.name,
            "receipt_count": len(expenses),
            "total_amount": total_amount,
            "category_totals": category_totals,
            "expenses": expenses,
        }