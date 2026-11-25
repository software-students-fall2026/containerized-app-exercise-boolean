"""Unit tests for the parking sample data generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

# pylint: disable=wrong-import-position
from seed_parking_data import generate_parking_data


def test_generates_ten_spaces():
    """Verify that ten parking spaces are generated."""
    spaces = generate_parking_data()
    assert len(spaces) == 10


def test_spot_ids_are_unique():
    """Verify that every parking space has a unique ID."""
    spaces = generate_parking_data()
    ids = [space["spot_id"] for space in spaces]
    assert len(ids) == len(set(ids))


def test_occupancy_is_boolean():
    """Verify that occupancy values are Boolean."""
    spaces = generate_parking_data()
    assert all(isinstance(space["occupied"], bool) for space in spaces)


def test_zero_spaces():
    """Verify that requesting zero spaces returns no records."""
    assert not generate_parking_data(0)
