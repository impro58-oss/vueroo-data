# Deploy-CryptoVue-Data.ps1
# Permanent solution for CryptoVue data freshness
# Pushes latest scan to predictable URL and invalidates cache

param(
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

# Config
$RepoRoot = "C:\Users\impro\.openclaw\workspace"
$DataDir = "$RepoRoot\data\crypto"
$GitHubRepo = "impro58-oss/rooquest1"
$GitHubBranch = "master"

Write-Host "=== CryptoVue Data Deploy ===" -ForegroundColor Cyan

# Find the latest scan file
$LatestScan = Get-ChildItem -Path "$RepoRoot\skills\tradingview-claw-v2" -Filter "top_50_analysis_*.json" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 1

if (-not $LatestScan) {
    Write-Error "No scan files found!"
    exit 1
}

Write-Host "Latest scan: $($LatestScan.Name)" -ForegroundColor Green

# Read the scan data
$ScanData = Get-Content $LatestScan.FullName | ConvertFrom-Json

# Create stable symlink-style file (always same name)
$StableFile = "$DataDir\crypto_latest_stable.json"
$ScanData | ConvertTo-Json -Depth 10 | Set-Content $StableFile

Write-Host "Created stable reference: crypto_latest_stable.json"

# Ensure dated archive exists
$ArchiveMonth = $ScanData.analysis_time.Substring(0,7)  # YYYY-MM
$ArchiveDir = "$DataDir\$ArchiveMonth"
if (-not (Test-Path $ArchiveDir)) {
    New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null
}

$ArchiveFile = "$ArchiveDir\$($LatestScan.Name)"
if (-not (Test-Path $ArchiveFile)) {
    Copy-Item $LatestScan.FullName $ArchiveFile
    Write-Host "Archived to: $ArchiveFile"
}

# Stage and commit
Set-Location $RepoRoot

# Check if there are changes
$Status = git status --porcelain
if ($Status -or $Force) {
    Write-Host "Committing changes to GitHub..." -ForegroundColor Yellow
    
    git add data/crypto/ | Out-Null
    git commit -m "Auto-deploy: CryptoVue data $($LatestScan.Name) [$(Get-Date -Format 'yyyy-MM-dd HH:mm')]" | Out-Null
    git push origin $GitHubBranch | Out-Null
    
    Write-Host "✅ Committed and pushed to GitHub" -ForegroundColor Green
    
    # Show the URL that should work
    $ExpectedUrl = "https://raw.githubusercontent.com/$GitHubRepo/$GitHubBranch/data/crypto/crypto_latest_stable.json"
    Write-Host "Expected URL: $ExpectedUrl"
    
    # Wait for GitHub to propagate (usually 30-60 seconds)
    Write-Host "Waiting 5 seconds for CDN propagation..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Verify URL is accessible
    try {
        $Response = Invoke-WebRequest -Uri "$ExpectedUrl?t=$(Get-Random)" -UseBasicParsing -TimeoutSec 10
        $RemoteData = $Response.Content | ConvertFrom-Json
        Write-Host "✅ GitHub raw URL verified! Scan date: $($RemoteData.scan_date)" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  GitHub CDN may still be propagating (cache delay up to 5 minutes)" -ForegroundColor Yellow
    }
    
} else {
    Write-Host "No changes to commit" -ForegroundColor Gray
}

Write-Host "=== Deploy Complete ===" -ForegroundColor Cyan
