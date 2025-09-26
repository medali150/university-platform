@echo off
echo Testing University Management API
echo =====================================

echo.
echo 1. Testing API Status...
curl -X GET "http://localhost:8000/" -H "accept: application/json"

echo.
echo.
echo 2. Testing Health Check...
curl -X GET "http://localhost:8000/health" -H "accept: application/json"

echo.
echo.
echo 3. Creating a Department...
curl -X POST "http://localhost:8000/departments" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"name\":\"Mathematics\"}"

echo.
echo.
echo 4. Getting All Departments...
curl -X GET "http://localhost:8000/departments" -H "accept: application/json"

echo.
echo.
echo 5. Creating a User...
curl -X POST "http://localhost:8000/users" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"firstName\":\"Alice\",\"lastName\":\"Smith\",\"email\":\"alice.smith@uni.edu\",\"login\":\"alicesmith\",\"password\":\"password123\",\"role\":\"TEACHER\"}"

echo.
echo.
echo 6. Getting All Users...
curl -X GET "http://localhost:8000/users" -H "accept: application/json"

echo.
echo.
echo Testing Complete!
echo You can also visit http://localhost:8000/docs for interactive API documentation
pause