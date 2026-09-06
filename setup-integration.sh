#!/bin/bash

# ARIA Integration Setup Script
# This script sets up all services for the complete integration

echo "🚀 ARIA Emergency Response System - Integration Setup"
echo "======================================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running from project root
if [ ! -f "PROJECT-STATUS.md" ]; then
    echo -e "${RED}❌ Error: Please run this script from the project root directory${NC}"
    exit 1
fi

echo ""
echo "📦 Step 1: Installing Backend Dependencies..."
echo "----------------------------------------------"
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install requirements
echo "Installing Python packages..."
pip install -r requirements.txt
pip install -r requirements-integration.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install backend dependencies${NC}"
    exit 1
fi

cd ..

echo ""
echo "📦 Step 2: Installing Frontend Dependencies..."
echo "----------------------------------------------"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing Node packages..."
    npm install
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        echo -e "${RED}❌ Failed to install frontend dependencies${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Frontend dependencies already installed${NC}"
fi

cd ..

echo ""
echo "🔧 Step 3: Setting up Environment Files..."
echo "----------------------------------------------"

# Backend environment
if [ ! -f "backend/.env" ]; then
    echo "Creating backend .env file..."
    cp .env.development backend/.env
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your API keys${NC}"
else
    echo -e "${GREEN}✅ Backend .env already exists${NC}"
fi

# Frontend environment
if [ ! -f "frontend/.env" ]; then
    echo "Creating frontend .env file..."
    cp frontend/.env.development frontend/.env
    echo -e "${YELLOW}⚠️  Please edit frontend/.env if needed${NC}"
else
    echo -e "${GREEN}✅ Frontend .env already exists${NC}"
fi

echo ""
echo "📁 Step 4: Creating Required Directories..."
echo "----------------------------------------------"

# Create logs directory
mkdir -p backend/logs
mkdir -p models
mkdir -p data/uploads

echo -e "${GREEN}✅ Directories created${NC}"

echo ""
echo "🗄️  Step 5: Database Setup..."
echo "----------------------------------------------"

echo -e "${YELLOW}⚠️  Please ensure PostgreSQL is running with PostGIS extension${NC}"
echo "To initialize the database, run:"
echo "  cd backend"
echo "  python -c 'from app.core.database import init_db; import asyncio; asyncio.run(init_db())'"

echo ""
echo "✅ Setup Complete!"
echo "======================================================"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure API Keys:"
echo "   - Edit backend/.env"
echo "   - Add OPENAI_API_KEY"
echo "   - Add GOOGLE_MAPS_API_KEY"
echo "   - Add TWILIO credentials"
echo "   - Add SENDGRID_API_KEY"
echo ""
echo "2. Start PostgreSQL:"
echo "   brew services start postgresql@14  # macOS"
echo "   sudo systemctl start postgresql    # Linux"
echo ""
echo "3. Start Redis:"
echo "   brew services start redis          # macOS"
echo "   sudo systemctl start redis         # Linux"
echo ""
echo "4. Start Backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo ""
echo "5. Start Frontend (in another terminal):"
echo "   cd frontend"
echo "   npm start"
echo ""
echo "6. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📚 For more information, see COMPLETE-INTEGRATION-GUIDE.md"
echo ""
