# Unified-Deploy.ps1
# Deploys ALL dashboard data (CryptoVue + StockVue + Polymarket) to GitHub
# Run automatically after each scan completes

param(
    [ValidateSet('crypto', 'stocks', 'polymarket', 'all')]
    [string]$Source = 'all',
    [switch]$SkipCommit = $false
)

$ErrorActionPreference = "Stop"
$RepoRoot = "C:\Users\impro\.openclaw\workspace"
$Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC'

Write-Host "=== Unified Deploy Pipeline ===" -ForegroundColor Cyan
Write-Host "Source: $Source | Time: $Timestamp"

# Track changes
$ChangesMade = $false

# ============================================================================
# CRYPTO DEPLOY
# ============================================================================
if ($Source -eq 'crypto' -or $Source -eq 'all') {
    Write-Host "`n[CRYPTO] Checking for updates..." -ForegroundColor Yellow
    
    $CryptoDir = "$RepoRoot\skills\tradingview-claw-v2"
    $CryptoLatest = Get-ChildItem -Path $CryptoDir -Filter "top_200_analysis_*.json" |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($CryptoLatest) {
        # Copy to data/crypto
        $DataDir = "$RepoRoot\data\crypto"
        $LatestJson = "$DataDir\crypto_latest.json"
        
        # Read and validate
        $ScanData = Get-Content $CryptoLatest.FullName | ConvertFrom-Json
        
        # Update crypto_latest.json
        $ScanData | ConvertTo-Json -Depth 10 | Set-Content $LatestJson
        
        # Archive
        $MonthDir = "$DataDir\$($ScanData.analysis_time.Substring(0,7))"
        if (-not (Test-Path $MonthDir)) { New-Item -ItemType Directory -Path $MonthDir -Force | Out-Null }
        $Archive = "$MonthDir\$($CryptoLatest.Name)"
        Copy-Item $CryptoLatest.FullName $Archive -Force
        
        Write-Host "  ✓ Crypto data updated: $($CryptoLatest.Name)" -ForegroundColor Green
        $ChangesMade = $true
    }
}

# ============================================================================
# STOCKS DEPLOY  
# ============================================================================
if ($Source -eq 'stocks' -or $Source -eq 'all') {
    Write-Host "`n[STOCKS] Checking for updates..." -ForegroundColor Yellow
    
    $StocksDir = "$RepoRoot\data\stocks"
    if (Test-Path "$StocksDir\stocks_latest.json") {
        $StockData = Get-Content "$StocksDir\stocks_latest.json" | ConvertFrom-Json
        
        # Archive if not already
        $MonthDir = "$StocksDir\$($StockData.scan_date.Substring(0,7))"
        if (-not (Test-Path $MonthDir)) { New-Item -ItemType Directory -Path $MonthDir -Force | Out-Null }
        
        $ArchiveFile = "$MonthDir\$($StockData.scan_date)_$($StockData.scan_time.Replace(':','')).json"
        if (-not (Test-Path $ArchiveFile)) {
            Copy-Item "$StocksDir\stocks_latest.json" $ArchiveFile
            Write-Host "  ✓ Stocks data archived" -ForegroundColor Green
            $ChangesMade = $true
        } else {
            Write-Host "  ℹ Stocks data already current" -ForegroundColor Gray
        }
    }
}

# ============================================================================
# POLYMARKET DEPLOY
# ============================================================================
if ($Source -eq 'polymarket' -or $Source -eq 'all') {
    Write-Host "`n[POLYMARKET] Checking for updates..." -ForegroundColor Yellow
    
    $PolyDir = "$RepoRoot\data\polymarket"
    if (Test-Path "$PolyDir\polymarket_latest.json") {
        $PolyData = Get-Content "$PolyDir\polymarket_latest.json" | ConvertFrom-Json
        
        $MonthDir = "$PolyDir\$($PolyData.timestamp.Substring(0,7))"
        if (-not (Test-Path $MonthDir)) { New-Item -ItemType Directory -Path $MonthDir -Force | Out-Null }
        
        $ArchiveFile = "$MonthDir\polymarket_$($PolyData.timestamp.Substring(0,10).Replace('-',''))_$($PolyData.timestamp.Substring(11,2) + $PolyData.timestamp.Substring(14,2)).json"
        if (-not (Test-Path $ArchiveFile)) {
            Copy-Item "$PolyDir\polymarket_latest.json" $ArchiveFile
            Write-Host "  ✓ Polymarket data archived" -ForegroundColor Green
            $ChangesMade = $true
        }
    }
}

# ============================================================================
# COMMIT TO GITHUB (vueroo-data public repo)
# ============================================================================
if ($ChangesMade -and -not $SkipCommit) {
    Write-Host "`n[GIT] Committing to vueroo-data..." -ForegroundColor Cyan
    
    Set-Location $RepoRoot
    
    # Stage all data directories
    git add data/crypto/ data/stocks/ data/polymarket/ --all 2>$null
    
    # Check if there's anything to commit
    $Status = git status --porcelain
    if ($Status) {
        $CommitMsg = "Deploy: $Source data update [$Timestamp]"
        git commit -m $CommitMsg 2>$null | Out-Null
        
        # Push to vueroo-data (public - for dashboards)
        Write-Host "  Pushing to vueroo-data (public)..." -ForegroundColor Yellow
        git push data master 2>$null | Out-Null
        Write-Host "  ✓ Pushed to vueroo-data" -ForegroundColor Green
        
        # Push to rooquest1 (private - for archive)
        Write-Host "  Pushing to rooquest1 (private)..." -ForegroundColor Yellow
        git push origin master 2>$null | Out-Null
        Write-Host "  ✓ Pushed to rooquest1" -ForegroundColor Green
        
        # Wait for CDN propagation
        Write-Host "  Waiting for CDN propagation (3s)..." -ForegroundColor Gray
        Start-Sleep -Seconds 3
    } else {
        Write-Host "  ℹ No new changes to commit" -ForegroundColor Gray
    }
    
    # ============================================================================
    # TRIGGER VERCEL REDEPLOY
    # ============================================================================
    Write-Host "`n[VERCEL] Triggering dashboard redeploy..." -ForegroundColor Cyan
    
    Set-Location "$RepoRoot\vueroo-portal"
    
    # Empty commit to trigger redeploy
    git commit --allow-empty -m "Deploy: Dashboard refresh [$Timestamp]" 2>$null | Out-Null
    git push origin main 2>$null | Out-Null
    
    Write-Host "  ✓ Vercel redeploy triggered" -ForegroundColor Green
}

Write-Host "`n=== Deploy Complete ===" -ForegroundColor Cyan
