#!/usr/bin/env powershell
# Auto-commit stock data to GitHub (both repos)

$WorkingDir = "C:\Users\impro\.openclaw\workspace"
$DataDir = "$WorkingDir\data\stocks"

Set-Location $WorkingDir

# Check for changes
$Status = git status --porcelain

if ($Status) {
    Write-Host "Stock data changes detected"
    
    # Stage stock data
    git add data/stocks/
    
    # Commit
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "StockVue: Update stock market data - $Timestamp UTC"
    
    # Push to rooquest1 (private archive)
    git push origin master
    Write-Host "Pushed to rooquest1"
    
    # Push to vueroo-data (public - for dashboards)
    git push data master
    Write-Host "Pushed to vueroo-data"
    
    Write-Host "Stock data committed to both repos"
} else {
    Write-Host "No changes to commit"
}
