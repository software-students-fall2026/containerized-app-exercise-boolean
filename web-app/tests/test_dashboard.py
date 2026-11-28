"""Tests for grocery dashboard routes."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# pylint: disable=wrong-import-position
from app import app


def test_dashboard_loads():
    """Verify that the dashboard loads successfully."""
    client = app.test_client()
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"Grocery Price Finder" in response.data


def test_home_redirects_to_dashboard():
    """Verify that the homepage redirects correctly."""
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")


def test_dashboard_has_required_sections():
    """Verify that the dashboard displays its main sections."""
    client = app.test_client()
    response = client.get("/dashboard")

    assert b"Product Details" in response.data
    assert b"Price Comparisons" in response.data
    assert b"Recent Scans" in response.data
