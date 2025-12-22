#!/bin/bash

# SmartGrow - Mobile Access Startup Script
# This script starts both backend and frontend for network access

echo "🌱 Starting SmartGrow for Mobile Access"
echo "========================================"

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "📱 Your local IP: $LOCAL_IP"
echo ""

# Start Backend (bind to 0.0.0.0 to accept all connections)
echo "🔧 Starting Backend API on $LOCAL_IP:5000..."
cd /home/paul/precisionfarming
source venv/bin/activate

# Kill any existing Flask processes
pkill -f "flask run" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true

# Start backend in background
cd backend
export FLASK_APP=app
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000 &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Access at: http://$LOCAL_IP:5000"
echo ""

# Wait for backend to start
sleep 3

# Start Frontend (bind to 0.0.0.0 for network access)
echo "🎨 Starting Frontend on $LOCAL_IP:5174..."
cd ../frontend

# Kill any existing Vite processes
pkill -f "vite" 2>/dev/null || true

# Start frontend in background
npm run dev -- --host 0.0.0.0 --port 5174 &
FRONTEND_PID=$!

echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo ""

# Wait for services to fully start
sleep 5

echo "========================================"
echo "✅ SmartGrow is running!"
echo "========================================"
echo ""
echo "📱 Mobile Access URLs:"
echo "   Frontend: http://$LOCAL_IP:5174"
echo "   Backend:  http://$LOCAL_IP:5000"
echo ""
echo "💻 Desktop Access URLs:"
echo "   Frontend: http://localhost:5174"
echo "   Backend:  http://localhost:5000"
echo ""
echo "📋 Instructions:"
echo "1. Make sure your mobile is on the same WiFi network"
echo "2. On your mobile browser, go to: http://$LOCAL_IP:5174"
echo "3. Test the app!"
echo ""
echo "⚠️  If it doesn't work, check your firewall:"
echo "   sudo ufw allow 5000"
echo "   sudo ufw allow 5174"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Keep script running
wait
