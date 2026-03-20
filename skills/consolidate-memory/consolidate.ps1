#!/usr/bin/env powershell
# OpenClaw Memory Consolidation Script
# Run nightly to extract key decisions and update memory files

param(
    [switch]$Manual = $false,
    [string]$WorkspacePath = "$env:USERPROFILE\.openclaw\workspace"
)

$ErrorActionPreference = "Stop"

# Configuration
$MemoryDir = Join-Path $WorkspacePath "memory"
$GitExe = "C:\Program Files\Git\bin\git.exe"

Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  OPENCLAW MEMORY CONSOLIDATION" -ForegroundColor Cyan
Write-Host "  $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')" -ForegroundColor Gray
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Verify memory directory exists
if (-not (Test-Path $MemoryDir)) {
    Write-Error "Memory directory not found: $MemoryDir"
    exit 1
}

Write-Host "✓ Memory directory found: $MemoryDir" -ForegroundColor Green

# Step 2: Find recent memory files (last 24 hours)
$CutoffDate = (Get-Date).AddHours(-24)
$RecentFiles = Get-ChildItem -Path $MemoryDir -Filter "2026-*.md" | 
    Where-Object { $_.LastWriteTime -gt $CutoffDate -and $_.Name -match '^\d{4}-\d{2}-\d{2}\.md$' } |
    Sort-Object LastWriteTime -Descending

Write-Host "Found $($RecentFiles.Count) memory files from last 24 hours" -ForegroundColor Gray

# Step 3: Read recent-memory.md
$RecentMemoryPath = Join-Path $MemoryDir "recent-memory.md"
if (Test-Path $RecentMemoryPath) {
    $RecentContent = Get-Content $RecentMemoryPath -Raw
    Write-Host "✓ Loaded recent-memory.md" -ForegroundColor Green
} else {
    Write-Host "⚠ recent-memory.md not found, will create new" -ForegroundColor Yellow
    $RecentContent = "# Recent Memory — Rolling 48hr Context`n**Last Updated:** $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')`n`n---`n`n"
}

# Step 4: Update timestamp in recent-memory
$NewRecentContent = $RecentContent -replace 'Last Updated:.*UTC', "Last Updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss UTC')"

# Step 5: Remove entries older than 48 hours
$TwoDaysAgo = (Get-Date).AddHours(-48)
$CutoffString = $TwoDaysAgo.ToString('yyyy-MM-dd')

# Simple logic: keep entries from last 48 hours only
# This is a basic implementation - could be enhanced with date parsing
$Lines = $NewRecentContent -split "`n"
$FilteredLines = @()
$InOldEntry = $false

foreach ($Line in $Lines) {
    if ($Line -match "^### 2026-\d{2}-\d{2}") {
        $EntryDate = $Line -replace "### ", "" -replace " —.*", ""
        if ($EntryDate -lt $CutoffString) {
            $InOldEntry = $true
        } else {
            $InOldEntry = $false
            $FilteredLines += $Line
        }
    } elseif ($Line -match "^###") {
        $InOldEntry = $false
        $FilteredLines += $Line
    } elseif (-not $InOldEntry) {
        $FilteredLines += $Line
    }
}

$NewRecentContent = $FilteredLines -join "`n"

# Step 6: Extract key decisions from today's files
$KeyDecisions = @()
$KeyInsights = @()
$ProjectUpdates = @()

foreach ($File in $RecentFiles) {
    $Content = Get-Content $File.FullName -Raw
    
    # Extract decisions (look for patterns)
    if ($Content -match "Decision.*?:\s*(.+?)(?=\n|$)") {
        $KeyDecisions += $Matches[1].Trim()
    }
    
    # Extract critical insights
    if ($Content -match "Critical.*?(?:Finding|Gap).*?:\s*(.+?)(?=\n|$)") {
        $KeyInsights += $Matches[1].Trim()
    }
    
    # Extract project updates
    if ($Content -match "Project.*?:\s*(.+?)(?=\n|$)") {
        $ProjectUpdates += $Matches[1].Trim()
    }
}

Write-Host "Extracted $($KeyDecisions.Count) decisions, $($KeyInsights.Count) insights" -ForegroundColor Gray

# Step 7: Read long-term-memory.md
$LongTermPath = Join-Path $MemoryDir "long-term-memory.md"
if (Test-Path $LongTermPath) {
    $LongTermContent = Get-Content $LongTermPath -Raw
    Write-Host "✓ Loaded long-term-memory.md" -ForegroundColor Green
} else {
    Write-Host "⚠ long-term-memory.md not found, will create new" -ForegroundColor Yellow
    $LongTermContent = ""
}

# Step 8: Promote critical insights to long-term
$PromotedCount = 0
foreach ($Insight in $KeyInsights) {
    if ($LongTermContent -notcontains $Insight) {
        # Add to long-term with timestamp
        $LongTermContent += "`n`n**Insight ($(Get-Date -Format 'yyyy-MM-dd')):** $Insight"
        $PromotedCount++
    }
}

# Step 9: Save updated files
$NewRecentContent | Set-Content $RecentMemoryPath -NoNewline
Write-Host "✓ Updated recent-memory.md" -ForegroundColor Green

if ($PromotedCount -gt 0) {
    $LongTermContent | Set-Content $LongTermPath -NoNewline
    Write-Host "✓ Updated long-term-memory.md (+$PromotedCount insights)" -ForegroundColor Green
}

# Step 10: Git commit
Set-Location $WorkspacePath

if (Test-Path $GitExe) {
    & $GitExe add memory/ --verbose 2>&1 | Out-Null
    $Status = & $GitExe status --porcelain 2>$null
    
    if ($Status) {
        $CommitMessage = "Memory consolidation: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
        & $GitExe commit -m $CommitMessage 2>&1 | Out-Null
        & $GitExe push origin master 2>&1 | Out-Null
        Write-Host "✓ Committed and pushed to GitHub" -ForegroundColor Green
    } else {
        Write-Host "  No changes to commit" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠ Git not found, skipping commit" -ForegroundColor Yellow
}

# Step 11: Report
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  CONSOLIDATION COMPLETE" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files Updated:" -ForegroundColor White
Write-Host "  ✓ recent-memory.md    (48hr window updated)" -ForegroundColor Green
if ($PromotedCount -gt 0) {
    Write-Host "  ✓ long-term-memory.md (+$PromotedCount new insights)" -ForegroundColor Green
}
Write-Host ""
Write-Host "Key Decisions Found: $($KeyDecisions.Count)" -ForegroundColor Gray
Write-Host "Critical Insights: $($KeyInsights.Count)" -ForegroundColor Gray
Write-Host ""
if ($Manual) {
    Write-Host "Run manually. Next auto-run: tonight at 02:00 UTC" -ForegroundColor Yellow
} else {
    Write-Host "Next auto-run: tomorrow at 02:00 UTC" -ForegroundColor Gray
}
Write-Host ""
