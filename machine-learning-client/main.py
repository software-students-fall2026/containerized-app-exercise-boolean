"""Read a barcode photo and find its product."""

import io
import requests
import zxingcpp
from PIL import Image

PRODUCT_URL = "https://world.openfoodfacts.org/api/v2/product/{}.json"
USER_AGENT = (
    "BooleanBarcode/1.0 "
    "(https://github.com/software-students-fall2026/containerized-app-exercise-boolean)"
)


def read_barcode(photo):
    """Find the barcode number in photo bytes."""
    try:
        # Pillow opens the uploaded bytes as an image.
        with Image.open(io.BytesIO(photo)) as image:
            picture = image.convert("RGB")
    except (OSError, ValueError) as error:
        raise ValueError("Please upload a valid image.") from error

    # The barcode library looks at the pixels in the photo.
    barcodes = zxingcpp.read_barcodes(picture)  # pylint: disable=no-member
    for barcode in barcodes:
        number = barcode.text
        if number.isdigit() and len(number) in (8, 12, 13, 14):
            return number

    raise ValueError("No barcode was found in this photo.")


def lookup_product(barcode):
    """Find basic product details using its barcode number."""
    # Send the number rather than the photo to the product API.
    response = requests.get(
        PRODUCT_URL.format(barcode),
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("status") != 1 or not data.get("product"):
        raise ValueError("Product not found for this barcode.")

    product = data["product"]
    return {
        "barcode": barcode,
        "name": product.get("product_name") or "Unnamed product",
        "brand": product.get("brands") or "",
        "image_url": product.get("image_front_url") or "",
        "categories": product.get("categories_tags") or [],
    }
