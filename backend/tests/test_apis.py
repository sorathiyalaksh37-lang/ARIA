"""
FastAPI v1 Integration Test Suite
Tests endpoints for Bystander, Mass Casualty, Family Communication, Traffic Green Corridor, and Hospital Prep.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_bystander_api():
    """Test /api/v1/bystander endpoints"""
    response = client.get("/api/v1/bystander/protocols?lang=en")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "protocols" in data
    assert len(data["protocols"]) >= 5


def test_mass_casualty_api():
    """Test /api/v1/mass-casualty endpoints"""
    response = client.post("/api/v1/mass-casualty/activate", json={
        "incident_id": "MCI-API-TEST",
        "victim_count": 15,
        "location": "City Center Plaza"
    })
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["mci_status"] == "ACTIVE"


def test_family_api():
    """Test /api/v1/family endpoints"""
    # 1. Add contact
    response = client.post("/api/v1/family/contacts", json={
        "incident_id": "INC-API-TEST",
        "name": "API Contact",
        "phone": "+1-555-000-1111",
        "email": "api@example.com",
        "relationship": "Spouse",
        "is_primary": True
    })
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["name"] == "API Contact"

    # 2. Get tracking
    track_resp = client.get("/api/v1/family/tracking/TRACK-INC-1001-TOKEN")
    assert track_resp.status_code == 200


def test_traffic_api():
    """Test /api/v1/traffic endpoints"""
    response = client.get("/api/v1/traffic/time-savings?distance_km=8.0&normal_stops=6")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "time_saved_minutes" in data


def test_hospital_prep_api():
    """Test /api/v1/hospital-prep endpoints"""
    response = client.get("/api/v1/hospital-prep/checklist/INC-1001")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "emergency_category" in data
    assert "items" in data
