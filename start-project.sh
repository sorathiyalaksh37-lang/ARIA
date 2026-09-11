#!/bin/bash

# ARIA Emergency Response System - Startup Script
# This script starts all required services for local development

set -e  # Exit on error

echo "🚀 Starting ARIA Emergency Response System..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Starting Docker Desktop...${NC}"
    open -a Docker
    echo -e "${YELLOW}⏳ Waiting for Docker to start (30 seconds)...${NC}"
    sleep 30
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Start database and redis services
echo -e "${BLUE}📦 Starting PostgreSQL and Redis...${NC}"
docker-compose up -d postgres redis

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
sleep 10

# Check if services are running
if docker-compose ps | grep -q "aria-postgres.*Up"; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL failed to start${NC}"
    exit 1
fi

if docker-compose ps | grep -q "aria-redis.*Up"; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis failed to start${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}🔧 Setting up Python virtual environment...${NC}"

# Backend setup
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if alembic is set up)
if [ -d "alembic" ]; then
    echo -e "${YELLOW}Running database migrations...${NC}"
    alembic upgrade head
fi

echo -e "${GREEN}✅ Backend dependencies installed${NC}"
echo ""

# Start backend in background
echo -e "${BLUE}🚀 Starting FastAPI backend on http://localhost:8000${NC}"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
sleep 5

cd ..

echo ""
echo -e "${BLUE}🔧 Setting up Frontend...${NC}"

# Frontend setup
cd frontend

# Install dependencies if node_modules doesn't exist or package.json changed
if [ ! -d "node_modules" ] || [ package.json -nt node_modules ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
fi

echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
echo ""

# Start frontend in background
echo -e "${BLUE}🚀 Starting React frontend on http://localhost:3000${NC}"
nohup npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"

cd ..

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 ARIA System Started Successfully! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📍 Service URLs:${NC}"
echo -e "   🌐 Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "   🔧 Backend:   ${GREEN}http://localhost:8000${NC}"
echo -e "   📚 API Docs:  ${GREEN}http://localhost:8000/docs${NC}"
echo -e "   🗄️  PostgreSQL: ${GREEN}localhost:5432${NC}"
echo -e "   📦 Redis:     ${GREEN}localhost:6379${NC}"
echo ""
echo -e "${BLUE}📋 Process IDs:${NC}"
echo -e "   Backend PID:  $BACKEND_PID"
echo -e "   Frontend PID: $FRONTEND_PID"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo -e "   Backend:  tail -f logs/backend.log"
echo -e "   Frontend: tail -f logs/frontend.log"
echo ""
echo -e "${YELLOW}⚠️  To stop all services, run:${NC}"
echo -e "   ./stop-project.sh"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
