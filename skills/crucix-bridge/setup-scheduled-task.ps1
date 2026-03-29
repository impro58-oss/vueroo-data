# Crucix Auto-Update Scheduled Task
# Run this in PowerShell as Administrator

$Action = New-ScheduledTaskAction -Execute "C:\Users\impro\.openclaw\workspace\skills\crucix-bridge\crucix-update.bat"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 3650)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "Crucix-Auto-Update" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "Updates Crucix intelligence data every 15 minutes"

Write-Host "Task 'Crucix-Auto-Update' created successfully"
Write-Host "Runs every 15 minutes"
Write-Host "Data output: C:\Users\impro\.openclaw\workspace\vueroo-portal\public\data\crucix_feed.json"
