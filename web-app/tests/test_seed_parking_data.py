"""Tests for the sample parking data generator."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from seed_parking_data import generate_parking_data


def test_generates_ten_spaces():
    spaces = generate_parking_data()
    assert len(spaces) == 10


def test_spot_ids_are_unique():
    spaces = generate_parking_data()
    ids = [space["spot_id"] for space in spaces]
    assert len(ids) == len(set(ids))


def test_occupancy_is_boolean():
    spaces = generate_parking_data()
    assert all(isinstance(space["occupied"], bool) for space in spaces)


def test_zero_spaces():
    assert generate_parking_data(0) == []
