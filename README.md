# Receipt Extractor

An end-to-end AI-powered receipt extraction and expense management application.

The application accepts PNG, JPG, JPEG, and PDF receipts, extracts structured
expense information using OCR and AI, classifies expenses using lightweight
specialized agents, stores the results in SQLite, generates expense reports,
and provides a Streamlit web interface for processing receipts and sending
expense reports by email.

---

## Features

### Part 1 — Receipt Extraction

- Receipt upload through REST API
- PNG, JPG, JPEG, and PDF support
- OCR using Tesseract
- PDF text extraction using PyMuPDF
- Support for scanned/image-based PDFs
- AI-powered structured receipt extraction
- Deterministic fallback extraction
- Receipt field validation and enrichment
- Merchant extraction
- Date extraction
- Line item extraction
- Total amount extraction
- Tax extraction
- Tip extraction
- SQLite persistence using SQLAlchemy
- FastAPI backend
- Streamlit frontend
- Previously processed receipt history

### Part 2 — Multi-Agent Expense Workflow

- Lightweight custom Python agents
- Expense dispatcher
- Food expense agent
- Travel expense agent
- Office expense agent
- Expense summary agent
- Category-based expense aggregation
- Excel expense report generation
- Recipient configuration through Excel
- SMTP email delivery
- Dry-run email mode for CLI workflow
- Real email delivery from the Streamlit UI
- Excel report download from the UI

---

## Architecture

```text
                         Receipt File
                              |
                              v
                    +-------------------+
                    |  File Processing  |
                    +-------------------+
                              |
                    +---------+---------+
                    |                   |
                 Image                 PDF
                    |                   |
                    v                   v
               Tesseract             PyMuPDF
                    |                   |
                    +---------+---------+
                              |
                              v
                         OCR / Text
                              |
                              v
                    AI Extraction Layer
                              |
                              v
                  Deterministic Fallback
                              |
                              v
                    Structured Receipt
                              |
                              v
                    Expense Dispatcher
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
           Food Agent     Travel Agent    Office Agent
              |               |               |
              +---------------+---------------+
                              |
                              v
                           SQLite
                              |
                              v
                     Expense Summary Agent
                              |
                    +---------+---------+
                    |                   |
                    v                   v
              Excel Report        Email Service
                    |                   |
                    |                   v
                    |              SMTP Server
                    |                   |
                    v                   v
             Download from UI     Recipient Email
````

---

## End-to-End Application Flow

The Streamlit application connects both assessment parts into one workflow.

```text
Streamlit UI
     |
     +---- Upload Receipt
     |          |
     |          v
     |      POST /upload
     |          |
     |          v
     |     OCR + AI Extraction
     |          |
     |          v
     |    Expense Dispatcher
     |          |
     |     +----+----+
     |     |         |
     |   Food      Travel      Office
     |     |         |           |
     |     +---------+-----------+
     |               |
     |               v
     |             SQLite
     |
     +---- Generate & Send Expense Report
                |
                v
        POST /expense-report
                |
                v
        Read stored expenses
                |
                v
        Expense Summary Agent
                |
        +-------+-------+
        |               |
        v               v
   Excel Report      SMTP Email
        |               |
        v               v
   Download UI      Recipient
```

This allows a receipt uploaded through Part 1 to become part of the Part 2
expense workflow without manually copying or entering the expense data.

---

## Project Structure

```text
Receipt Extractor/
│
├── backend/
│   ├── __init__.py
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── food_agent.py
│   │   ├── travel_agent.py
│   │   ├── office_agent.py
│   │   ├── dispatcher.py
│   │   └── summary_agent.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── receipt.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── receipt.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr.py
│   │   ├── pdf.py
│   │   ├── llm.py
│   │   ├── extraction.py
│   │   ├── fallback.py
│   │   ├── expense_data.py
│   │   ├── recipients.py
│   │   ├── report.py
│   │   └── email.py
│   │
│   └── main.py
│
├── frontend/
│   └── app.py
│
├── part2/
│   ├── recipients.xlsx
│   ├── run_expense_workflow.py
│   └── expense_report.xlsx
│
├── sample_receipts/
│
├── tests/
│   ├── test_api.py
│   ├── test_fallback.py
│   └── test_agents.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

