"""Tests for reading barcodes and looking up products."""

import io
from unittest.mock import patch
import pytest
import requests
import zxingcpp
from PIL import Image
import main


class TestMain:
    """Test the barcode and product functions in main.py."""

    def test_reads_barcode(self):
        """A barcode photo should return the correct number."""
        # Generate a barcode image so we do not need an actual image for this test.
        # pylint: disable=no-member
        barcode = zxingcpp.create_barcode("3017620422003", zxingcpp.BarcodeFormat.EAN13)
        # pylint: enable=no-member

        image = Image.fromarray(barcode.to_image(scale=4))
        photo = io.BytesIO()
        image.save(photo, format="PNG")

        expected = "3017620422003"
        actual = main.read_barcode(photo.getvalue())
        assert actual == expected

    def test_blank_photo(self):
        """A photo with no barcode should give an error."""
        photo = io.BytesIO()
        Image.new("RGB", (200, 200), "white").save(photo, format="PNG")

        with pytest.raises(ValueError, match="No barcode"):
            main.read_barcode(photo.getvalue())

    def test_invalid_image(self):
        """A file that is not an image should give an error."""
        with pytest.raises(ValueError, match="valid image"):
            main.read_barcode(b"not an image")

    def test_product_found(self):
        """A listed product should have a name, brand, and image."""
        # Pretending the product API sent back this information.
        with patch("main.requests.get") as fake_get:
            fake_get.return_value.json.return_value = {
                "status": 1,
                "product": {
                    "product_name": "Chocolate spread",
                    "brands": "Example Brand",
                    "image_front_url": "https://example.com/image.jpg",
                },
            }
            actual = main.lookup_product("3017620422003")

        assert actual["name"] == "Chocolate spread"
        assert actual["brand"] == "Example Brand"
        assert actual["image_url"] == "https://example.com/image.jpg"

    def test_product_not_found(self):
        """An unknown barcode should give an error."""
        with patch("main.requests.get") as fake_get:
            fake_get.return_value.json.return_value = {"status": 0}

            with pytest.raises(ValueError, match="Product not found"):
                main.lookup_product("12345678")

    def test_product_api_timeout(self):
        """An API timeout should be reported as an error."""
        with patch("main.requests.get", side_effect=requests.Timeout):
            with pytest.raises(requests.Timeout):
                main.lookup_product("3017620422003")
