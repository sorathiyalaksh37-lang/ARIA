"""
Comprehensive Integration Test Suite for ARIA Platform
Tests all 32+ API endpoints, external services, and incident workflows
"""
import pytest
import asyncio
import os
from datetime import datetime
from typing import Dict, Any
import httpx
import json

# Test configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_EMAIL = "test@aria-emergency.com"
TEST_PASSWORD = "TestPassword123!"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class IntegrationTestRunner:
    """Main test runner for ARIA platform integration tests"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token = None
        self.test_incident_id = None
        self.test_ambulance_id = None
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "tests": []
        }
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def log(self, message: str, color: str = Colors.RESET):
        """Print colored log message"""
        print(f"{color}{message}{Colors.RESET}")
    
    def log_test(self, name: str, passed: bool, duration: float, error: str = None):
        """Log test result"""
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"  {status} {name} ({duration:.2f}s)")
        if error:
            print(f"    {Colors.RED}Error: {error}{Colors.RESET}")
        
        self.results["total"] += 1
        if passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
        
        self.results["tests"].append({
            "name": name,
            "passed": passed,
            "duration": duration,
            "error": error
        })
    
    async def run_test(self, name: str, test_func):
        """Run a single test with timing and error handling"""
        start_time = datetime.utcnow()
        try:
            await test_func()
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.log_test(name, True, duration)
            return True
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.log_test(name, False, duration, str(e))
            return False
    
    # ========================================================================
    # HEALTH CHECK TESTS
    # ========================================================================
    
    async def test_health_check(self):
        """Test system health endpoint"""
        response = await self.client.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_api_health(self):
        """Test API health endpoint"""
        response = await self.client.get(f"{self.base_url}/api/health")
        assert response.status_code == 200
    
    # ========================================================================
    # AUTHENTICATION TESTS
    # ========================================================================
    
    async def test_register_user(self):
        """Test user registration"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": "Test User",
                "role": "dispatcher"
            }
        )
        # May already exist, accept both 201 and 400
        assert response.status_code in [201, 400]
    
    async def test_login(self):
        """Test user login and obtain token"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data["data"]
        self.access_token = data["data"]["access_token"]
    
    async def test_get_current_user(self):
        """Test get current user profile"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/auth/me",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == TEST_EMAIL
    
    # ========================================================================
    # INCIDENT WORKFLOW TESTS
    # ========================================================================
    
    async def test_create_incident(self):
        """Test incident creation"""
        response = await self.client.post(
            f"{self.base_url}/api/v1/incidents",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "type": "medical_emergency",
                "severity": "high",
                "description": "Test incident - chest pain",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "reporter_name": "Test Reporter",
                "reporter_phone": "+15551234567"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data["data"]
        self.test_incident_id = data["data"]["id"]
    
    async def test_get_incident(self):
        """Test get incident by ID"""
        assert self.test_incident_id is not None
        response = await self.client.get(
            f"{self.base_url}/api/v1/incidents/{self.test_incident_id}",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == self.test_incident_id
    
    async def test_list_incidents(self):
        """Test list all incidents"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/incidents",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
    
    async def test_process_incident(self):
        """Test incident processing (triage, analysis)"""
        assert self.test_incident_id is not None
        response = await self.client.post(
            f"{self.base_url}/api/v1/incidents/{self.test_incident_id}/process",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        # May already be processed
        assert response.status_code in [200, 400]
    
    async def test_update_incident_status(self):
        """Test update incident status"""
        assert self.test_incident_id is not None
        response = await self.client.patch(
            f"{self.base_url}/api/v1/incidents/{self.test_incident_id}/status",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"status": "in_progress"}
        )
        assert response.status_code == 200
    
    # ========================================================================
    # HOSPITAL TESTS
    # ========================================================================
    
    async def test_list_hospitals(self):
        """Test list all hospitals"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/hospitals",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)
    
    async def test_nearby_hospitals(self):
        """Test find nearby hospitals"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/hospitals/nearby",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={
                "latitude": 37.7749,
                "longitude": -122.4194,
                "radius": 10
            }
        )
        assert response.status_code == 200
    
    async def test_rank_hospitals(self):
        """Test rank hospitals for incident"""
        assert self.test_incident_id is not None
        response = await self.client.post(
            f"{self.base_url}/api/v1/hospitals/rank",
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={
                "incident_id": self.test_incident_id,
                "max_results": 5
            }
        )
        assert response.status_code == 200
    
    # ========================================================================
    # AMBULANCE TESTS
    # ========================================================================
    
    async def test_list_ambulances(self):
        """Test list all ambulances"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/ambulances",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        if len(data["data"]) > 0:
            self.test_ambulance_id = data["data"][0]["id"]
    
    async def test_nearest_ambulances(self):
        """Test find nearest available ambulances"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/ambulances/nearest",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={
                "latitude": 37.7749,
                "longitude": -122.4194,
                "limit": 5
            }
        )
        assert response.status_code == 200
    
    async def test_update_ambulance_location(self):
        """Test update ambulance location"""
        if self.test_ambulance_id:
            response = await self.client.patch(
                f"{self.base_url}/api/v1/ambulances/{self.test_ambulance_id}/location",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={
                    "latitude": 37.7750,
                    "longitude": -122.4195
                }
            )
            assert response.status_code in [200, 404]
    
    async def test_update_ambulance_status(self):
        """Test update ambulance status"""
        if self.test_ambulance_id:
            response = await self.client.patch(
                f"{self.base_url}/api/v1/ambulances/{self.test_ambulance_id}/status",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={"status": "available"}
            )
            assert response.status_code in [200, 404]
    
    # ========================================================================
    # DASHBOARD TESTS
    # ========================================================================
    
    async def test_dashboard_stats(self):
        """Test dashboard statistics"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/dashboard/stats",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    async def test_active_incidents(self):
        """Test get active incidents"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/dashboard/active-incidents",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
    
    async def test_agent_status(self):
        """Test agent system status"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/dashboard/agent-status",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
    
    # ========================================================================
    # RESOURCE ALLOCATION TESTS
    # ========================================================================
    
    async def test_hotspots_prediction(self):
        """Test hotspot prediction"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/resource-allocation/hotspots",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={"hours_ahead": 6, "grid_size": 30}
        )
        assert response.status_code == 200
        data = response.json()
        assert "hotspots" in data["data"]
    
    async def test_demand_forecast(self):
        """Test demand forecasting"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/resource-allocation/demand-forecast",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={"hours_ahead": 24}
        )
        assert response.status_code == 200
        data = response.json()
        assert "forecasts" in data["data"]
    
    async def test_ambulance_positioning(self):
        """Test ambulance positioning recommendations"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/resource-allocation/ambulance-positioning",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={"hours_ahead": 6}
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data["data"]
    
    async def test_coverage_gaps(self):
        """Test coverage gap detection"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/resource-allocation/coverage-gaps",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={"target_response_time": 8}
        )
        assert response.status_code == 200
        data = response.json()
        assert "coverage_gaps" in data["data"]
    
    async def test_resource_heatmap(self):
        """Test heatmap generation"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/resource-allocation/heatmap",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={"metric": "risk"}
        )
        assert response.status_code == 200
    
    async def test_optimization_summary(self):
        """Test optimization summary"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/resource-allocation/optimization-summary",
            headers={"Authorization": f"Bearer {self.access_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "hotspots" in data["data"]
        assert "demand" in data["data"]
        assert "fleet" in data["data"]
    
    async def test_hospital_capacity_forecast(self):
        """Test hospital capacity forecasting"""
        response = await self.client.get(
            f"{self.base_url}/api/v1/resource-allocation/hospital-capacity-forecast",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={"hours_ahead": 12}
        )
        assert response.status_code == 200
    
    # ========================================================================
    # RUN ALL TESTS
    # ========================================================================
    
    async def run_all_tests(self):
        """Run complete test suite"""
        self.log(f"\n{Colors.BOLD}{'='*70}", Colors.BLUE)
        self.log(f"ARIA PLATFORM - COMPREHENSIVE INTEGRATION TESTS", Colors.BLUE)
        self.log(f"{'='*70}{Colors.RESET}\n", Colors.BLUE)
        
        self.log(f"Testing API: {self.base_url}\n", Colors.YELLOW)
        
        # Health Checks
        self.log(f"{Colors.BOLD}[1] HEALTH CHECKS{Colors.RESET}")
        await self.run_test("System health check", self.test_health_check)
        await self.run_test("API health check", self.test_api_health)
        
        # Authentication
        self.log(f"\n{Colors.BOLD}[2] AUTHENTICATION{Colors.RESET}")
        await self.run_test("User registration", self.test_register_user)
        await self.run_test("User login", self.test_login)
        await self.run_test("Get current user", self.test_get_current_user)
        
        # Incident Workflow
        self.log(f"\n{Colors.BOLD}[3] INCIDENT WORKFLOW{Colors.RESET}")
        await self.run_test("Create incident", self.test_create_incident)
        await self.run_test("Get incident by ID", self.test_get_incident)
        await self.run_test("List incidents", self.test_list_incidents)
        await self.run_test("Process incident", self.test_process_incident)
        await self.run_test("Update incident status", self.test_update_incident_status)
        
        # Hospitals
        self.log(f"\n{Colors.BOLD}[4] HOSPITAL INTEGRATION{Colors.RESET}")
        await self.run_test("List hospitals", self.test_list_hospitals)
        await self.run_test("Find nearby hospitals", self.test_nearby_hospitals)
        await self.run_test("Rank hospitals", self.test_rank_hospitals)
        
        # Ambulances
        self.log(f"\n{Colors.BOLD}[5] AMBULANCE MANAGEMENT{Colors.RESET}")
        await self.run_test("List ambulances", self.test_list_ambulances)
        await self.run_test("Find nearest ambulances", self.test_nearest_ambulances)
        await self.run_test("Update ambulance location", self.test_update_ambulance_location)
        await self.run_test("Update ambulance status", self.test_update_ambulance_status)
        
        # Dashboard
        self.log(f"\n{Colors.BOLD}[6] DASHBOARD{Colors.RESET}")
        await self.run_test("Dashboard statistics", self.test_dashboard_stats)
        await self.run_test("Active incidents", self.test_active_incidents)
        await self.run_test("Agent status", self.test_agent_status)
        
        # Resource Allocation
        self.log(f"\n{Colors.BOLD}[7] RESOURCE ALLOCATION (ML){Colors.RESET}")
        await self.run_test("Hotspot prediction", self.test_hotspots_prediction)
        await self.run_test("Demand forecast", self.test_demand_forecast)
        await self.run_test("Ambulance positioning", self.test_ambulance_positioning)
        await self.run_test("Coverage gap detection", self.test_coverage_gaps)
        await self.run_test("Resource heatmap", self.test_resource_heatmap)
        await self.run_test("Optimization summary", self.test_optimization_summary)
        await self.run_test("Hospital capacity forecast", self.test_hospital_capacity_forecast)
        
        # Print Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        self.log(f"\n{Colors.BOLD}{'='*70}", Colors.BLUE)
        self.log(f"TEST SUMMARY", Colors.BLUE)
        self.log(f"{'='*70}{Colors.RESET}\n", Colors.BLUE)
        
        pass_rate = (self.results["passed"] / self.results["total"] * 100) if self.results["total"] > 0 else 0
        
        self.log(f"Total Tests:  {self.results['total']}")
        self.log(f"Passed:       {Colors.GREEN}{self.results['passed']}{Colors.RESET}")
        self.log(f"Failed:       {Colors.RED}{self.results['failed']}{Colors.RESET}")
        self.log(f"Skipped:      {Colors.YELLOW}{self.results['skipped']}{Colors.RESET}")
        self.log(f"Pass Rate:    {Colors.GREEN if pass_rate >= 90 else Colors.YELLOW}{pass_rate:.1f}%{Colors.RESET}")
        
        if self.results["failed"] > 0:
            self.log(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
            for test in self.results["tests"]:
                if not test["passed"]:
                    self.log(f"  • {test['name']}: {test['error']}", Colors.RED)
        
        self.log(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}\n", Colors.BLUE)
        
        # Save results to file
        with open("integration_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        self.log(f"Results saved to: integration_test_results.json\n")


async def main():
    """Main entry point"""
    async with IntegrationTestRunner() as runner:
        await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
