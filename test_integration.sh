#!/bin/bash

# ARIA Platform Integration Test Script
# Quick API endpoint testing with curl

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_BASE="${API_BASE_URL:-http://localhost:8000}"
TEST_EMAIL="test@aria.com"
TEST_PASSWORD="TestPass123!"
ACCESS_TOKEN=""
INCIDENT_ID=""

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED_TESTS++))
    ((TOTAL_TESTS++))
}

error() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED_TESTS++))
    ((TOTAL_TESTS++))
}

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_code="${5:-200}"
    
    echo -n "Testing: $name... "
    
    if [ "$method" = "GET" ]; then
        if [ -z "$ACCESS_TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE$endpoint" \
                -H "Authorization: Bearer $ACCESS_TOKEN")
        fi
    else
        if [ -z "$ACCESS_TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_BASE$endpoint" \
                -H "Content-Type: application/json" \
                -d "$data")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_BASE$endpoint" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $ACCESS_TOKEN" \
                -d "$data")
        fi
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_code" ]; then
        success "$name"
        echo "$body"
    else
        error "$name (Expected $expected_code, got $http_code)"
        echo "$body"
    fi
    
    echo ""
}

# Banner
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   ARIA PLATFORM - INTEGRATION TEST SUITE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
log "Testing API: $API_BASE"
echo ""

# ============================================================================
# HEALTH CHECKS
# ============================================================================
echo -e "${YELLOW}[1] HEALTH CHECKS${NC}"
echo "----------------------------------------"

test_endpoint "System health" "GET" "/health" "" "200"
test_endpoint "API health" "GET" "/api/health" "" "200"

# ============================================================================
# AUTHENTICATION
# ============================================================================
echo -e "${YELLOW}[2] AUTHENTICATION${NC}"
echo "----------------------------------------"

# Register (may fail if user exists, that's ok)
test_endpoint "User registration" "POST" "/api/v1/auth/register" \
    "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"Test User\",\"role\":\"dispatcher\"}" \
    "201"

# Login
log "Logging in..."
login_response=$(curl -s -X POST "$API_BASE/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

ACCESS_TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$ACCESS_TOKEN" ]; then
    success "User login - Token obtained"
    echo ""
else
    error "User login - Failed to obtain token"
    echo "Response: $login_response"
    echo ""
    exit 1
fi

test_endpoint "Get current user" "GET" "/api/v1/auth/me" "" "200"

# ============================================================================
# INCIDENT WORKFLOW
# ============================================================================
echo -e "${YELLOW}[3] INCIDENT WORKFLOW${NC}"
echo "----------------------------------------"

# Create incident
log "Creating test incident..."
incident_response=$(curl -s -X POST "$API_BASE/api/v1/incidents" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -d '{
        "type":"medical_emergency",
        "severity":"high",
        "description":"Test incident - integration test",
        "latitude":37.7749,
        "longitude":-122.4194,
        "reporter_name":"Test Reporter",
        "reporter_phone":"+15551234567"
    }')

INCIDENT_ID=$(echo "$incident_response" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -n "$INCIDENT_ID" ]; then
    success "Create incident - ID: $INCIDENT_ID"
    echo ""
else
    error "Create incident - Failed to get incident ID"
    echo "$incident_response"
    echo ""
fi

test_endpoint "Get incident" "GET" "/api/v1/incidents/$INCIDENT_ID" "" "200"
test_endpoint "List incidents" "GET" "/api/v1/incidents" "" "200"

# ============================================================================
# HOSPITALS
# ============================================================================
echo -e "${YELLOW}[4] HOSPITAL INTEGRATION${NC}"
echo "----------------------------------------"

test_endpoint "List hospitals" "GET" "/api/v1/hospitals" "" "200"
test_endpoint "Nearby hospitals" "GET" "/api/v1/hospitals/nearby?latitude=37.7749&longitude=-122.4194&radius=10" "" "200"

if [ -n "$INCIDENT_ID" ]; then
    test_endpoint "Rank hospitals" "POST" "/api/v1/hospitals/rank" \
        "{\"incident_id\":$INCIDENT_ID,\"max_results\":5}" "200"
fi

# ============================================================================
# AMBULANCES
# ============================================================================
echo -e "${YELLOW}[5] AMBULANCE MANAGEMENT${NC}"
echo "----------------------------------------"

test_endpoint "List ambulances" "GET" "/api/v1/ambulances" "" "200"
test_endpoint "Nearest ambulances" "GET" "/api/v1/ambulances/nearest?latitude=37.7749&longitude=-122.4194&limit=5" "" "200"

# ============================================================================
# DASHBOARD
# ============================================================================
echo -e "${YELLOW}[6] DASHBOARD${NC}"
echo "----------------------------------------"

test_endpoint "Dashboard stats" "GET" "/api/v1/dashboard/stats" "" "200"
test_endpoint "Active incidents" "GET" "/api/v1/dashboard/active-incidents" "" "200"
test_endpoint "Agent status" "GET" "/api/v1/dashboard/agent-status" "" "200"

# ============================================================================
# RESOURCE ALLOCATION
# ============================================================================
echo -e "${YELLOW}[7] RESOURCE ALLOCATION (ML)${NC}"
echo "----------------------------------------"

test_endpoint "Hotspot prediction" "GET" "/api/v1/resource-allocation/hotspots?hours_ahead=6&grid_size=30" "" "200"
test_endpoint "Demand forecast" "GET" "/api/v1/resource-allocation/demand-forecast?hours_ahead=24" "" "200"
test_endpoint "Ambulance positioning" "GET" "/api/v1/resource-allocation/ambulance-positioning?hours_ahead=6" "" "200"
test_endpoint "Coverage gaps" "GET" "/api/v1/resource-allocation/coverage-gaps?target_response_time=8" "" "200"
test_endpoint "Resource heatmap" "GET" "/api/v1/resource-allocation/heatmap?metric=risk" "" "200"
test_endpoint "Optimization summary" "GET" "/api/v1/resource-allocation/optimization-summary" "" "200"
test_endpoint "Hospital capacity forecast" "GET" "/api/v1/resource-allocation/hospital-capacity-forecast?hours_ahead=12" "" "200"

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   TEST SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo "Total Tests:  $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed:       ${RED}$FAILED_TESTS${NC}"

PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")
echo -e "Pass Rate:    ${GREEN}$PASS_RATE%${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    echo ""
    exit 1
fi
