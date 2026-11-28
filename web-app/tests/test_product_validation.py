import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from product_validation import is_valid_barcode


def test_valid_upc_barcode():
    assert is_valid_barcode("012345678905")


def test_valid_ean_barcode():
    assert is_valid_barcode("4006381333931")


def test_short_barcode():
    assert not is_valid_barcode("12345")


def test_barcode_with_letters():
    assert not is_valid_barcode("hello1234567")


def test_wrong_check_digit():
    assert not is_valid_barcode("012345678906")


def test_missing_barcode():
    assert not is_valid_barcode(None)


def test_non_ascii_digits():
    assert not is_valid_barcode("１２３４５６７８９０１２")
