@echo off
echo Running migration to email-based authentication...
echo.

cd /d "%~dp0"

echo Step 1: Running database migration...
python migrate_to_email_auth.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Migration completed successfully!
    echo.
    echo Updated Test Credentials:
    echo   Department Head: john.doe@university.com / depthead123
    echo   Teacher: teacher@university.com / teacher123  
    echo   Student: student@university.edu / student123
    echo.
    echo You can now use email addresses for authentication!
) else (
    echo.
    echo ❌ Migration failed. Please check the error messages above.
)

pause