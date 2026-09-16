import json
import shutil
import tempfile
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.agents.dispatcher import ExpenseDispatcher
from backend.agents.summary_agent import ExpenseSummaryAgent
from backend.models.database import get_db
from backend.models.receipt import Receipt
from backend.services.email import send_expense_report
from backend.services.expense_data import get_stored_expenses
from backend.services.extraction import extract_receipt
from backend.services.recipients import load_recipients
from backend.services.report import generate_expense_report

from pydantic import BaseModel

router = APIRouter()

class ExpenseReportRequest(BaseModel):
    recipient_email: str

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}


@router.post("/upload")
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Allowed: PNG, JPG, JPEG, PDF."
            ),
        )

    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name

        # Run extraction pipeline
        extracted = extract_receipt(temp_path)

        # Part 2: classify the expense
        dispatcher = ExpenseDispatcher()
        expense = dispatcher.dispatch(extracted)

        # Save to database
        receipt = Receipt(
            filename=file.filename,
            merchant_name=extracted.merchant_name,
            date=extracted.date,
            total_amount=extracted.total_amount,
            category=expense["category"],
            extracted_json=json.dumps(
                extracted.model_dump()
            ),
        )

        db.add(receipt)
        db.commit()
        db.refresh(receipt)

        return {
            "id": receipt.id,
            "filename": receipt.filename,
            "merchant_name": receipt.merchant_name,
            "date": receipt.date,
            "total_amount": receipt.total_amount,
            "category": expense["category"],
            "line_items": [
                item.model_dump()
                for item in extracted.line_items
            ],
            "tax": extracted.tax,
            "tip": extracted.tip,
        }

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=(
                "Receipt processing failed. "
                "Please check the uploaded file and try again."
            ),
        )

    finally:
        # Remove temporary file
        if "temp_path" in locals():
            Path(temp_path).unlink(
                missing_ok=True
            )


@router.get("/receipts")
def get_receipts(
    db: Session = Depends(get_db),
):
    receipts = (
        db.query(Receipt)
        .order_by(Receipt.created_at.desc())
        .all()
    )

    return [
        {
            "id": receipt.id,
            "filename": receipt.filename,
            "merchant_name": receipt.merchant_name,
            "date": receipt.date,
            "category": receipt.category,
            "total_amount": receipt.total_amount,
            "extracted_json": json.loads(
                receipt.extracted_json
            ),
            "created_at": receipt.created_at,
        }
        for receipt in receipts
    ]


@router.post("/expense-report")
def create_expense_report(
    db: Session = Depends(get_db),
):
    try:
        expenses = get_stored_expenses(db)

        if not expenses:
            raise HTTPException(
                status_code=404,
                detail="No stored receipts found.",
            )

        summary = ExpenseSummaryAgent().summarize(expenses)

        report_path = generate_expense_report(
            summary,
            "part2/expense_report.xlsx",
        )

        return {
            "message": "Expense report generated successfully.",
            "receipt_count": summary["receipt_count"],
            "total_amount": summary["total_amount"],
            "category_totals": summary["category_totals"],
            "report": str(report_path),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate expense report: {exc}",
        )

@router.post("/expense-report/send-email")
def send_report_email(
    request: ExpenseReportRequest,
):
    try:
        recipient_email = request.recipient_email.strip()

        if not recipient_email or "@" not in recipient_email:
            raise HTTPException(
                status_code=400,
                detail="A valid recipient email is required.",
            )

        report_path = Path("part2/expense_report.xlsx")

        if not report_path.exists():
            raise HTTPException(
                status_code=404,
                detail=(
                    "Expense report has not been generated yet. "
                    "Generate the report first."
                ),
            )

        recipient = {
            "name": recipient_email,
            "email": recipient_email,
        }

        email_result = send_expense_report(
            recipient,
            report_path,
            dry_run=False,
        )

        return {
            "message": "Expense report sent successfully.",
            "recipient_email": recipient_email,
            "email_result": email_result,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Could not send expense report: {exc}",
        )

    
@router.get("/expense-report/download")
def download_expense_report():
    report_path = Path("part2/expense_report.xlsx")

    if not report_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Expense report has not been generated yet.",
        )

    return FileResponse(
        path=report_path,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        filename="expense_report.xlsx",
    )