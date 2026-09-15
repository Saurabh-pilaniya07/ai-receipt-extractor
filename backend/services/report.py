from pathlib import Path
from typing import Any

from openpyxl import Workbook


def generate_expense_report(
    summary: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Generate an Excel expense report from the expense summary."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Expense Report"

    worksheet.append([
        "Date",
        "Merchant",
        "Category",
        "Total Amount",
        "Tax",
        "Tip",
    ])

    for expense in summary.get("expenses", []):
        worksheet.append([
            expense.get("date"),
            expense.get("merchant_name"),
            expense.get("category"),
            expense.get("total_amount"),
            expense.get("tax"),
            expense.get("tip"),
        ])

    worksheet.append([])
    worksheet.append(["Summary"])
    worksheet.append([
        "Receipt Count",
        summary.get("receipt_count", 0),
    ])
    worksheet.append([
        "Total Amount",
        summary.get("total_amount", 0),
    ])

    worksheet.append([])
    worksheet.append(["Category", "Category Total"])

    for category, amount in summary.get(
        "category_totals", {}
    ).items():
        worksheet.append([category, amount])

    workbook.save(output_path)

    return output_path