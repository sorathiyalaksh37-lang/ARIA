#!/bin/bash

# ARIA Platform - Service Health Check Script
# Checks all services and dependencies

set +e  # Don't exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL="${API_BASE_URL:-http://localhost:8000}"
FRONTEND_URL="http://localhost:3000"

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   ARIA PLATFORM - SERVICE HEALTH CHECK${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

check_service() {
    local name="$1"
    local command="$2"
    
    echo -n "Checking $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ OK${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

check_url() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"
    
    echo -n "Checking $name... "
    
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $http_code)"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code, expected $expected_code)"
        ((TESTS_FAILED++))
        return 1
    fi
}

# ============================================================================
# SYSTEM DEPENDENCIES
# ============================================================================
echo -e "${YELLOW}[1] SYSTEM DEPENDENCIES${NC}"
echo "----------------------------------------"

check_service "Python 3.9+" "python3 --version | grep -E 'Python 3\\.(9|10|11|12)'"
check_service "Node.js" "node --version"
check_service "npm" "npm --version"
check_service "PostgreSQL client" "psql --version"
check_service "Redis client" "redis-cli --version"
check_service "curl" "curl --version"

echo ""

# ============================================================================
# BACKEND SERVICES
# ============================================================================
echo -e "${YELLOW}[2] BACKEND SERVICES${NC}"
echo "----------------------------------------"

check_service "PostgreSQL server" "pg_isready"
check_service "Redis server" "redis-cli ping | grep -q PONG"

echo ""

# ============================================================================
# BACKEND API
# ============================================================================
echo -e "${YELLOW}[3] BACKEND API${NC}"
echo "----------------------------------------"

check_url "Backend health endpoint" "$API_URL/health" "200"
check_url "API health endpoint" "$API_URL/api/health" "200"
check_url "API docs (Swagger)" "$API_URL/docs" "200"

# Check if backend process is running
echo -n "Backend process... "
if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Not running${NC}"
    ((TESTS_FAILED++))
fi

echo ""

# ============================================================================
# FRONTEND
# ============================================================================
echo -e "${YELLOW}[4] FRONTEND${NC}"
echo "----------------------------------------"

# Check if frontend process is running
echo -n "Frontend process... "
if pgrep -f "react-scripts start" > /dev/null || pgrep -f "node.*react-scripts" > /dev/null; then
    echo -e "${GREEN}✓ Running${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠ Not running${NC}"
    ((TESTS_FAILED++))
fi

# Try to check frontend URL
if curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
    check_url "Frontend application" "$FRONTEND_URL" "200"
else
    echo -e "Frontend URL... ${YELLOW}⚠ Not accessible${NC}"
fi

echo ""

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================
echo -e "${YELLOW}[5] ENVIRONMENT CONFIGURATION${NC}"
echo "----------------------------------------"

