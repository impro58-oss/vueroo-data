# Setup Daily Opportunity Research Task
# Run this script once to create the scheduled task

$taskName = "OpenClaw-Daily-Research"
$scriptPath = "C:\Users\impro\.openclaw\workspace\opportunity-research\scripts\daily-research-trigger.ps1"
$logPath = "C:\Users\impro\.openclaw\workspace\opportunity-research\scheduler-log.txt"

Write-Host "Setting up daily research schedule..." -ForegroundColor Cyan

# Create the scheduled task
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`" -ResearchMode prompted"

# Run daily at 09:00 AM
trigger = New-ScheduledTaskTrigger -Daily -At 09:00

# Run whether user is logged on or not, with highest privileges
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Settings: Wake computer, run immediately if missed
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

# Register the task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
    Write-Host "✅ Scheduled task created: $taskName" -ForegroundColor Green
    Write-Host "   Runs daily at 09:00" -ForegroundColor Green
    Write-Host "   Mode: Prompted (waits for your confirmation)" -ForegroundColor Green
    
    # Log setup
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[$timestamp] Scheduled task created: Daily at 09:00" | Out-File -Append -FilePath $logPath
    
    Write-Host ""
    Write-Host "To modify or remove:" -ForegroundColor Yellow
    Write-Host "  View: Task Scheduler > Task Scheduler Library > $taskName"
    Write-Host "  Remove: Unregister-ScheduledTask -TaskName $taskName -Confirm:`$false"
} catch {
    Write-Host "❌ Failed to create scheduled task: $_" -ForegroundColor Red
}
