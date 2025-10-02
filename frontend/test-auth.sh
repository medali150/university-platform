#!/usr/bin/env bash
# Test script for the new authentication system

echo "🚀 Testing University Platform Authentication System"
echo "=================================================="

echo ""
echo "🔧 1. Starting FastAPI Server..."
cd ../api
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!
echo "   API Server started with PID: $API_PID"

echo ""
echo "🔧 2. Starting Next.js Frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "   Frontend started with PID: $FRONTEND_PID"

echo ""
echo "⏳ Waiting for servers to start..."
sleep 10

echo ""
echo "🎯 3. Test URLs:"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Login: http://localhost:3000/login"
echo "   Register: http://localhost:3000/register"

echo ""
echo "📧 4. Test Credentials:"
echo "   Admin: admin@university.com / admin123"
echo "   Teacher: jean.dupont@university.com / teacher123"
echo "   Student: marie.martin@student.university.edu / student123"
echo "   Dept Head: pierre.leclerc@university.com / depthead123"

echo ""
echo "🛑 To stop servers, run:"
echo "   kill $API_PID $FRONTEND_PID"

echo ""
echo "✅ Setup complete! Open http://localhost:3000 to test the application."

# Keep script running
wait