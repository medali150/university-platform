# Restart Backend Server Script
# This script stops any running Python processes and restarts the backend

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  University App - Backend Server Restart" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop existing Python processes
Write-Host "Step 1: Stopping existing backend server..." -ForegroundColor Yellow
$processes = Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*universety_app*"}

if ($processes) {
    Write-Host "  Found $($processes.Count) Python process(es) to stop" -ForegroundColor Gray
    $processes | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Processes stopped" -ForegroundColor Green
} else {
    Write-Host "  No existing processes found" -ForegroundColor Gray
}

Write-Host ""

# Step 2: Verify port 8000 is free
Write-Host "Step 2: Checking if port 8000 is available..." -ForegroundColor Yellow
$port = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($port) {
    Write-Host "  ⚠ Port 8000 is still in use, waiting..." -ForegroundColor Red
    Start-Sleep -Seconds 3
    
    # Force kill process using the port
    $processId = $port.OwningProcess
    if ($processId) {
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Freed port 8000" -ForegroundColor Green
    }
} else {
    Write-Host "  ✓ Port 8000 is available" -ForegroundColor Green
}

Write-Host ""

# Step 3: Start backend server
Write-Host "Step 3: Starting backend server..." -ForegroundColor Yellow
Write-Host "  Location: C:\Users\pc\universety_app\api" -ForegroundColor Gray
Write-Host "  Command: python run_server.py" -ForegroundColor Gray
Write-Host ""

Set-Location "C:\Users\pc\universety_app\api"

# Start the server in a new window
Start-Process -FilePath "c:\Users\pc\universety_app\.venv\Scripts\python.exe" `
              -ArgumentList "run_server.py" `
              -WorkingDirectory "C:\Users\pc\universety_app\api" `
              -WindowStyle Normal

Write-Host "  ✓ Server starting in new window..." -ForegroundColor Green
Write-Host ""

# Step 4: Wait for server to start
Write-Host "Step 4: Waiting for server to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 5: Test server
Write-Host "Step 5: Testing server health..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Server is healthy!" -ForegroundColor Green
    Write-Host "    Status: $($response.status)" -ForegroundColor Gray
    Write-Host "    Database: $($response.database)" -ForegroundColor Gray
    Write-Host "    Users: $($response.users_count)" -ForegroundColor Gray
} catch {
    Write-Host "  ⚠ Server not responding yet (may need more time)" -ForegroundColor Yellow
    Write-Host "    Check the new window for server status" -ForegroundColor Gray
}

Write-Host ""

# Step 6: Test room occupancy endpoint
Write-Host "Step 6: Testing room occupancy endpoint..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/room-occupancy/debug/rooms" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Room occupancy endpoint working!" -ForegroundColor Green
    Write-Host "    Success: $($response.success)" -ForegroundColor Gray
    Write-Host "    Rooms: $($response.data.Count)" -ForegroundColor Gray
    Write-Host "    Week: $($response.week_info.start_date) to $($response.week_info.end_date)" -ForegroundColor Gray
} catch {
    Write-Host "  ⚠ Room occupancy endpoint not responding yet" -ForegroundColor Yellow
    Write-Host "    This is normal, server may still be initializing" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  Backend Restart Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Check the new window for server logs" -ForegroundColor White
Write-Host "  2. Verify server shows: 'Uvicorn running on http://127.0.0.1:8000'" -ForegroundColor White
Write-Host "  3. Start frontend: cd frontend; npm run dev" -ForegroundColor White
Write-Host "  4. Test in browser: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Yellow
Write-Host "  Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Room Occupancy (debug): http://localhost:8000/room-occupancy/debug/rooms" -ForegroundColor White
Write-Host ""
