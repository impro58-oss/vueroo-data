# Polymarket Complete Hourly Scan + Alert
# Runs scanner and sends Telegram alert if hot bets found

$WorkingDir = "C:\Users\impro\.openclaw\workspace\scripts"
$Timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"

Write-Host "=== POLYMARKET HOURLY SCAN ==="
Write-Host "Time: $Timestamp"
Write-Host ""

# Run the improved scanner
$AlertFile = & "$WorkingDir\polymarket-hourly-scanner-v2.ps1"

if ($AlertFile -and (Test-Path $AlertFile)) {
    Write-Host ""
    Write-Host "Sending Telegram alert..."
    
    # Send alert
    & "$WorkingDir\polymarket-alert-telegram-v2.ps1" -AlertFile $AlertFile
    
    Write-Host "Done!"
} else {
    Write-Host "No alert file generated (no hot bets or error)"
}

Write-Host ""
Write-Host "=== SCAN COMPLETE ==="
