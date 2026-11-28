def is_valid_barcode(barcode):
    if not isinstance(barcode, str):
        return False

    if len(barcode) not in (12, 13):
        return False

    if not barcode.isascii() or not barcode.isdigit():
        return False
    digits = [int(digit) for digit in barcode]

    total = sum(
        digit * (3 if index % 2 == 0 else 1)
        for index, digit in enumerate(reversed(digits[:-1]))
    )
    expected_check_digit = (-total) % 10

    return digits[-1] == expected_check_digit
