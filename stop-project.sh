#!/bin/bash

# ARIA Emergency Response System - Stop Script
# This script stops all running services

set -e  # Exit on error

echo "🛑 Stopping ARIA Emergency Response System..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Stop backend
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID
        rm logs/backend.pid
        echo -e "${GREEN}✅ Backend stopped${NC}"
    else
        echo -e "${YELLOW}Backend process not found${NC}"
        rm logs/backend.pid
    fi
else
    echo -e "${YELLOW}No backend PID file found${NC}"
fi

# Stop frontend
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID
        rm logs/frontend.pid
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    else
        echo -e "${YELLOW}Frontend process not found${NC}"
        rm logs/frontend.pid
    fi
else
    echo -e "${YELLOW}No frontend PID file found${NC}"
fi

# Stop any remaining node/uvicorn processes (be careful!)
echo -e "${YELLOW}Stopping any remaining processes...${NC}"
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "react-scripts start" 2>/dev/null || true

# Stop Docker containers
echo -e "${YELLOW}Stopping Docker containers...${NC}"
docker-compose down

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ ARIA System Stopped Successfully! ✅${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}To start again, run:${NC} ./start-project.sh"
echo ""
