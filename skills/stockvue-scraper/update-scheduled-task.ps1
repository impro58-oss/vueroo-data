# Update StockVue scheduled task to use Alpha Vantage
param(
    [string]$OldTaskName = "StockVue Auto Scanner",
    [string]$NewTaskName = "StockVue Alpha Vantage Scanner",
    [string]$ScriptPath = "C:\Users\impro\.openclaw\workspace\skills\stockvue-scraper\auto_stock_scanner.ps1",
    [string]$ApiKey = "736QMMKKKRUZP5F3"
)

Write-Host "Updating StockVue scheduled task..." -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Remove old task if exists
try {
    $OldTask = Get-ScheduledTask -TaskName $OldTaskName -ErrorAction SilentlyContinue
    if ($OldTask) {
        Write-Host "Removing old task '$OldTaskName'..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $OldTaskName -Confirm:$false
        Write-Host "Old task removed." -ForegroundColor Green
    }
} catch {
    # Task doesn't exist
}

# Remove new task if already exists (fresh start)
try {
    $ExistingTask = Get-ScheduledTask -TaskName $NewTaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Write-Host "Removing existing task '$NewTaskName'..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $NewTaskName -Confirm:$false
    }
} catch {
    # Task doesn't exist
}

# Create the action
$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`" -ApiKey `"$ApiKey`""

# Create the trigger (every 3 hours, but API limit is 25 calls/day)
# So we run: 08:00, 12:00, 16:00 (3 times = 12-15 symbols max per day)
$Triggers = @()
$Triggers += New-ScheduledTaskTrigger -Daily -At "08:00"
$Triggers += New-ScheduledTaskTrigger -Daily -At "12:00"
$Triggers += New-ScheduledTaskTrigger -Daily -At "16:00"

# Create task settings
$Settings = New-ScheduledTaskSettingsSet `
    -RunOnlyIfNetworkAvailable `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopOnIdleEnd

# Create principal
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive

# Create the task
Write-Host "Creating new Alpha Vantage task..."
try {
    Register-ScheduledTask `
        -TaskName $NewTaskName `
        -Action $Action `
        -Trigger $Triggers `
        -Settings $Settings `
        -Principal $Principal `
        -Description "StockVue market scanner using Alpha Vantage API (25 calls/day limit)" `
        -Force

    Write-Host ""
    Write-Host "[SUCCESS] Task '$NewTaskName' created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  - Name: $NewTaskName"
    Write-Host "  - Schedule: 08:00, 12:00, 16:00 daily"
    Write-Host "  - Script: $ScriptPath"
    Write-Host "  - API: Alpha Vantage (25 calls/day free tier)"
    Write-Host ""
    Write-Host "API Limits:" -ForegroundColor Yellow
    Write-Host "  - 25 calls/day = ~12 symbols with RSI (2 calls each)"
    Write-Host "  - Or 25 symbols with prices only (1 call each)"
    Write-Host ""
    Write-Host "To run now:" -ForegroundColor Cyan
    Write-Host "  Start-ScheduledTask -TaskName '$NewTaskName'"

} catch {
    Write-Host ""
    Write-Host "[ERROR] Failed to create task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
