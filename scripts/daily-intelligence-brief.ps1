# Daily Intelligence Brief - Runs at 6:30 AM Europe/Dublin
# Generates summary report and sends to Telegram

param(
    [string]$WorkingDir = "C:\Users\impro\.openclaw\workspace"
)

$LogFile = "$WorkingDir\logs\daily-intelligence-$(Get-Date -Format 'yyyyMM').log"
New-Item -ItemType Directory -Force -Path "$WorkingDir\logs" | Out-Null

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry -Encoding UTF8
}

Write-Log "=== DAILY INTELLIGENCE BRIEF STARTED ==="

# Check for overnight crypto scans
$CryptoDataPath = "$WorkingDir\data\crypto\crypto_history.json"
$LatestScanPath = "$WorkingDir\data\crypto\crypto_latest.json"

$Report = @()
$Report += "=== DAILY INTELLIGENCE BRIEF ==="
$Report += "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm') UTC"
$Report += ""

# Crypto Summary
if (Test-Path $LatestScanPath) {
    try {
        $LatestData = Get-Content $LatestScanPath | ConvertFrom-Json
        $Report += "CRYPTO MARKETS:"
        $Report += "- Symbols scanned: $($LatestData.summary.total_symbols)"
        $Report += "- LONG signals: $($LatestData.summary.long_signals)"
        $Report += "- SHORT signals: $($LatestData.summary.short_signals)"
        $Report += "- HOLD signals: $($LatestData.summary.hold_signals)"
        $Report += "- Last scan: $($LatestData.timestamp)"
        $Report += ""
        
        # Top opportunities
        $Opportunities = $LatestData.results | Where-Object { $_.signal -in @('LONG', 'SHORT') -and $_.confidence -ge 0.45 } | Sort-Object confidence -Descending | Select-Object -First 3
        if ($Opportunities) {
            $Report += "TOP OPPORTUNITIES:"
            foreach ($Opp in $Opportunities) {
                $Report += "- $($Opp.symbol): $($Opp.signal) @ $([math]::Round($Opp.confidence * 100))% confidence"
            }
            $Report += ""
        }
        
        Write-Log "Crypto data loaded: $($LatestData.summary.total_symbols) symbols"
    } catch {
        Write-Log "Error loading crypto data: $_"
        $Report += "CRYPTO: Error loading data"
        $Report += ""
    }
} else {
    Write-Log "No crypto data found"
    $Report += "CRYPTO: No scan data available"
    $Report += ""
}

# System Status
$Report += "SYSTEM STATUS:"
$Report += "- Gateway: $(if ((Test-NetConnection -ComputerName 127.0.0.1 -Port 18789 -WarningAction SilentlyContinue).TcpTestSucceeded) { 'ONLINE' } else { 'OFFLINE' })"
$Report += "- Last commit: $(git -C $WorkingDir log -1 --format='%h %s' 2>$null)"
$Report += ""

# Notion Control Room Update
$Report += "NOTION CONTROL ROOM:"
$Report += "- Visual Dashboard: https://notion.so/3230491758dd819c90e4fce960777521"
$Report += "- Intelligence DB: https://notion.so/3230491758dd81d8a31efe277bf4b0d1"
$Report += ""

$Report += "=== END OF BRIEF ==="

# Output report
$ReportText = $Report -join "`n"
Write-Host "`n$ReportText"

# Send to Telegram if configured
$TelegramBotToken = "8758242941:AAFga397u6IC3BqT-n866h2cd_XB1xJYQsw"
$TelegramChatId = "1018254667"  # Roo's chat ID

if ($TelegramBotToken -and $TelegramChatId) {
    try {
        $Url = "https://api.telegram.org/bot$TelegramBotToken/sendMessage"
        $Body = @{
            chat_id = $TelegramChatId
            text = $ReportText
            parse_mode = "HTML"
        } | ConvertTo-Json
        
        Invoke-RestMethod -Uri $Url -Method Post -ContentType "application/json" -Body $Body | Out-Null
        Write-Log "Report sent to Telegram"
    } catch {
        Write-Log "Failed to send Telegram message: $_"
    }
}

# Save report to file
$ReportPath = "$WorkingDir\reports\daily-brief-$(Get-Date -Format 'yyyy-MM-dd').txt"
New-Item -ItemType Directory -Force -Path "$WorkingDir\reports" | Out-Null
$ReportText | Out-File -FilePath $ReportPath -Encoding UTF8
Write-Log "Report saved to: $ReportPath"

Write-Log "=== DAILY INTELLIGENCE BRIEF COMPLETE ==="
