#!/usr/bin/env powershell
# Auto-commit stock data to GitHub

$WorkingDir = "C:\Users\impro\.openclaw\workspace"
$DataDir = "$WorkingDir\data\stocks"

Set-Location $WorkingDir

# Check for changes
$Status = git status --porcelain

if ($Status) {
    Write-Host "📊 Changes detected in stock data"
    
    # Stage stock data
    git add data/stocks/
    
    # Commit
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "StockVue: Update stock market data - $Timestamp UTC"
    
    # Push
    git push origin master
    
    Write-Host "✅ Stock data committed to GitHub"
} else {
    Write-Host "📭 No changes to commit"
}
