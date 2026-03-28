# NeuroVue Local Server Starter
# Run this script to start the local server

Write-Host "Starting NeuroVue Local Server..." -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard will be available at: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

Set-Location "C:\Users\impro\.openclaw\workspace\neurovue-local"
python -m http.server 8080

Read-Host "Press Enter to exit"
