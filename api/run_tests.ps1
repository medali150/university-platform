Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "University Management API Test Runner" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting API tests..." -ForegroundColor Green
Write-Host ""

# Run the Python test script
python test_modular_api.py

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Test completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To access API documentation:" -ForegroundColor Yellow
Write-Host "- Swagger UI: " -NoNewline -ForegroundColor White
Write-Host "http://127.0.0.1:8000/docs" -ForegroundColor Blue
Write-Host "- ReDoc: " -NoNewline -ForegroundColor White  
Write-Host "http://127.0.0.1:8000/redoc" -ForegroundColor Blue
Write-Host ""
Write-Host "Check swagger_test_examples.md for manual testing examples" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Cyan

Read-Host "Press Enter to continue"