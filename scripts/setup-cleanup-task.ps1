# Polymarket Auto-Cleanup Scheduled Task Setup
# Run this script once to create the daily cleanup task

$TaskName = "OpenClaw-Polymarket-Cleanup"
$ScriptPath = "C:\Users\impro\.openclaw\workspace\scripts\cleanup-polymarket.ps1"
$LogPath = "C:\Users\impro\.openclaw\workspace\scripts\logs\cleanup-polymarket.log"

# Create logs directory if it doesn't exist
$LogDir = Split-Path -Parent $LogPath
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Check if script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Error "Cleanup script not found at: $ScriptPath"
    exit 1
}

# Remove existing task if it exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Removed existing task: $TaskName"
}

# Create the scheduled task
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`" -LogPath `"$LogPath`""

# Trigger: Daily at 3:00 AM (after the last scan of the day)
$Trigger = New-ScheduledTaskTrigger -Daily -At "03:00"

# Settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Register the task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Auto-cleanup Polymarket scan files older than 24 hours" -RunLevel Highest

Write-Host "`nScheduled task '$TaskName' created successfully!" -ForegroundColor Green
Write-Host "Runs daily at 3:00 AM"
Write-Host "Logs saved to: $LogPath"

# Show task info
Get-ScheduledTask -TaskName $TaskName | Select-Object TaskName, State, NextRunTime | Format-List
