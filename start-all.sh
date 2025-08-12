#!/bin/bash

echo "🚀 Starting Internal Assistant Platform..."
echo ""

# Check if setup has been run
if [ ! -f ".env" ]; then
    echo "❌ Environment file not found. Please run setup first:"
    echo "   ./setup-yarn.sh"
    exit 1
fi

# Start backend in background
echo "🐍 Starting backend server..."
./start-backend.sh &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
./start-frontend.sh &
FRONTEND_PID=$!

echo ""
echo "🎉 Both servers are starting..."
echo "🌐 Frontend: http://localhost:3000"
echo "🌐 Backend:  http://localhost:5000"
echo ""
echo "🛑 Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
