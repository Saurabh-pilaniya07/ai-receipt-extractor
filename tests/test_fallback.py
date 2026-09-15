from backend.services.fallback import extract_with_rules


def test_target_receipt_extraction():
    text = """
    TARGET STORES
    Date: 02/18/2026

    1. Wireless Mouse       $24.99
    2. USB-C Cable 6ft      $12.50
    3. Notebook 3-Pack       $8.99

    SUBTOTAL                $46.48
    TAX (8.25%)              $3.83
    TOTAL                    $50.31
    """

    result = extract_with_rules(text)

    assert result.merchant_name == "TARGET STORES"
    assert result.date == "2026-02-18"

    assert len(result.line_items) == 3
    assert result.line_items[0].item_name == "Wireless Mouse"
    assert result.line_items[0].price == 24.99

    assert result.tax == 3.83
    assert result.total_amount == 50.31
    assert result.tip is None


def test_corner_bistro_extraction():
    text = """
    THE CORNER BISTRO
    Date: Feb 20, 2026

    1x Sparkling Water     $4.00
    2x Caesar Salad        $22.00
    2x Grilled Salmon      $48.00
    1x Espresso            $3.50

    SUBTOTAL               $77.50
    TAX                    $6.98
    GRATUITY / TIP         $15.00
    TOTAL DUE              $99.48
    """

    result = extract_with_rules(text)

    assert result.merchant_name == "THE CORNER BISTRO"
    assert result.date == "2026-02-20"

    assert len(result.line_items) == 4

    assert result.tax == 6.98
    assert result.tip == 15.00
    assert result.total_amount == 99.48


def test_total_is_calculated_when_ocr_total_is_missing():
    text = """
    TARGET STORES
    1. Wireless Mouse       $24.99
    2. USB-C Cable 6ft      $12.50
    3. Notebook 3-Pack       $8.99

    SUBTOTAL                $46.48
    TAX                     $3.83
    """

    result = extract_with_rules(text)

    assert result.total_amount == 50.31