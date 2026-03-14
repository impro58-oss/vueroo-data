# Polymarket Hourly Scan
# Runs every hour, sends Telegram alert if hot bets found

cd "C:\Users\impro\.openclaw\workspace\scripts"

# Run scanner and capture output
$HotBets = .\polymarket-hourly-scanner.ps1

# If hot bets found, send Telegram alert
if ($HotBets) {
    $LatestAlert = Get-ChildItem "C:\Users\impro\Documents\Polymarket-Scans\2026-03-14\hot-bets-*.txt" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($LatestAlert) {
        .\polymarket-alert-telegram.ps1 -AlertFile $LatestAlert.FullName
    }
}

# Update Notion with new opportunities
.\update-notion-next-bets.ps1
