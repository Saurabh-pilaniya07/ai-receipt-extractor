from backend.agents.summary_agent import ExpenseSummaryAgent
from backend.models.database import SessionLocal
from backend.services.email import send_expense_report
from backend.services.expense_data import get_stored_expenses
from backend.services.recipients import load_recipients
from backend.services.report import generate_expense_report


def main():
    db = SessionLocal()

    try:
        expenses = get_stored_expenses(db)

        if not expenses:
            print("No stored receipts found.")
            return

        summary = ExpenseSummaryAgent().summarize(expenses)

        report_path = generate_expense_report(
            summary,
            "part2/expense_report.xlsx",
        )

        recipients = load_recipients()

        email_results = [
            send_expense_report(
                recipient,
                report_path,
                dry_run=True,
            )
            for recipient in recipients
        ]

        print("Expense workflow completed.")
        print(f"Receipts processed: {summary['receipt_count']}")
        print(f"Total amount: {summary['total_amount']}")
        print(f"Report: {report_path}")
        print(f"Email results: {email_results}")

    finally:
        db.close()


if __name__ == "__main__":
    main()