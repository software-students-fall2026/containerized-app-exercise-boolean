"""Read a barcode photo and find its product."""

import io
import os
import time
import requests
import zxingcpp
from PIL import Image
from pymongo import MongoClient

PRODUCT_URL = "https://world.openfoodfacts.org/api/v2/product/{}.json"
SERPAPI_URL = "https://serpapi.com/search.json"
USER_AGENT = (
    "Boolean/1.0 "
    "(https://github.com/software-students-fall2026/containerized-app-exercise-boolean)"
)


def read_barcode(photo):
    """Find the barcode number in photo bytes."""
    try:
        # Pillow package opens the uploaded bytes as an image.
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


def lookup_offers(product):
    """Find online stores selling the product."""
    api_key = os.getenv("SERPAPI_KEY")

    if not api_key:
        raise ValueError("SerpApi key is missing.")

    # Build a search query using the product name and brand
    query = f'{product.get("brand", "")} {product["name"]}'.strip()

    # Search Google Shopping through SerpApi
    response = requests.get(
        SERPAPI_URL,
        params={
            "engine": "google_shopping",
            "q": query,
            "gl": "us",
            "api_key": api_key,
        },
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()

    if data.get("error"):
        raise ValueError(data["error"])

    # Find the matching product
    product_id = None

    for item in data.get("shopping_results", []):
        if product["name"].lower() in item.get("title", "").lower():
            product_id = item.get("product_id")
            if product_id:
                break

    # No matching product found
    if not product_id:
        return []

    # Get the stores selling this product
    response = requests.get(
        SERPAPI_URL,
        params={
            "engine": "google_product",
            "product_id": product_id,
            "offer_view": "true",
            "gl": "us",
            "api_key": api_key,
        },
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()

    if data.get("error"):
        raise ValueError(data["error"])

    offers = []

    for store in data.get("product_results", {}).get("stores", []):
        price = store.get("extracted_price")
        link = store.get("link")

        if price is not None and link:
            offers.append(
                {
                    "store": store.get("name") or "Online store",
                    "price": price,
                    "link": link,
                }
            )

    # Sort from lowest price to highest price
    offers.sort(key=lambda offer: offer["price"])

    # Return up to five offers
    return offers[:5]


def process_one_scan(collection):
    """Process one pending photo from MongoDB, if there is one."""
    # The frontend will save the new uploads with status "pending".
    scan = collection.find_one({"status": "pending"})
    if scan is None:
        return False

    barcode = None
    try:
        photo = scan.get("barcode_image")
        if not photo:
            raise ValueError("No barcode photo was uploaded.")

        barcode = read_barcode(photo)
        product = lookup_product(barcode)
        result = {"status": "completed", "barcode": barcode, "product": product}

        try:
            result["offers"] = lookup_offers(product)
        except (ValueError, requests.RequestException):
            result["offers"] = []
            result["offers_error"] = "Online prices are unavailable."

    except (ValueError, requests.RequestException) as error:
        # Save an error so the frontend can tell the shopper what happened.
        result = {"status": "failed", "error": str(error)}
        if barcode is not None:
            result["barcode"] = barcode

    collection.update_one({"_id": scan["_id"]}, {"$set": result})
    return True


def process_scans():
    """Keep checking MongoDB for uploaded scans."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DB_NAME", "boolean_barcode")

    client = MongoClient(mongo_uri)
    client.admin.command("ping")
    collection = client[db_name]["scans"]
    print("Connected to MongoDB", flush=True)

    try:
        while True:
            process_one_scan(collection)
            time.sleep(2)
    finally:
        client.close()


if __name__ == "__main__":
    process_scans()
