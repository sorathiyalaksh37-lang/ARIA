"""
Backend Unit Test Suite
Tests for ARIA core emergency response services:
Bystander Protocols, START Triage, Family Notifications, Green Corridor, and Hospital Prep.
"""

import pytest
import asyncio
from datetime import datetime

# Import services
from app.services.bystander.protocols import get_protocol, search_protocols
from app.services.bystander.location import find_nearby_resources
from app.services.mass_casualty.triage import triage_manager
from app.services.family.contact_service import family_contact_service
from app.services.family.notification_service import family_notification_service
from app.services.family.tracking_service import family_tracking_service
from app.services.traffic.corridor_service import green_corridor_service
from app.services.traffic.traffic_service import city_traffic_service
from app.services.hospital.preparation_service import hospital_prep_service


@pytest.mark.asyncio
async def test_bystander_protocols():
    """Test bystander first aid protocol retrieval and multi-language support"""
    cpr_en = get_protocol("cpr", lang="en")
    assert cpr_en is not None
    assert cpr_en["protocol_id"] == "cpr"
    assert cpr_en["compression_rate"] == "100-120 bpm"

    cpr_hi = get_protocol("cpr", lang="hi")
    assert cpr_hi is not None
    assert "सीपीआर" in cpr_hi["title"]

    results = search_protocols("bleeding")
    assert len(results) > 0
    assert results[0]["protocol_id"] == "bleeding_control"


@pytest.mark.asyncio
async def test_bystander_location():
    """Test finding nearby AEDs, CPR civilians, and emergency clinics"""
    res = await find_nearby_resources(latitude=37.7749, longitude=-122.4194, radius_km=3.0)
    assert "aeds" in res
    assert "cpr_certified_civilians" in res
    assert len(res["aeds"]) > 0
    assert "navigation_url" in res["aeds"][0] or "google_maps_url" in res["aeds"][0]


@pytest.mark.asyncio
async def test_start_triage_algorithm():
    """Test START triage algorithm categorization (RED, YELLOW, GREEN, BLACK)"""
    # 1. Immediate (RED) - Unresponsive, breathing > 30 bpm
    red_result = triage_manager.classify_victim(
        respirations_pm=34,
        pulse_present=True,
        can_follow_commands=False
    )
    assert red_result == "RED"

    # 2. Delayed (YELLOW) - Breathing < 30, pulse present, can follow commands
    yellow_result = triage_manager.classify_victim(
        respirations_pm=22,
        pulse_present=True,
        can_follow_commands=True
    )
    assert yellow_result == "YELLOW"

    # 3. Expectant (BLACK) - No respirations
    black_result = triage_manager.classify_victim(
        respirations_pm=0,
        pulse_present=False,
        can_follow_commands=False
    )
    assert black_result == "BLACK"


@pytest.mark.asyncio
async def test_family_communication_system():
    """Test family contact registration, notification dispatch, and tracking tokens"""
    incident_id = "TEST-INC-99"

    # 1. Add contact
    contact = await family_contact_service.add_contact(
        incident_id=incident_id,
        name="Alice Test",
        phone="+1-555-999-0000",
        email="alice@example.com",
        relationship="Parent",
        is_primary=True,
        preferred_channel="WHATSAPP",
        language="en",
        privacy_level="FULL_MEDICAL"
    )
    assert contact["name"] == "Alice Test"
    assert contact["is_primary"] is True

    # 2. Dispatch milestone notification
    notif = await family_notification_service.notify_milestone(
        incident_id=incident_id,
        event_type="PATIENT_EN_ROUTE",
        hospital_name="Test General Hospital",
        eta_minutes=8
    )
    assert notif["contacts_notified_count"] == 1
    assert "dispatched_logs" in notif

    # 3. Test tracking link
    tracking = await family_tracking_service.get_tracking_by_incident(incident_id)
    assert tracking["incident_id"] == incident_id
    assert tracking["token"].startswith("TRACK-")


@pytest.mark.asyncio
async def test_green_corridor_traffic_preemption():
    """Test Green Corridor signal preemption and time savings calculation"""
    savings = await green_corridor_service.calculate_time_savings(distance_km=10.0, normal_light_stops=10)
    assert savings["time_saved_minutes"] > 0
    assert savings["percentage_time_saved"] > 30.0

    corridor = await green_corridor_service.create_green_corridor(ambulance_id="AMB-TEST")
    assert corridor["status"] == "ACTIVE"
    assert len(corridor["preempted_nodes"]) > 0


@pytest.mark.asyncio
async def test_hospital_preparation_checklist():
    """Test hospital pre-arrival checklist generation, staff check-off, and progress %"""
    incident_id = "PREP-TEST-1"

    # 1. Generate trauma checklist
    prep = await hospital_prep_service.generate_checklist(
        incident_id=incident_id,
        emergency_category="TRAUMA",
        patient_name="Test Patient"
    )
    assert prep["emergency_category"] == "TRAUMA"
    assert prep["total_items"] > 0
    assert prep["completed_items"] == 0

    # 2. Toggle first item
    first_item_id = prep["items"][0]["item_id"]
    updated = await hospital_prep_service.toggle_item(
        incident_id=incident_id,
        item_id=first_item_id,
        completed=True,
        staff_id="STF-TEST"
    )
    assert updated["completed_items"] == 1
    assert updated["progress_percentage"] > 0.0
