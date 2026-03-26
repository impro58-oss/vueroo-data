# StockVue Auto Scanner — Runs every 3 hours using Alpha Vantage
param(
    [string]$WorkingDir = "C:\Users\impro\.openclaw\workspace\skills\stockvue-scraper",
    [string]$PythonPath = "C:\Users\impro\AppData\Local\Programs\Python\Python311\python.exe",
    [string]$ApiKey = "736QMMKKKRUZP5F3"
)

Set-Location $WorkingDir

# Log file
$LogDir = "$WorkingDir\logs"
$LogFile = "$LogDir\stock_scan_$(Get-Date -Format 'yyyyMMdd').log"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$Timestamp - $Message" | Tee-Object -FilePath $LogFile -Append
}

Write-Log "=== Starting StockVue Alpha Vantage Scan ==="

# Run scraper
Write-Log "Scanning stocks using Alpha Vantage API..."
try {
    $env:ALPHA_VANTAGE_API_KEY = $ApiKey
    $Output = & $PythonPath alpha_vantage_scraper.py 2>&1
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