# Setup

## 1. Create and activate the virtual environment

From the project root:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

---

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 3. Install Tesseract OCR

Install Tesseract OCR on the local machine.

The application supports the standard Windows installation path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

The OCR service automatically uses this path when the executable exists.

---

## 4. Configure environment variables

Create a `.env` file in the project root.

Example:

```env
OPENROUTER_API_KEY=your_openrouter_api_key

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_SENDER=your_email@example.com
```

For Gmail SMTP, an App Password should be used instead of the normal Google
Account password when App Password authentication is available.

Example:

```env
SMTP_SENDER=yourgmail@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=yourgmail@gmail.com
SMTP_PASSWORD=your_16_character_app_password
```

Never commit `.env` or API credentials to Git.

---

# Running the Backend

From the project root:

```powershell
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Health Check

```text
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

---

# API Endpoints

## Upload Receipt

```text
POST /upload
```

Accepts:

* PNG
* JPG
* JPEG
* PDF

Example:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/upload" `
  -F "file=@sample_receipts/test_receipt.jpg"
```

Example response:

```json
{
  "id": 1,
  "filename": "test_receipt.jpg",
  "merchant_name": "THE CORNER BISTRO",
  "date": "2026-02-20",
  "total_amount": 99.48,
  "category": "Food",
  "line_items": [
    {
      "item_name": "Sparkling Water",
      "price": 4.0
    },
    {
      "item_name": "Caesar Salad",
      "price": 22.0
    }
  ],
  "tax": 6.98,
  "tip": 15.0
}
```

The uploaded receipt is:

1. Processed through OCR/text extraction.
2. Passed to the AI extraction layer.
3. Enriched or validated using deterministic rules.
4. Classified by the expense dispatcher.
5. Stored in SQLite.

---

## Get Stored Receipts

```text
GET /receipts
```

Returns previously processed receipts stored in SQLite.

The response includes:

* Receipt ID
* Filename
* Merchant
* Date
* Category
* Total
* Extracted JSON
* Creation timestamp

---

## Generate Expense Report

```text
POST /expense-report
```

This endpoint connects Part 1 and Part 2.

It:

1. Reads stored receipts from SQLite.
2. Builds structured expense objects.
3. Runs the Expense Summary Agent.
4. Calculates receipt count and totals.
5. Generates the Excel expense report.
6. Sends the report to the recipient email supplied by the UI.

Request body:

```json
{
  "recipient_email": "recipient@example.com"
}
```

Example response:

```json
{
  "message": "Expense report generated and sent successfully.",
  "receipt_count": 1,
  "total_amount": 99.48,
  "category_totals": {
    "Food": 99.48
  },
  "recipient_email": "recipient@example.com",
  "report": "part2/expense_report.xlsx",
  "email_result": {
    "sent": true
  }
}
```

Real SMTP delivery requires valid SMTP configuration in `.env`.

---

## Download Expense Report

```text
GET /expense-report/download
```

Downloads the most recently generated Excel expense report.

The file is returned as:

```text
expense_report.xlsx
```

---

# Running the Frontend

In a second terminal:

```powershell
streamlit run frontend/app.py
```

The Streamlit interface provides:

* Receipt upload
* Receipt processing
* Merchant information
* Receipt date
* Total amount
* Expense category
* Line items
* Tax
* Tip
* Raw structured JSON
* Previously extracted receipts
* Expense report generation
* Category totals
* Email delivery status
* Excel report download

---

# Using the Streamlit Application

## Step 1 — Upload a Receipt

Use the upload area to select:

```text
PNG / JPG / JPEG / PDF
```

Click:

```text
Process Receipt
```

The receipt is sent to the FastAPI backend.

---

## Step 2 — Review Extracted Information

The UI displays:

* Merchant
* Date
* Total
* Line items
* Tax
* Tip
* Expense category

The raw structured extraction can also be inspected through the JSON
expander.

---

## Step 3 — Generate and Send Expense Report

Scroll to:

```text
Expense Report
```

Enter a recipient email address.

Example:

```text
finance@example.com
```

Click:

```text
Generate & Send Expense Report
```

The backend reads all stored receipts and runs the Part 2 workflow.

The UI displays:

* Number of receipts processed
* Total expenses
* Category totals
* Email delivery status

The generated Excel file can also be downloaded directly from the UI.

---

# Part 2 — Multi-Agent Expense Workflow

Part 2 demonstrates a lightweight custom multi-agent architecture using
Python classes rather than a large agent framework.

The architecture is:

```text
Structured Receipt
       |
       v
