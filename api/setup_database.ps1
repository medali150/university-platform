#!/usr/bin/env pwsh
# Setup database with French schema
Write-Host "🚀 Setting up University Platform Database with French Schema..." -ForegroundColor Green
Write-Host ""

Write-Host "📝 Validating Prisma schema..." -ForegroundColor Yellow
npx prisma validate
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Schema validation failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Schema is valid!" -ForegroundColor Green
Write-Host ""

Write-Host "🔄 Resetting database and applying schema..." -ForegroundColor Yellow
python reset_and_migrate.py

Write-Host ""
Write-Host "🎉 Database setup complete!" -ForegroundColor Green
Write-Host "You can now start your FastAPI server and test the frontend." -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"