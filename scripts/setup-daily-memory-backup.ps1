# Setup Daily Memory Backup Task
# Creates a scheduled task to run daily memory backup at 23:00

param(
    [string]$TaskName = "Daily Memory Backup",
    [string]$ScriptPath = "C:\Users\impro\.openclaw\workspace\scripts\daily-memory-backup.ps1",
    [string]$UserName = $env:USERNAME
)

Write-Host "Setting up Daily Memory Backup Task..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Verify script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Host "[ERROR] Script not found: $ScriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "Script path: $ScriptPath"
Write-Host "Task name: $TaskName"
Write-Host "Run as: $UserName"
Write-Host ""

# Check if task already exists
try {
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Write-Host "Task '$TaskName' already exists. Removing old task..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Old task removed." -ForegroundColor Green
    }
} catch {
    # Task doesn't exist, continue
}

# Create the action
$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ScriptPath`""

# Create the trigger (daily at 23:00)
$Trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "23:00"

# Create task settings
$Settings = New-ScheduledTaskSettingsSet `
    -RunOnlyIfNetworkAvailable `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopOnIdleEnd

# Create principal (run as current user)
$Principal = New-ScheduledTaskPrincipal `
    -UserId $UserName `
    -LogonType Interactive

# Create the task
Write-Host "Creating scheduled task..."
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "Daily backup of memory files to GitHub and local archive" `
        -Force

    Write-Host ""
    Write-Host "[SUCCESS] Task '$TaskName' created!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Task Details:" -ForegroundColor Cyan
    Write-Host "  - Name: $TaskName"
    Write-Host "  - Schedule: Daily at 23:00"
    Write-Host "  - Script: $ScriptPath"
    Write-Host "  - Logs: C:\Users\impro\.openclaw\workspace\logs\"
    Write-Host ""
    Write-Host "Next run: $((Get-Date).Date.AddDays(1).ToString('yyyy-MM-dd')) 23:00"
    Write-Host ""
    Write-Host "To test now, run:" -ForegroundColor Yellow
    Write-Host "  powershell -File `"$ScriptPath`"" -ForegroundColor DarkYellow

} catch {
    Write-Host ""
    Write-Host "[ERROR] Failed to create task: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
