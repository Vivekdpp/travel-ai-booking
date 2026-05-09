#!/bin/bash
# Quick start script for TravelAI Booking System

set -e

echo "=================================="
echo "🌍 TravelAI Booking System"
echo "Quick Start Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "📋 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.10+${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found${NC}"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ PostgreSQL not found locally${NC}"
    echo "   Install: https://www.postgresql.org/download/"
    echo "   Or use Docker: docker-compose up -d"
fi

echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

echo -e "${GREEN}✓ Virtual environment created${NC}"

# Activate venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi

echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo ""
echo "📚 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓ Dependencies installed${NC}"

echo ""
echo "⚙️  Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env from template${NC}"
    echo -e "${YELLOW}⚠ Edit .env and add your ANTHROPIC_API_KEY${NC}"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

echo ""
echo "🐳 Starting Docker services..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d 2>/dev/null
    echo -e "${GREEN}✓ Docker services started${NC}"
    sleep 3
else
    echo -e "${YELLOW}⚠ Docker not found. Make sure PostgreSQL is running!${NC}"
fi

echo ""
echo "🗄️  Initializing database..."
python -m scripts.setup_db
echo -e "${GREEN}✓ Database initialized${NC}"

echo ""
echo "=================================="
echo -e "${GREEN}✓ Setup complete!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Start the server: python -m api.main"
echo "3. Run demo: python scripts/demo.py"
echo "4. Visit: http://localhost:8000/docs"
echo ""
echo "Happy coding! 🚀"
