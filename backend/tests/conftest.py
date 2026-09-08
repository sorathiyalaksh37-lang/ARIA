"""
Pytest Configuration and Fixtures
Provides shared fixtures for all tests
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.models.incident import Incident
from app.models.hospital import Hospital
from app.models.ambulance import Ambulance
from app.core.security import get_password_hash, create_access_token


# Test Database URL
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def db() -> Generator:
    """Create test database session."""
    Base.metadata.create_all(bind=test_engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Create test client with database session override."""
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
def test_user(db) -> User:
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpass123"),
        full_name="Test User",
        role="coordinator",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db) -> User:
    """Create admin user."""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpass123"),
        full_name="Admin User",
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_token(test_user) -> str:
    """Create test JWT token."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture
def admin_token(admin_user) -> str:
    """Create admin JWT token."""
    return create_access_token(data={"sub": admin_user.email})


@pytest.fixture
def auth_headers(test_token) -> dict:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def admin_headers(admin_token) -> dict:
    """Create admin authorization headers."""
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================================================
# DATA FIXTURES
# ============================================================================

@pytest.fixture
def test_incident(db, test_user) -> Incident:
    """Create test incident."""
    incident = Incident(
        title="Test Road Accident",
        description="Multiple vehicle collision on Highway 101",
        incident_type="road_accident",
        severity="high",
        status="pending",
        latitude=37.7749,
        longitude=-122.4194,
        location="Highway 101, San Francisco",
        victim_count=3,
        caller_phone="+1234567890",
        created_by_id=test_user.id,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@pytest.fixture
def test_hospital(db) -> Hospital:
    """Create test hospital."""
    hospital = Hospital(
        name="Test General Hospital",
        address="123 Medical Center Dr, San Francisco, CA 94143",
        latitude=37.7625,
        longitude=-122.4598,
        phone="+14155551234",
        total_beds=200,
        available_beds=50,
        icu_beds=20,
        available_icu_beds=5,
        specialties=["trauma", "cardiology", "orthopedic"],
        is_active=True,
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


@pytest.fixture
def test_ambulance(db) -> Ambulance:
    """Create test ambulance."""
    ambulance = Ambulance(
        vehicle_number="AMB-001",
        ambulance_type="ALS",
        current_latitude=37.7749,
        current_longitude=-122.4194,
        status="available",
        is_active=True,
    )
    db.add(ambulance)
    db.commit()
    db.refresh(ambulance)
    return ambulance


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "incident_type": "road_accident",
        "severity": "high",
        "victim_count": 3,
        "injuries": ["head trauma", "fracture", "bleeding"],
        "location_mentioned": "Highway 101",
        "urgency_level": "emergency",
    }


@pytest.fixture
def mock_google_maps_response():
    """Mock Google Maps API response."""
    return {
        "lat": 37.7749,
        "lng": -122.4194,
        "formatted_address": "Market St, San Francisco, CA 94103, USA",
        "place_id": "ChIJIQBpAG2ahYAR_6128GcTUEo",
    }


@pytest.fixture
def mock_twilio_response():
    """Mock Twilio SMS response."""
    return {
        "sid": "SM1234567890abcdef1234567890abcdef",
        "status": "sent",
        "to": "+1234567890",
        "from": "+0987654321",
    }


# ============================================================================
# ASYNC FIXTURES
# ============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# CLEANUP
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup after each test."""
    yield
    # Add any cleanup code here