# Check backend .env
echo -n "Backend .env file... "
if [ -f "backend/.env" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ Missing${NC} (Copy from .env.example)"
    ((TESTS_FAILED++))
fi

# Check frontend .env
echo -n "Frontend .env file... "
if [ -f "frontend/.env" ]; then
    echo -e "${GREEN}✓ Exists${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠ Missing${NC} (Optional, will use defaults)"
fi

# Check for required environment variables
echo -n "Database URL configured... "
if grep -q "DATABASE_URL=" backend/.env 2>/dev/null; then
    echo -e "${GREEN}✓ Yes${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ No${NC}"
    ((TESTS_FAILED++))
fi

echo -n "Secret key configured... "
if grep -q "SECRET_KEY=" backend/.env 2>/dev/null; then
    SECRET_KEY=$(grep "SECRET_KEY=" backend/.env | cut -d'=' -f2)
    if [ "$SECRET_KEY" != "your-super-secret-key-change-this-in-production" ]; then
        echo -e "${GREEN}✓ Custom key set${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ Using default (change in production!)${NC}"
    fi
else
    echo -e "${RED}✗ Not set${NC}"
    ((TESTS_FAILED++))
fi

echo ""

# ============================================================================
# EXTERNAL API KEYS
# ============================================================================
echo -e "${YELLOW}[6] EXTERNAL API KEYS${NC}"
echo "----------------------------------------"

check_api_key() {
    local name="$1"
    local env_var="$2"
    local pattern="$3"
    
    echo -n "$name... "
    
    if grep -q "$env_var=" backend/.env 2>/dev/null; then
        value=$(grep "$env_var=" backend/.env | cut -d'=' -f2)
        if [ -n "$value" ] && [[ "$value" =~ $pattern ]]; then
            echo -e "${GREEN}✓ Configured${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ Invalid format${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠ Not configured${NC}"
        return 1
    fi
}

check_api_key "OpenAI API Key" "OPENAI_API_KEY" "^sk-"
check_api_key "Google Maps API Key" "GOOGLE_MAPS_API_KEY" "^AIza"
check_api_key "Twilio Account SID" "TWILIO_ACCOUNT_SID" "^AC"
check_api_key "SendGrid API Key" "SENDGRID_API_KEY" "^SG\\."
check_api_key "OpenWeather API Key" "OPENWEATHER_API_KEY" "."

echo ""

# ============================================================================
# PYTHON DEPENDENCIES
# ============================================================================
echo -e "${YELLOW}[7] PYTHON DEPENDENCIES${NC}"
echo "----------------------------------------"

check_python_package() {
    local package="$1"
    echo -n "$package... "
    
    if python3 -c "import $package" 2>/dev/null; then
        version=$(python3 -c "import $package; print($package.__version__)" 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✓ Installed${NC} ($version)"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ Not installed${NC}"
        ((TESTS_FAILED++))
    fi
}

check_python_package "fastapi"
check_python_package "sqlalchemy"
check_python_package "pydantic"
check_python_package "openai"
check_python_package "httpx"

echo ""

# ============================================================================
# NODE DEPENDENCIES
# ============================================================================
echo -e "${YELLOW}[8] NODE DEPENDENCIES${NC}"
echo "----------------------------------------"

if [ -d "frontend/node_modules" ]; then
    echo -e "node_modules... ${GREEN}✓ Exists${NC}"
    ((TESTS_PASSED++))
    
    # Check key packages
    for package in react react-dom axios leaflet; do
        echo -n "$package... "
        if [ -d "frontend/node_modules/$package" ]; then
            echo -e "${GREEN}✓ Installed${NC}"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗ Not installed${NC}"
            ((TESTS_FAILED++))
        fi
    done
else
    echo -e "node_modules... ${RED}✗ Not found${NC} (Run: cd frontend && npm install)"
    ((TESTS_FAILED++))
fi

echo ""

# ============================================================================
# DATABASE STATUS
# ============================================================================
echo -e "${YELLOW}[9] DATABASE STATUS${NC}"
echo "----------------------------------------"

if [ -f "backend/.env" ]; then
    DATABASE_URL=$(grep "DATABASE_URL=" backend/.env | cut -d'=' -f2)
    
    if [ -n "$DATABASE_URL" ]; then
        # Test connection
        echo -n "Database connection... "
        if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Connected${NC}"
            ((TESTS_PASSED++))
            
            # Check tables
            echo -n "Database tables... "
            table_count=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'" 2>/dev/null | tr -d ' ')
            if [ -n "$table_count" ] && [ "$table_count" -gt 0 ]; then
                echo -e "${GREEN}✓ $table_count tables${NC}"
                ((TESTS_PASSED++))
            else
                echo -e "${YELLOW}⚠ No tables (Run migrations)${NC}"
            fi
        else
            echo -e "${RED}✗ Cannot connect${NC}"
            ((TESTS_FAILED++))
        fi
    else
        echo -e "Database URL... ${RED}✗ Not configured${NC}"
    fi
else
    echo -e "Configuration... ${RED}✗ .env file missing${NC}"
fi

echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($TESTS_PASSED/$TOTAL_TESTS)*100}")
else
    PASS_RATE=0
fi

echo "Total Checks: $TOTAL_TESTS"
echo -e "Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:       ${RED}$TESTS_FAILED${NC}"
echo -e "Success Rate: ${GREEN}$PASS_RATE%${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED!${NC}"
    echo -e "System is ready for development."
    echo ""
    exit 0
elif [ $TESTS_FAILED -le 3 ]; then
    echo -e "${YELLOW}⚠ MINOR ISSUES DETECTED${NC}"
    echo -e "System may function with limited features."
    echo ""
    exit 0
else
    echo -e "${RED}✗ SIGNIFICANT ISSUES DETECTED${NC}"
    echo -e "Please fix the failed checks before proceeding."
    echo ""
    echo "Quick fixes:"
    echo "  1. Start services: docker-compose up -d (if using Docker)"
    echo "  2. Install Python deps: cd backend && pip install -r requirements.txt"
    echo "  3. Install Node deps: cd frontend && npm install"
    echo "  4. Configure environment: cp backend/.env.example backend/.env"
    echo "  5. Run migrations: cd backend && alembic upgrade head"
    echo ""
    exit 1
fi
