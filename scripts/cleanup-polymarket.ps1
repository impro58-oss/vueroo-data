#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Auto-cleanup script for Polymarket scan files
.DESCRIPTION
    Removes Polymarket scan files older than 24 hours.
    Keeps only the latest 24 hours of data plus the -latest files.
    Should be run daily via scheduled task.
.EXAMPLE
    .\cleanup-polymarket.ps1
#>

param(
    [string]$DataPath = "$PSScriptRoot\..\data\polymarket",
    [int]$KeepHours = 24,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

# Calculate cutoff time
$CutoffTime = (Get-Date).AddHours(-$KeepHours)
Write-Host "Cleaning Polymarket files older than: $CutoffTime" -ForegroundColor Cyan

# Get all polymarket files (excluding *-latest files)
$Files = Get-ChildItem -Path $DataPath -File | Where-Object { 
    ($_.Name -like "hot-bets-*.html" -or $_.Name -like "polymarket_*.json") -and
    $_.Name -notlike "*-latest.*"
}

$DeletedCount = 0
$KeptCount = 0
$TotalSize = 0

foreach ($File in $Files) {
    # Extract timestamp from filename
    # Format: hot-bets-2026-03-25-0700.html or polymarket_2026-03-25-0700.json
    if ($File.Name -match "(\d{4})-(\d{2})-(\d{2})-(\d{2})(\d{2})") {
        $FileDateTime = Get-Date -Year $matches[1] -Month $matches[2] -Day $matches[3] -Hour $matches[4] -Minute $matches[5]
        
        if ($FileDateTime -lt $CutoffTime) {
            # File is older than cutoff - delete it
            if ($DryRun) {
                Write-Host "[DRY RUN] Would delete: $($File.Name)" -ForegroundColor Yellow
            } else {
                Remove-Item -Path $File.FullName -Force
                Write-Host "Deleted: $($File.Name)" -ForegroundColor Red
            }
            $DeletedCount++
            $TotalSize += $File.Length
        } else {
            Write-Host "Kept: $($File.Name)" -ForegroundColor Green
            $KeptCount++
        }
    } else {
        Write-Warning "Could not parse timestamp from: $($File.Name)"
    }
}

# Summary
Write-Host "`n=== Cleanup Summary ===" -ForegroundColor Cyan
Write-Host "Files deleted: $DeletedCount" -ForegroundColor Red
Write-Host "Files kept: $KeptCount" -ForegroundColor Green
Write-Host "Space freed: $([math]::Round($TotalSize / 1KB, 2)) KB" -ForegroundColor Yellow

# Git commit if files were deleted
if ($DeletedCount -gt 0 -and -not $DryRun) {
    $RepoRoot = Resolve-Path "$PSScriptRoot\.."
    Push-Location $RepoRoot
    try {
        $HasChanges = git status --porcelain 2>$null | Where-Object { $_ -match "^\s*D" }
        if ($HasChanges) {
            Write-Host "`nCommitting deletions to Git..." -ForegroundColor Cyan
            git add data/polymarket/
            git commit -m "Auto-cleanup: Remove Polymarket scans older than 24 hours ($(Get-Date -Format 'yyyy-MM-dd HH:mm'))"
            git push origin master
            Write-Host "Git commit and push complete!" -ForegroundColor Green
        }
    } catch {
        Write-Warning "Git operations failed: $_"
    } finally {
        Pop-Location
    }
}

Write-Host "`nCleanup complete!" -ForegroundColor Green
