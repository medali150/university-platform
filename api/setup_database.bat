@echo off
REM Setup database with French schema
echo 🚀 Setting up University Platform Database with French Schema...
echo.

echo 📝 Validating Prisma schema...
npx prisma validate
if %errorlevel% neq 0 (
    echo ❌ Schema validation failed!
    pause
    exit /b 1
)

echo ✅ Schema is valid!
echo.

echo 🔄 Resetting database and applying schema...
python reset_and_migrate.py

echo.
echo 🎉 Database setup complete!
echo You can now start your FastAPI server and test the frontend.
echo.
pause