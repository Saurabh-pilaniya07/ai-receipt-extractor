# AI Receipt Extractor

An end-to-end AI-powered receipt extraction and expense management POC.

The application accepts **PNG, JPG, JPEG, and PDF** receipts, extracts structured expense data using OCR + AI, categorizes expenses through lightweight agents, stores results in SQLite, and generates downloadable Excel expense reports. Email delivery is available as a separate optional step.

## Features

### Receipt Extraction
- PNG, JPG, JPEG, and PDF support
- Tesseract OCR with image preprocessing
- PyMuPDF PDF text extraction and scanned-PDF OCR
- AI-powered structured extraction
- Deterministic fallback extraction
- Merchant, date, line items, total, tax, and tip extraction
- SQLite persistence with SQLAlchemy
- FastAPI REST API
- Streamlit frontend
- Receipt history

### Multi-Agent Expense Workflow
- Food, Travel, and Office expense agents
- Deterministic expense dispatcher
- Expense summary agent
- Excel report generation
- Separate report download
- Optional SMTP email delivery
- CLI dry-run email workflow

## Architecture

```text
Receipt
   |
   v
OCR / PDF Text Extraction
   |
   v
AI Extraction
   |
   v
Deterministic Fallback / Validation
   |
   v
Structured Receipt
   |
   v
Expense Dispatcher
   |
   +---- Food Agent
   +---- Travel Agent
   +---- Office Agent
   |
   v
SQLite
   |
   v
Expense Summary Agent
   |
   v
Excel Report
   |
   +---- Download
   |
   +---- Optional Email
```

The Streamlit frontend communicates with the FastAPI backend; it does not access the database directly.

## Project Structure

```text
Receipt Extractor/
├── backend/
│   ├── agents/
│   │   ├── base.py
│   │   ├── food_agent.py
│   │   ├── travel_agent.py
│   │   ├── office_agent.py
│   │   ├── dispatcher.py
│   │   └── summary_agent.py
│   ├── api/
│   │   └── routes.py
│   ├── models/
│   │   ├── database.py
│   │   └── receipt.py
│   ├── schemas/
│   │   └── receipt.py
│   ├── services/
│   │   ├── ocr.py
│   │   ├── pdf.py
│   │   ├── llm.py
│   │   ├── extraction.py
│   │   ├── fallback.py
│   │   ├── expense_data.py
│   │   ├── recipients.py
│   │   ├── report.py
│   │   └── email.py
│   └── main.py
├── frontend/
│   └── app.py
├── part2/
│   ├── recipients.xlsx
│   └── run_expense_workflow.py
├── sample_receipts/
├── tests/
│   ├── test_api.py
│   ├── test_fallback.py
│   └── test_agents.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### 1. Create virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

Install Tesseract OCR locally. The current Windows configuration uses:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

The application automatically uses this path when the executable exists.

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key

SMTP_SENDER=your_email@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

For Gmail, use an **App Password** where required.

Never commit `.env`, API keys, SMTP passwords, or App Passwords.

## Running the Application

### Terminal 1 — FastAPI

```powershell
uvicorn backend.main:app --reload
```

API: `http://127.0.0.1:8000`

Interactive documentation: `http://127.0.0.1:8000/docs`

### Terminal 2 — Streamlit

```powershell
streamlit run frontend/app.py
```

The UI supports:

1. Uploading a receipt
2. Processing and reviewing extracted fields
3. Viewing stored receipts
4. Generating an expense report
5. Downloading the generated Excel report
6. Sending the generated report by email

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | API health check |
| POST | `/upload` | Upload and process a receipt |
| GET | `/receipts` | Retrieve stored receipts |
| POST | `/expense-report` | Generate the Excel expense report |
| GET | `/expense-report/download` | Download the generated report |
| POST | `/expense-report/send-email` | Send the generated report by email |

### Upload Receipt

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
    {"item_name": "Sparkling Water", "price": 4.0},
    {"item_name": "Caesar Salad", "price": 22.0}
  ],
  "tax": 6.98,
  "tip": 15.0
}
```

### Expense Report Workflow

Report generation and email delivery are intentionally separated:

```text
Stored Receipts
      |
      v
POST /expense-report
      |
      v
Excel Report
   /       \
  v         v
