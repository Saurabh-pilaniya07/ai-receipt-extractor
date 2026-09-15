from pathlib import Path
from backend.agents.dispatcher import ExpenseDispatcher
from backend.schemas.receipt import LineItem, ReceiptExtraction


def test_target_routes_to_office_agent():
    receipt = ReceiptExtraction(
        merchant_name="TARGET STORES",
        date="2026-02-18",
        line_items=[
            LineItem(
                item_name="Wireless Mouse",
                price=24.99,
            ),
            LineItem(
                item_name="USB-C Cable 6ft",
                price=12.50,
            ),
            LineItem(
                item_name="Notebook 3-Pack",
                price=8.99,
            ),
        ],
        total_amount=50.31,
        tax=3.83,
        tip=None,
    )

    dispatcher = ExpenseDispatcher()
    result = dispatcher.dispatch(receipt)

    assert result["agent"] == "office"
    assert result["category"] == "Office"
    assert result["total_amount"] == 50.31


def test_quick_mart_routes_to_travel_agent():
    receipt = ReceiptExtraction(
        merchant_name="QUICK-MART FUEL & MORE",
        date="2026-02-25",
        line_items=[
            LineItem(
                item_name="Regular Unleaded Fuel",
                price=40.30,
            ),
            LineItem(
                item_name="Monster Energy Drink",
                price=3.49,
            ),
        ],
        total_amount=44.07,
        tax=0.28,
        tip=None,
    )

    dispatcher = ExpenseDispatcher()
    result = dispatcher.dispatch(receipt)

    assert result["agent"] == "travel"
    assert result["category"] == "Travel"
    assert result["total_amount"] == 44.07


def test_corner_bistro_routes_to_food_agent():
    receipt = ReceiptExtraction(
        merchant_name="THE CORNER BISTRO",
        date="2026-02-20",
        line_items=[
            LineItem(
                item_name="Sparkling Water",
                price=4.00,
            ),
            LineItem(
                item_name="Caesar Salad",
                price=22.00,
            ),
            LineItem(
                item_name="Grilled Salmon",
                price=48.00,
            ),
            LineItem(
                item_name="Espresso",
                price=3.50,
            ),
        ],
        total_amount=99.48,
        tax=6.98,
        tip=15.00,
    )

    dispatcher = ExpenseDispatcher()
    result = dispatcher.dispatch(receipt)

    assert result["agent"] == "food"
    assert result["category"] == "Food"
    assert result["total_amount"] == 99.48


def test_unknown_expense_raises_error():
    receipt = ReceiptExtraction(
        merchant_name="UNKNOWN STORE",
        date="2026-02-26",
        line_items=[
            LineItem(
                item_name="Something Unclassified",
                price=25.00,
            ),
        ],
        total_amount=25.00,
        tax=None,
        tip=None,
    )

    dispatcher = ExpenseDispatcher()

    try:
        dispatcher.dispatch(receipt)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "No expense agent could handle" in str(exc)

from backend.agents.summary_agent import ExpenseSummaryAgent


def test_summary_agent():
    expenses = [
        {
            "agent": "food",
            "category": "Food",
            "merchant_name": "Corner Bistro",
            "date": "2025-01-15",
            "total_amount": 24.50,
        },
        {
            "agent": "travel",
            "category": "Travel",
            "merchant_name": "Quick-Mart",
            "date": "2025-01-16",
            "total_amount": 40.58,
        },
        {
            "agent": "office",
            "category": "Office",
            "merchant_name": "Office Store",
            "date": "2025-01-17",
            "total_amount": 15.00,
        },
    ]

    summary = ExpenseSummaryAgent().summarize(expenses)

    assert summary["receipt_count"] == 3
    assert summary["total_amount"] == 80.08
    assert summary["category_totals"]["Food"] == 24.50
    assert summary["category_totals"]["Travel"] == 40.58
    assert summary["category_totals"]["Office"] == 15.00


from pathlib import Path

from backend.services.email import send_expense_report
from backend.services.recipients import load_recipients
from backend.services.report import generate_expense_report


def test_load_recipients(tmp_path):
    from openpyxl import Workbook

    recipient_file = tmp_path / "recipients.xlsx"

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Recipients"
    worksheet.append(["name", "email"])
    worksheet.append(["Test Finance", "test@example.com"])
    workbook.save(recipient_file)

    recipients = load_recipients(recipient_file)

    assert recipients == [
        {
            "name": "Test Finance",
            "email": "test@example.com",
        }
    ]


def test_generate_expense_report(tmp_path):
    summary = {
        "receipt_count": 2,
        "total_amount": 65.08,
        "category_totals": {
            "Food": 24.50,
            "Travel": 40.58,
        },
        "expenses": [
            {
                "date": "2025-01-15",
                "merchant_name": "Corner Bistro",
                "category": "Food",
                "total_amount": 24.50,
                "tax": 2.00,
                "tip": 3.00,
            },
            {
                "date": "2025-01-16",
                "merchant_name": "Quick-Mart",
                "category": "Travel",
                "total_amount": 40.58,
                "tax": 0.28,
                "tip": None,
            },
        ],
    }

    report_path = tmp_path / "expense_report.xlsx"

    result = generate_expense_report(
        summary,
        report_path,
    )

    assert result == Path(report_path)
    assert report_path.exists()
    assert report_path.stat().st_size > 0


def test_email_dry_run(tmp_path):
    report_path = tmp_path / "expense_report.xlsx"
    report_path.write_bytes(b"test report")

    result = send_expense_report(
        {
            "name": "Finance Team",
            "email": "finance@example.com",
        },
        report_path,
        dry_run=True,
    )

    assert result["sent"] is False
    assert result["dry_run"] is True
    assert result["recipient"] == "finance@example.com"

from backend.models.database import SessionLocal
from backend.models.receipt import Receipt
from backend.services.expense_data import get_stored_expenses


def test_get_stored_expenses():
    db = SessionLocal()

    try:
        receipt = Receipt(
            filename="test_expense_data.jpg",
            merchant_name="Test Cafe",
            date="2026-09-15",
            total_amount=12.50,
            category="Food",
            extracted_json='{"tax": 1.00, "tip": 1.50, "line_items": []}',
        )

        db.add(receipt)
        db.commit()

        expenses = get_stored_expenses(db)

        matching = [
            expense
            for expense in expenses
            if expense["merchant_name"] == "Test Cafe"
        ]

        assert len(matching) == 1
        assert matching[0]["category"] == "Food"
        assert matching[0]["total_amount"] == 12.50
        assert matching[0]["tax"] == 1.00
        assert matching[0]["tip"] == 1.50

    finally:
        db.query(Receipt).filter(
            Receipt.filename == "test_expense_data.jpg"
        ).delete()
        db.commit()
        db.close()