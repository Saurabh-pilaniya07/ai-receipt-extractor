from backend.services.llm import extract_receipt_data


OCR_TEXT = """
THE CORNER BISTRO
Order #849 - Table 12
Date: Feb 20, 2026 Time: 19:45

1x Sparkling Water        $ 4.00
2x Caesar Salad           $ 22.00
2x Grilled Salmon         $ 48.00
1x Espresso               $ 3.50

SUBTOTAL                  $ 77.50
TAX                       $ 6.98
GRATUITY / TIP            $ 15.00

TOTAL DUE                $ 99.48

Server: Sarah M.
"""


if __name__ == "__main__":
    result = extract_receipt_data(OCR_TEXT)

    print("\n===== AI EXTRACTION RESULT =====\n")
    print(result.model_dump_json(indent=2))
    print("\n=================================\n")