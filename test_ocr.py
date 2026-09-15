from backend.services.ocr import extract_text_from_image


if __name__ == "__main__":
    file_path = "sample_receipts/test_receipt.jpg"

    text = extract_text_from_image(file_path)

    print("\n===== OCR RESULT =====\n")
    print(text)
    print("\n======================\n")