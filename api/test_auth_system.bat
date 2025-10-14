@echo off
echo Testing Authentication System Backend
echo =====================================
echo.

echo Testing Admin Login...
curl -X POST "http://localhost:8000/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"email\": \"admin@university.com\", \"password\": \"admin123\"}"
echo.
echo.

echo Testing Teacher Registration...
curl -X POST "http://localhost:8000/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"nom\": \"Test\", \"prenom\": \"Teacher\", \"email\": \"test.teacher@university.com\", \"password\": \"test123\", \"role\": \"TEACHER\", \"department_id\": \"dept1\"}"
echo.
echo.

echo Testing Student Registration...
curl -X POST "http://localhost:8000/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"nom\": \"Test\", \"prenom\": \"Student\", \"email\": \"test.student@university.com\", \"password\": \"test123\", \"role\": \"STUDENT\"}"
echo.
echo.

echo Getting Departments...
curl -X GET "http://localhost:8000/auth/departments"
echo.
echo.

echo Authentication system testing complete!
pause