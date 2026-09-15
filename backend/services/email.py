import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_expense_report(
    recipient: dict[str, str],
    report_path: str | Path,
    dry_run: bool = True,
) -> dict[str, str | bool]:
    """
    Send an expense report by SMTP.

    Dry-run mode returns the intended action without sending email.
    """

    report_path = Path(report_path)

    if not report_path.exists():
        raise FileNotFoundError(
            f"Report file not found: {report_path}"
        )

    sender = os.getenv("SMTP_SENDER", "")
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    recipient_email = recipient["email"]
    recipient_name = recipient["name"]

    if dry_run:
        return {
            "sent": False,
            "dry_run": True,
            "recipient": recipient_email,
            "message": (
                f"Expense report prepared for {recipient_name} "
                f"({recipient_email})."
            ),
        }

    if not all([
        sender,
        smtp_host,
        smtp_username,
        smtp_password,
    ]):
        raise ValueError(
            "SMTP configuration is incomplete."
        )

    message = EmailMessage()
    message["Subject"] = "Expense Report"
    message["From"] = sender
    message["To"] = recipient_email
    message.set_content(
        "Please find the attached expense report."
    )

    with report_path.open("rb") as attachment:
        message.add_attachment(
            attachment.read(),
            maintype="application",
            subtype=(
                "vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
            filename=report_path.name,
        )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)

    return {
        "sent": True,
        "dry_run": False,
        "recipient": recipient_email,
        "message": f"Expense report sent to {recipient_name}.",
    }