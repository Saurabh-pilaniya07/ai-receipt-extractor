import json
import os

import httpx
from dotenv import load_dotenv

from backend.schemas.receipt import ReceiptExtraction
from backend.services.fallback import extract_with_rules

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openrouter/free"


EXTRACTION_PROMPT = """
You are a receipt data extraction system.

Extract structured information from the receipt text below.

Return ONLY valid JSON with exactly these fields:

{
  "merchant_name": string or null,
  "date": string or null,
  "line_items": [
    {
      "item_name": string,
      "price": number
    }
  ],
  "total_amount": number or null,
  "tax": number or null,
  "tip": number or null
}

Rules:
1. Preserve the merchant/store name exactly as reasonably readable.
2. Convert the receipt date to YYYY-MM-DD when possible.
3. Extract every purchased line item.
4. For quantities such as "2x Caesar Salad $22.00", the price should be
   the line total shown on the receipt, not the unit price.
5. Extract tax when present.
6. Extract gratuity/tip when present.
7. Do not treat subtotal as the total amount.
8. Use TOTAL, TOTAL DUE, GRAND TOTAL, etc. as total_amount.
9. Do not invent information.
10. If a field is not present or cannot be determined, return null.
11. Return JSON only. No markdown and no explanation.
12. The input may contain PRIMARY OCR and SECONDARY OCR sections.
13. Use both sections together and resolve conflicting or duplicated information.
14. Ignore OCR noise, decorative characters, separator lines, and repeated text.
15. Pay particular attention to the first meaningful text near the top of the receipt when identifying the merchant.
16. Receipts may use numbered items such as "1.", "2.", "3." instead of quantities.
17. Ignore store addresses, phone numbers, order numbers, table numbers,
    payment information, authorization codes, and other non-purchase metadata.
18. A tax percentage in parentheses is not the tax amount. Extract the
    actual monetary tax amount when available.
19. Prices must be numeric values without currency symbols.
20. If OCR contains minor character errors such as "$99,48", interpret
    the value as a monetary amount when the context clearly indicates it.
21. Do not confuse subtotal with total.
22. If the receipt contains "TOTAL", "TOTAL PAID", or "TOTAL DUE",
    use that monetary value as total_amount.

Receipt text:
"""


def extract_receipt_data(text: str) -> ReceiptExtraction:
    """
    Send OCR text to OpenRouter and convert the response
    into our validated ReceiptExtraction schema.
    """

    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not configured."
        )

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": EXTRACTION_PROMPT + text,
            }
        ],
        "temperature": 0,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
        )

    response.raise_for_status()

    result = response.json()

    content = result["choices"][0]["message"]["content"]

    # Clean and parse the model response.
    content = content.strip()

    if not content:
        raise ValueError(
         "The AI model returned an empty response."
     )


    def parse_json_response(content: str) -> dict:
        """
        Parse JSON from an LLM response.

        Handles:
        - Plain JSON
        - ```json ... ``` code fences
        - Explanatory text surrounding JSON
        """

        # Case 1: Markdown code fence
        if "```" in content:
            parts = content.split("```")

            for part in parts:
                cleaned = part.strip()

                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()

                if cleaned.startswith("{") and cleaned.endswith("}"):
                    try:
                        return json.loads(cleaned)
                    except json.JSONDecodeError:
                        pass

        # Case 2: Plain JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Case 3: JSON embedded inside explanatory text
        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1 and end > start:
            candidate = content[start:end + 1]

            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        raise ValueError(
            "AI model did not return valid JSON."
        )


    try:
        extracted = parse_json_response(content)

        return ReceiptExtraction.model_validate(
            extracted
        )

    except (ValueError, json.JSONDecodeError):
        # AI response was unusable.
        # Fall back to deterministic OCR parsing.
        return extract_with_rules(text)