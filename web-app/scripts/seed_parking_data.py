"""Generate sample parking occupancy data for development."""

import os
import random
from datetime import datetime, timezone

from pymongo import MongoClient


def generate_parking_data(total_spaces=10):
    """Create sample parking records."""
    spaces = []

    for number in range(1, total_spaces + 1):
        spaces.append(
            {
                "spot_id": f"A{number}",
                "occupied": random.choice([True, False]),
                "timestamp": datetime.now(timezone.utc),
            }
        )

    return spaces


def validate_parking_data(space):
    """Check whether a parking record has valid fields and types."""
    if not isinstance(space, dict):
        return False

    spot_id = space.get("spot_id")
    occupied = space.get("occupied")
    timestamp = space.get("timestamp")

    return (
        isinstance(spot_id, str)
        and bool(spot_id.strip())
        and isinstance(occupied, bool)
        and isinstance(timestamp, datetime)
        and timestamp.tzinfo is not None
        and timestamp.utcoffset() is not None
    )


def seed_database():
    """Insert sample records into MongoDB."""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGO_DB_NAME", "parking_management")

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    try:
        client.admin.command("ping")
        collection = client[db_name]["parking_spaces"]

        spaces = generate_parking_data()

        for space in spaces:
            if not validate_parking_data(space):
                raise ValueError(f"Invalid parking record: {space}")

            collection.update_one(
                {"spot_id": space["spot_id"]},
                {"$set": space},
                upsert=True,
            )

        print(f"Successfully seeded {len(spaces)} parking spaces!")

    finally:
        client.close()


if __name__ == "__main__":
    seed_database()
