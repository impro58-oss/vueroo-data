# Generate-FallbackList.ps1
# Creates an auto-updated list of recent scan files for fallback loading
# Called automatically after each crypto scan

param(
    [int]$DaysBack = 7
)

$RepoRoot = "C:\Users\impro\.openclaw\workspace"
$ScanDir = "$RepoRoot\skills\tradingview-claw-v2"
$OutputFile = "$RepoRoot\vueroo-portal\public\crypto\fallback-files.json"

Write-Host "Generating fallback file list..." -ForegroundColor Cyan

# Find all scan files
$ScanFiles = Get-ChildItem -Path $ScanDir -Filter "top_200_analysis_*.json" |
    Where-Object { $_.Name -match 'top_200_analysis_(\d{8})_(\d{6})\.json' } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 50  # Last 50 scans

if ($ScanFiles.Count -eq 0) {
    Write-Error "No scan files found!"
    exit 1
}

# Build fallback list with metadata
$Fallbacks = $ScanFiles | ForEach-Object {
    $Match = $_.Name -match 'top_200_analysis_(\d{8})_(\d{6})\.json'
    if ($Match) {
        $DateStr = $Matches[1]
        $TimeStr = $Matches[2]
        $Year = $DateStr.Substring(0,4)
        $Month = $DateStr.Substring(4,2)
        $Day = $DateStr.Substring(6,2)
        $Hour = $TimeStr.Substring(0,2)
        $Minute = $TimeStr.Substring(2,2)
        $Second = $TimeStr.Substring(4,2)
        
        [PSCustomObject]@{
            filename = $_.Name
            timestamp = "$Year-$Month-$Day $Hour`:$Minute`:$Second"
            iso_timestamp = "$Year-$Month-$Day`T$Hour`:$Minute`:$Second`Z"
        }
    }
}

# Save as JSON
$Fallbacks | ConvertTo-Json -Depth 2 | Set-Content $OutputFile

Write-Host "✅ Generated fallback list with $($Fallbacks.Count) entries" -ForegroundColor Green
Write-Host "   Saved to: $OutputFile"

# Also update the data-loader.js CONFIG.FALLBACK_FILES (optional - static fallback)
$RecentFiles = $Fallbacks | Select-Object -First 20 | ForEach-Object { $_.filename }
Write-Host "   Recent files: $($RecentFiles -join ', ')"

# Stage for commit (vueroo-portal is a submodule)
Set-Location "$RepoRoot\vueroo-portal"
git add public/crypto/fallback-files.json | Out-Null

# Show summary
$Latest = $Fallbacks | Select-Object -First 1
Write-Host "   Latest scan: $($Latest.filename) at $($Latest.timestamp)"
