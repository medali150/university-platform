@echo off
echo ==================================================
echo University Management API Test Runner
echo ==================================================
echo.
echo Starting API tests...
echo.

python test_modular_api.py

echo.
echo ==================================================
echo Test completed!
echo.
echo To access API documentation:
echo - Swagger UI: http://127.0.0.1:8000/docs
echo - ReDoc: http://127.0.0.1:8000/redoc
echo.
echo Check swagger_test_examples.md for manual testing examples
echo ==================================================
pause