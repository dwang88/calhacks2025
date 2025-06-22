#!/bin/bash

# Website Testing Assistant Startup Script

echo "🚀 Starting Website Testing Assistant..."

# Check if .env file exists in backend
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found!"
    echo "Please create backend/.env with your API keys:"
    echo "ANTHROPIC_API_KEY=your_key_here"
    echo "GITHUB_TOKEN=your_token_here (optional)"
    echo "GITHUB_REPO=owner/repo (optional)"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $FASTMCP_PID $API_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start FastMCP server
echo "🔧 Starting FastMCP server..."
cd backend
python fastmcp_server.py &
FASTMCP_PID=$!
cd ..

# Wait a moment for FastMCP server to start
sleep 3

# Start API server
echo "🔧 Starting API server..."
cd backend
python api_server.py &
API_PID=$!
cd ..

# Wait a moment for API server to start
sleep 3

# Start frontend server
echo "🎨 Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ All servers are starting..."
echo "🔧 FastMCP Server: http://localhost:8001"
echo "🔧 API Server: http://localhost:8000"
echo "📱 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for all processes
wait $FASTMCP_PID $API_PID $FRONTEND_PID 