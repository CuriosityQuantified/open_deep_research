#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Open Deep Research UI (Production Mode)...${NC}"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${RED}🛑 Shutting down server...${NC}"
    # Kill all child processes
    pkill -P $$
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Please run 'uv venv' and 'uv sync' first."
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "$SCRIPT_DIR/frontend/node_modules" ]; then
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
    cd "$SCRIPT_DIR/frontend"
    npm install
    cd "$SCRIPT_DIR"
fi

# Always build frontend for production
echo -e "${BLUE}🔨 Building frontend for production...${NC}"
cd "$SCRIPT_DIR/frontend"
npm run build

if [ ! -d "$SCRIPT_DIR/frontend/dist" ]; then
    echo -e "${RED}❌ Frontend build failed!${NC}"
    exit 1
fi

# Start backend server (which serves the frontend)
echo -e "${GREEN}✅ Starting server on http://localhost:8000${NC}"
cd "$SCRIPT_DIR/backend"
source "$PROJECT_ROOT/.venv/bin/activate"
python server.py &
BACKEND_PID=$!

# Wait for backend to start
echo -e "${BLUE}⏳ Waiting for server to start...${NC}"
sleep 3

# Check if backend is running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo -e "${RED}❌ Server failed to start!${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 Open Deep Research UI is running!${NC}"
echo -e "${BLUE}🌐 Web UI: http://localhost:8000${NC}"
echo -e "${BLUE}📊 API Docs: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}📌 Note: Frontend is served directly from the backend (production mode)${NC}"
echo ""
echo -e "Press ${RED}Ctrl+C${NC} to stop the server"

# Wait for process to exit
wait $BACKEND_PID