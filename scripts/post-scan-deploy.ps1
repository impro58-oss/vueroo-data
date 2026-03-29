# Post-Scan-Deploy.ps1
# Complete deployment pipeline after crypto scan completes
# Ensures data reaches GitHub and dashboard stays fresh

param(
    [switch]$SkipCommit = $false,
    [switch]$SkipVercel = $false
)

$ErrorActionPreference = "Stop"

$RepoRoot = "C:\Users\impro\.openclaw\workspace"
$ScanDir = "$RepoRoot\skills\tradingview-claw-v2"
$DataDir = "$RepoRoot\data\crypto"

Write-Host "=== Post-Scan Deploy Pipeline ===" -ForegroundColor Cyan

# 1. Find the scan we just created
$LatestScan = Get-ChildItem -Path $ScanDir -Filter "top_50_analysis_*.json" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $LatestScan) {
    Write-Error "No scan file found! Did the scan complete?"
    exit 1
}

$ScanData = Get-Content $LatestScan.FullName | ConvertFrom-Json
Write-Host "Found scan: $($LatestScan.Name)" -ForegroundColor Green
Write-Host "  Analysis time: $($ScanData.analysis_time)"
Write-Host "  Results: $($ScanData.results.Count) symbols"

# 2. Ensure crypto_latest.json exists and is up to date
$LatestJson = "$DataDir\crypto_latest.json"
if (Test-Path $LatestJson) {
    $CurrentLatest = Get-Content $LatestJson | ConvertFrom-Json
    $CurrentTime = $CurrentLatest.scan_timestamp -as [datetime]
    $NewTime = $ScanData.analysis_time -as [datetime]
    
    if ($NewTime -gt $CurrentTime) {
        Write-Host "Updating crypto_latest.json with newer data..." -ForegroundColor Yellow
        Copy-Item $LatestScan.FullName $LatestJson -Force
    } else {
        Write-Host "crypto_latest.json already current" -ForegroundColor Gray
    }
} else {
    Write-Host "Creating crypto_latest.json..." -ForegroundColor Yellow
    Copy-Item $LatestScan.FullName $LatestJson
}

# 3. Archive to dated folder
$ScanDate = ($ScanData.analysis_time -as [datetime]).ToString("yyyy-MM")
$ArchiveDir = "$DataDir\$ScanDate"
if (-not (Test-Path $ArchiveDir)) {
    New-Item -ItemType Directory -Path $ArchiveDir -Force | Out-Null
}
$ArchivePath = "$ArchiveDir\$($LatestScan.Name)"
if (-not (Test-Path $ArchivePath)) {
    Copy-Item $LatestScan.FullName $ArchivePath
    Write-Host "Archived to: $ArchivePath" -ForegroundColor Gray
}

# 4. Generate fallback file list
Write-Host "Generating fallback file list..." -ForegroundColor Cyan
& "$RepoRoot\scripts\generate-fallback-list.ps1" | Out-Null

# 5. Commit to GitHub
if (-not $SkipCommit) {
    Write-Host "Committing to GitHub..." -ForegroundColor Cyan
    Set-Location $RepoRoot
    
    $Changes = git status --porcelain
    if ($Changes) {
        git add data/crypto/ skills/tradingview-claw-v2/*.json vueroo-portal/public/crypto/fallback-files.json
        
        $CommitMsg = "Scan $($LatestScan.Name) - $(Get-Date -Format 'yyyy-MM-dd HH:mm') UTC"
        git commit -m $CommitMsg
        
        Write-Host "Pushing to origin..." -ForegroundColor Yellow
        git push origin master
        
        Write-Host "✅ Committed and pushed" -ForegroundColor Green
        
        # Wait for GitHub CDN (typically 30-60 seconds, up to 5 minutes)
        Write-Host "Waiting for GitHub CDN propagation..." -ForegroundColor Yellow
        Start-Sleep -Seconds 3
        
        # Verify raw URL is accessible
        $TestUrl = "https://raw.githubusercontent.com/impro58-oss/rooquest1/master/data/crypto/crypto_latest.json?t=" + [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        try {
            $Response = Invoke-WebRequest -Uri $TestUrl -UseBasicParsing -TimeoutSec 15
            $RemoteData = $Response.Content | ConvertFrom-Json
            Write-Host "✅ GitHub raw URL verified - scan date: $($RemoteData.scan_date)" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  CDN still propagating (normal, can take up to 5 minutes)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "No changes to commit" -ForegroundColor Gray
    }
}

# 6. Trigger Vercel redeploy (if needed)
if (-not $SkipVercel) {
    Write-Host "Triggering Vercel redeploy..." -ForegroundColor Cyan
    Set-Location "$RepoRoot\vueroo-portal"
    
    # Empty commit to force redeploy
    $VercelCommitMsg = "Deploy: Crypto data update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    
    try {
        git commit --allow-empty -m $VercelCommitMsg
        git push origin main
        Write-Host "✅ Vercel redeploy triggered" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Vercel deploy skipped (may already be in progress)" -ForegroundColor Yellow
    }
}

Write-Host "=== Deploy Pipeline Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard should update within 2-3 minutes" -ForegroundColor White
Write-Host "If still showing old data, hard refresh: Ctrl+Shift+R" -ForegroundColor Gray