Expense Dispatcher
       |
   +---+---+
   |   |   |
   v   v   v
 Food Travel Office
   |   |   |
   +---+---+
       |
       v
Expense Summary Agent
       |
       v
Excel Report
       |
       v
Email Service
```

---

## Agents

### Food Expense Agent

Handles food and dining-related expenses.

Examples include:

* Restaurants
* Cafes
* Coffee shops
* Grocery stores
* Bakeries
* Pizza
* Burgers
* Meals
* Beverages

---

### Travel Expense Agent

Handles travel and transportation-related expenses.

Examples include:

* Fuel
* Gas stations
* Petrol
* Diesel
* Taxi
* Transportation
* Flights
* Airlines
* Hotels
* Parking
* Tolls

---

### Office Expense Agent

Handles office supplies and equipment.

Examples include:

* Stationery
* Paper
* Pens
* Notebooks
* Printers
* Ink
* Toner
* Keyboards
* Mice
* Monitors
* Laptops
* Computers
* Cables
* Office equipment

---

### Expense Dispatcher

The dispatcher determines which specialized agent should process an extracted
receipt.

The current implementation uses deterministic keyword-based routing.

Travel is checked before Food so that receipts such as fuel purchases that also
contain product names like "Energy Drink" are routed correctly.

---

### Expense Summary Agent

The Summary Agent aggregates processed expenses and calculates:

* Receipt count
* Overall expense total
* Category totals
* Complete expense list

Example:

```json
{
  "receipt_count": 1,
  "total_amount": 99.48,
  "category_totals": {
    "Food": 99.48
  }
}
```

---

# Running Part 2 from the Command Line

From the project root:

```powershell
python -m part2.run_expense_workflow
```

The CLI workflow:

1. Reads stored receipts from SQLite.
2. Builds structured expense data.
3. Runs the Expense Summary Agent.
4. Generates the Excel expense report.
5. Loads recipients from `part2/recipients.xlsx`.
6. Prepares email delivery.
7. Uses dry-run mode by default.

Example output:

```text
Expense workflow completed.
Receipts processed: 1
Total amount: 99.48
Report: part2\expense_report.xlsx
Email results: [...]
```

---

# Recipient Configuration

Recipients are configured in:

```text
part2/recipients.xlsx
```

The workbook contains:

```text
name,email
Finance Team,finance@example.com
```

Additional recipients can be added as rows.

Example:

```text
name,email
Finance Team,finance@example.com
Accounting Team,accounting@example.com
```

---

# Email Delivery

The email service supports SMTP-based delivery.

Required environment variables:

```env
SMTP_SENDER=your_email@example.com
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
```

The generated Excel report is attached to the outgoing email.

---

## CLI Email Safety

The command-line Part 2 workflow uses dry-run mode by default:

```python
send_expense_report(
    recipient,
    report_path,
    dry_run=True,
)
```

Therefore:

```powershell
python -m part2.run_expense_workflow
```

does not send real emails.

It prepares and validates the email operation without contacting the
recipient.

---

## UI Email Delivery

The Streamlit UI provides a recipient email input.

The UI calls:

```text
POST /expense-report
```

with:

```json
{
  "recipient_email": "recipient@example.com"
}
```

The backend then performs SMTP delivery with:

```python
send_expense_report(
    recipient,
    report_path,
    dry_run=False,
)
```

SMTP credentials remain on the backend and are loaded from `.env`.

The recipient email is supplied by the user through the UI.

---

# Data Model

Each extracted receipt follows this structure:

```json
{
  "merchant_name": "Example Merchant",
  "date": "2026-01-15",
  "line_items": [
    {
      "item_name": "Example Item",
      "price": 10.99
    }
  ],
  "total_amount": 12.09,
  "tax": 1.10,
  "tip": null
}
```

The SQLite database stores:

* Receipt ID
* Original filename
* Merchant name
* Date
* Total amount
* Expense category
* Complete extracted JSON
* Creation timestamp

---

# Extraction Pipeline

The extraction pipeline is designed to handle both normal and noisy receipts.

```text
Input File
    |
    +---- Image
    |       |
    |       v
    |    Tesseract OCR
    |
    +---- PDF
            |
            v
         PyMuPDF
            |
            v
       Extracted Text
            |
            v
        AI Extraction
            |
            v
   Deterministic Fallback
            |
            v
    Structured Receipt
