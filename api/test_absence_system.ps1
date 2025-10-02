# PowerShell script to test absence management system
Write-Host "🧪 Starting Absence Management Testing" -ForegroundColor Cyan
Write-Host "=" * 50

# Change to API directory
Set-Location "c:\Users\pc\universety_app\api"

# Start server in background
Write-Host "🚀 Starting FastAPI server..." -ForegroundColor Yellow
$serverJob = Start-Job -ScriptBlock {
    Set-Location "c:\Users\pc\universety_app\api"
    python run_server.py
}

# Wait for server to start
Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if server is healthy
Write-Host "🔍 Checking server health..." -ForegroundColor Yellow
python check_absence_endpoints.py

# Run absence management tests
Write-Host "`n🧪 Running absence management tests..." -ForegroundColor Cyan
python test_absence_management.py

# Stop the server
Write-Host "`n🛑 Stopping server..." -ForegroundColor Red
Stop-Job $serverJob
Remove-Job $serverJob

Write-Host "`n✅ Testing completed!" -ForegroundColor Green