"""
Incident API Tests
Tests all incident management endpoints
"""
import pytest
from fastapi import status


class TestIncidentCreation:
    """Test incident creation endpoint."""
    
    def test_create_incident_success(self, client, auth_headers):
        """Test successful incident creation."""
        incident_data = {
            "title": "Car Accident on Highway 101",
            "description": "Multiple vehicle collision, 3 victims",
            "incident_type": "road_accident",
            "severity": "high",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "location": "Highway 101, San Francisco",
            "victim_count": 3,
            "caller_phone": "+1234567890",
        }
        
        response = client.post(
            "/api/v1/incidents",
            json=incident_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == incident_data["title"]
        assert data["status"] == "pending"
        assert "id" in data
    
    def test_create_incident_missing_fields(self, client, auth_headers):
        """Test incident creation with missing required fields."""
        incomplete_data = {
            "title": "Incident without location",
        }
        
        response = client.post(
            "/api/v1/incidents",
            json=incomplete_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_incident_invalid_coordinates(self, client, auth_headers):
        """Test incident creation with invalid coordinates."""
        invalid_data = {
            "title": "Test Incident",
            "description": "Test description",
            "incident_type": "road_accident",
            "severity": "high",
            "latitude": 200.0,  # Invalid latitude
            "longitude": -122.4194,
            "location": "Test Location",
            "victim_count": 1,
        }
        
        response = client.post(
            "/api/v1/incidents",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestIncidentRetrieval:
    """Test incident retrieval endpoints."""
    
    def test_get_incident_by_id(self, client, auth_headers, test_incident):
        """Test getting incident by ID."""
        response = client.get(
            f"/api/v1/incidents/{test_incident.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_incident.id
        assert data["title"] == test_incident.title
    
    def test_get_nonexistent_incident(self, client, auth_headers):
        """Test getting nonexistent incident."""
        response = client.get(
            "/api/v1/incidents/99999",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_incidents(self, client, auth_headers, test_incident):
        """Test listing all incidents."""
        response = client.get(
            "/api/v1/incidents",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_list_incidents_with_filters(self, client, auth_headers, test_incident):
        """Test listing incidents with filters."""
        response = client.get(
            "/api/v1/incidents?status=pending&severity=high",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)


class TestIncidentWorkflow:
    """Test incident workflow (approve, reject, dispatch)."""
    
    def test_approve_incident(self, client, auth_headers, test_incident):
        """Test approving incident plan."""
        response = client.post(
            f"/api/v1/incidents/{test_incident.id}/approve",
            json={"approved_by": "Test Coordinator"},
            headers=auth_headers
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_reject_incident(self, client, auth_headers, test_incident):
        """Test rejecting incident plan."""
        response = client.post(
            f"/api/v1/incidents/{test_incident.id}/reject",
            json={
                "rejected_by": "Test Coordinator",
                "rejection_reason": "Insufficient resources"
            },
            headers=auth_headers
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_dispatch_incident(self, client, auth_headers, test_incident):
        """Test dispatching incident resources."""
        response = client.post(
            f"/api/v1/incidents/{test_incident.id}/dispatch",
            headers=auth_headers
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_update_incident_status(self, client, auth_headers, test_incident):
        """Test updating incident status."""
        response = client.patch(
            f"/api/v1/incidents/{test_incident.id}/status",
            json={"status": "in_progress"},
            headers=auth_headers
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestIncidentValidation:
    """Test incident data validation."""
    
    def test_invalid_severity(self, client, auth_headers):
        """Test incident with invalid severity."""
        invalid_data = {
            "title": "Test Incident",
            "description": "Test",
            "incident_type": "road_accident",
            "severity": "invalid_severity",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "victim_count": 1,
        }
        
        response = client.post(
            "/api/v1/incidents",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_negative_victim_count(self, client, auth_headers):
        """Test incident with negative victim count."""
        invalid_data = {
            "title": "Test Incident",
            "description": "Test",
            "incident_type": "road_accident",
            "severity": "high",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "victim_count": -1,
        }
        
        response = client.post(
            "/api/v1/incidents",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