```

For images, OCR preprocessing includes:

* Grayscale conversion
* Image resizing
* Contrast enhancement
* Sharpness enhancement
* Multiple Tesseract page segmentation modes

For PDFs:

* Native PDF text is extracted when available.
* Image-only/scanned PDFs are rendered and passed through OCR.

---

# AI Extraction

The application uses OpenRouter for the AI extraction layer.

The model is configured through:

```text
OPENROUTER_API_KEY
```

The AI is instructed to return structured receipt data containing:

```text
merchant_name
date
line_items
total_amount
tax
tip
```

The implementation also handles malformed or fenced JSON responses.

If AI extraction is incomplete or unavailable, deterministic extraction rules
provide fallback values.

---

# Deterministic Fallback

The fallback extraction layer provides additional robustness for common OCR
and receipt formatting problems.

It can identify:

* Known merchants
* Merchant names
* Dates
* Line items
* Subtotals
* Taxes
* Tips
* Total amounts

The unified extraction service combines AI extraction with deterministic
fallback values when fields are missing.

Arithmetic validation is also used for selected receipt scenarios.

---

# Testing

Run the complete test suite:

```powershell
pytest -q
```

The current implementation passes:

```text
16 passed
```

There are currently two dependency deprecation warnings from the testing stack.
They do not cause test failures.

The test suite covers:

* Receipt fallback extraction
* API health endpoint
* Receipt upload
* Unsupported file handling
* Receipt retrieval
* Food agent routing
* Travel agent routing
* Office agent routing
* Dispatcher behavior
* Unknown expense handling
* Summary calculations
* Recipient loading
* Excel report generation
* Email dry-run behavior
* Stored expense retrieval

The API tests use an isolated in-memory SQLite database so test data does not
pollute the application's real `receipts.db`.

---

# Design Decisions

## AI + Deterministic Fallback

AI extraction is the primary extraction layer.

Deterministic rules provide a secondary validation and enrichment layer for
cases where:

* AI output is incomplete
* OCR contains common errors
* Receipt formatting is unusual
* Certain fields need additional validation

This provides a balance between flexible AI extraction and predictable
rule-based behavior.

---

## Local SQLite Persistence

SQLite was selected because it:

* Requires no external database service
* Is lightweight
* Is easy to inspect
* Is sufficient for the assessment
* Integrates directly with SQLAlchemy

For a production system, the database could be migrated to PostgreSQL or
another managed database.

---

## Custom Multi-Agent Architecture

The Part 2 implementation uses small Python agent classes instead of a large
agent framework.

This keeps the workflow:

* Transparent
* Testable
* Easy to understand
* Easy to extend
* Lightweight

Each specialized agent implements a common interface and can be replaced or
extended independently.

---

## API-Centered Architecture

The Streamlit frontend communicates with the FastAPI backend instead of
accessing the database directly.

This keeps responsibilities separated:

```text
Frontend
   |
   v
