# PowerShell script to clear Prisma database
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "           DATABASE CLEANUP UTILITY" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

Write-Host "Choose an option:" -ForegroundColor Yellow
Write-Host "1. Safe clear (with confirmation)" -ForegroundColor White
Write-Host "2. Quick clear (no confirmation)" -ForegroundColor White
Write-Host "3. Cancel" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Running safe database clear..." -ForegroundColor Green
        python clear_database.py
    }
    "2" {
        Write-Host ""
        Write-Host "Running quick database clear..." -ForegroundColor Green
        python quick_clear.py
    }
    "3" {
        Write-Host "Operation cancelled." -ForegroundColor Yellow
    }
    default {
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Read-Host "Press Enter to continue..."