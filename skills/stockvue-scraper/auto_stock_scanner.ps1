# StockVue Auto Scanner — Runs every 3 hours
param(
    [string]$WorkingDir = "C:\Users\impro\.openclaw\workspace\skills\stockvue-scraper",
    [string]$PythonPath = "C:\Users\impro\AppData\Local\Programs\Python\Python311\python.exe"
)

Set-Location $WorkingDir

# Log file
$LogFile = "$WorkingDir\logs\stock_scan_$(Get-Date -Format 'yyyyMMdd').log"
New-Item -ItemType Directory -Force -Path "$WorkingDir\logs" | Out-Null

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp - $Message" | Tee-Object -FilePath $LogFile -Append
}

Write-Log "=== Starting StockVue Scan ==="

# Run scraper
Write-Log "Scraping Yahoo Finance markets..."
try {
    $Output = & $PythonPath yahoo_finance_scraper.py 2>&1
    $Output | ForEach-Object { Write-Log $_ }
    
    # Commit to GitHub
    Write-Log "Committing data to GitHub..."
    $CommitOutput = & "C:\Users\impro\.openclaw\workspace\scripts\auto-commit-stock-data.ps1" 2>&1
    $CommitOutput | ForEach-Object { Write-Log $_ }
    
    Write-Log "=== StockVue scan complete ==="
} catch {
    Write-Log "ERROR: $_"
}

Write-Log ""