Download   Send Email
```

**Generate:** `POST /expense-report` reads stored receipts, summarizes expenses, and creates `part2/expense_report.xlsx`.

**Download:** `GET /expense-report/download` downloads the latest generated Excel report.

**Send Email:** `POST /expense-report/send-email` sends the already-generated Excel report using SMTP.

If email configuration or authentication fails, report generation and download remain available independently.

## Part 2 — Multi-Agent Workflow

The bonus workflow uses small Python classes rather than a large agent framework.

```text
Structured Receipt
       |
       v
Expense Dispatcher
   |      |      |
 Food  Travel  Office
   \      |      /
       Summary
          |
          v
     Excel Report
          |
          v
    Optional Email
```

### Agents

- **Food Agent** — food, restaurants, cafes, groceries, meals, beverages
- **Travel Agent** — fuel, gas stations, taxis, flights, hotels, parking, tolls
- **Office Agent** — stationery, paper, electronics, equipment, office supplies
- **Summary Agent** — receipt count, total amount, category totals, expense list

The dispatcher uses deterministic keyword-based routing. Travel is checked before Food to avoid misclassifying fuel-station receipts that contain food or beverage product names.

### CLI Workflow

```powershell
python -m part2.run_expense_workflow
```

The CLI reads stored receipts, runs the summary workflow, generates the Excel report, loads recipients from `part2/recipients.xlsx`, and uses **dry-run email mode** by default.

## Extraction Pipeline

```text
Image --> Preprocessing --> Tesseract OCR --\
                                             --> AI Extraction
PDF ----> PyMuPDF / OCR --------------------/          |
                                                       v
                                             Deterministic Fallback
                                                       |
                                                       v
                                              Structured Receipt
```

Image preprocessing includes grayscale conversion, resizing, contrast enhancement, sharpening, and multiple OCR page-segmentation modes.

For PDFs, native text is extracted when available. Scanned/image-only PDFs are rendered and passed through OCR.

## Data Model

```json
{
  "merchant_name": "Example Merchant",
  "date": "2026-01-15",
  "line_items": [
    {"item_name": "Example Item", "price": 10.99}
  ],
  "total_amount": 12.09,
  "tax": 1.10,
  "tip": null
}
```

SQLite stores the receipt ID, filename, merchant, date, total, category, complete extracted JSON, and creation timestamp.

## Testing

Run:

```powershell
pytest -q
```

Current validation:

```text
16 passed
```

Tests cover extraction fallback, API behavior, receipt upload/retrieval, unsupported files, agent routing, dispatcher behavior, summary calculations, recipient loading, Excel report generation, email dry-run behavior, and stored expense retrieval.

API tests use an isolated in-memory SQLite database so test data does not pollute the local application database.

## Design Decisions

### AI + Deterministic Fallback

AI is the primary extraction layer. Deterministic rules provide fallback and enrichment when AI output is incomplete or OCR introduces common errors.

### SQLite

SQLite keeps the POC lightweight and requires no external database service. SQLAlchemy provides the persistence layer.

### Lightweight Agents

The custom Python agent design keeps routing transparent, testable, and easy to extend without introducing unnecessary framework complexity.

### Separate Reporting and Email

Report generation is independent from SMTP delivery. This ensures the core reporting feature remains usable even when external email configuration is unavailable.

## Security

- Secrets are loaded from `.env`.
- `.env` is excluded from Git.
- SMTP credentials are kept on the backend.
- CLI email delivery defaults to dry-run mode.
- Never commit API keys, SMTP passwords, or Gmail App Passwords.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | SQLite |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| OCR | Tesseract |
| PDF Processing | PyMuPDF |
| Image Processing | Pillow |
| AI Extraction | OpenRouter |
| Excel Reports | openpyxl |
| Email | Python SMTP |
| Testing | pytest |

## Sample Validation

The extraction pipeline was tested with multiple receipt representations including PNG, JPG, and PDF files, covering merchant, date, line items, prices, tax, tip, and total extraction.

The Part 2 workflow was also validated with stored receipt data and Excel report generation.

## Future Improvements

- Confidence scores for extracted fields
- Duplicate receipt detection
- Stronger arithmetic validation
- Additional expense categories
- Authentication and authorization
- PostgreSQL for production deployment
- Background receipt processing
- Production email provider integration
- CI/CD
- Containerized deployment
- API rate limiting