FastAPI
   |
   +---- Extraction
   +---- Classification
   +---- Persistence
   +---- Reporting
   +---- Email
```

This also makes the backend reusable by other clients.

---

## Safe Email Delivery

The command-line workflow defaults to dry-run email behavior to prevent
accidental messages during development and testing.

The Streamlit workflow supports intentional real email delivery when valid
SMTP credentials are configured.

SMTP credentials are stored in `.env` and are not embedded in the frontend.

---

# Security Considerations

* API keys are stored in `.env`.
* SMTP credentials are stored in `.env`.
* `.env` is excluded from Git through `.gitignore`.
* Test databases are isolated from the application's production/local
  database.
* CLI email delivery defaults to dry-run mode.
* Real email delivery requires explicit SMTP configuration and a recipient
  email entered through the UI.

Never commit:

```text
.env
receipts.db
API keys
SMTP passwords
Gmail App Passwords
```

---

# Example End-to-End Run

Start FastAPI:

```powershell
uvicorn backend.main:app --reload
```

Start Streamlit in a second terminal:

```powershell
streamlit run frontend/app.py
```

Then:

1. Upload a receipt.
2. Click **Process Receipt**.
3. Review the extracted receipt information.
4. Confirm the expense category.
5. Scroll to **Expense Report**.
6. Enter the recipient email.
7. Click **Generate & Send Expense Report**.
8. Review receipt count and category totals.
9. Download the generated Excel report if required.
10. Check the recipient inbox when real SMTP delivery is enabled.

---

# Sample Validation

The application was validated against multiple receipt formats including:

* Target PNG
* Quick-Mart PNG
* Quick-Mart PDF
* Corner Bistro JPG
* Corner Bistro PDF
* Corner Bistro PNG

The extraction pipeline was validated for:

* Merchant
* Date
* Line items
* Prices
* Tax
* Tip
* Total

The Part 2 workflow was also validated using a stored Corner Bistro receipt:

```text
Receipts processed: 1
Total amount: 99.48
Category: Food
Category total: 99.48
```

The generated Excel report correctly reflected the stored receipt.

---

# Future Improvements

Possible future improvements include:

* Replace keyword routing with an LLM-based classification agent
* Add confidence scores for extracted fields
* Add duplicate receipt detection
* Add stronger receipt arithmetic validation
* Support additional expense categories
* Add authentication and authorization
* Add user-specific expense accounts
* Move SQLite to PostgreSQL for production deployments
* Add asynchronous/background receipt processing
* Add production-grade email provider integration
* Add structured application logging
* Add API rate limiting
* Add containerized deployment
* Add CI/CD pipeline
* Add automated frontend tests

---

# Technology Stack

| Component        | Technology       |
| ---------------- | ---------------- |
| Backend          | FastAPI          |
| Frontend         | Streamlit        |
| Database         | SQLite           |
| ORM              | SQLAlchemy       |
| Data Validation  | Pydantic         |
| OCR              | Tesseract        |
| PDF Processing   | PyMuPDF          |
| Image Processing | Pillow           |
| AI Extraction    | OpenRouter       |
| HTTP Client      | httpx / requests |
| Excel Reports    | openpyxl         |
| Email            | Python SMTP      |
| Testing          | pytest           |

---

# Running the Complete Application

### Terminal 1 — Backend

```powershell
uvicorn backend.main:app --reload
```

### Terminal 2 — Frontend

```powershell
streamlit run frontend/app.py
```

### Optional — CLI Part 2 Workflow

```powershell
python -m part2.run_expense_workflow
```

The Streamlit application provides the integrated Part 1 + Part 2 workflow,
while the CLI command provides a separate dry-run demonstration of the Part 2
workflow.

---

## Project Status

The application currently provides:

* End-to-end receipt extraction
* OCR and PDF processing
* AI-based structured extraction
* Deterministic fallback extraction
* SQLite persistence
* Expense categorization
* Custom multi-agent workflow
* Expense summarization
* Excel report generation
* Streamlit UI integration
* REST API
* Email delivery support
* Report download
* Automated tests