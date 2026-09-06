"""
Locust Performance Load Testing Script
Simulates 100+ concurrent emergency incident dispatches, measuring API latency,
throughput, and WebSocket response performance for the ARIA platform.
"""

from locust import HttpUser, task, between, events
import time
import json


class ARIAEmergencyLoadUser(HttpUser):
    """Simulates active emergency response coordinators and automated telemetry agents."""

    wait_time = between(0.1, 0.5)  # High frequency traffic simulation

    @task(3)
    def query_bystander_protocols(self):
        """Query CPR and emergency protocols under load"""
        self.client.get("/api/v1/bystander/protocols?lang=en", name="GET /api/v1/bystander/protocols")

    @task(3)
    def check_traffic_time_savings(self):
        """Query Green Corridor time savings under load"""
        self.client.get("/api/v1/traffic/time-savings?distance_km=7.8&normal_stops=8", name="GET /api/v1/traffic/time-savings")

    @task(2)
    def get_hospital_prep_checklist(self):
        """Fetch active hospital pre-arrival checklist"""
        self.client.get("/api/v1/hospital-prep/checklist/INC-1001", name="GET /api/v1/hospital-prep/checklist")

    @task(1)
    def dispatch_family_milestone_notification(self):
        """Dispatch automatic family milestone alert"""
        payload = {
            "incident_id": "INC-1001",
            "event_type": "PATIENT_EN_ROUTE",
            "hospital_name": "General Trauma Center",
            "eta_minutes": 8,
            "patient_status": "STABLE"
        }
        self.client.post("/api/v1/family/notify-event", json=payload, name="POST /api/v1/family/notify-event")

    @task(1)
    def query_mass_casualty_status(self):
        """Query Mass Casualty Mode status"""
        self.client.get("/api/v1/mass-casualty/status", name="GET /api/v1/mass-casualty/status")
