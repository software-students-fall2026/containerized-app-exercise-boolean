
"""Tests for UPC-A and EAN-13 grocery barcode validation."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# pylint: disable=wrong-import-position
from product_validation import is_valid_barcode


def test_valid_upc_barcode():
    """Accept a valid UPC-A barcode."""
    assert is_valid_barcode("012345678905")


def test_valid_ean_barcode():
    """Accept a valid EAN-13 barcode."""
    assert is_valid_barcode("4006381333931")


def test_short_barcode():
    """Reject barcodes that are too short."""
    assert not is_valid_barcode("12345")


def test_barcode_with_letters():
    """Reject barcodes containing letters."""
    assert not is_valid_barcode("hello1234567")


def test_wrong_check_digit():
    """Reject barcodes with an incorrect checksum."""
    assert not is_valid_barcode("012345678906")


def test_missing_barcode():
    """Reject a missing barcode."""
    assert not is_valid_barcode(None)


def test_non_ascii_digits():
    """Reject non-ASCII barcode digits."""
    assert not is_valid_barcode("１２３４５６７８９０１２")
