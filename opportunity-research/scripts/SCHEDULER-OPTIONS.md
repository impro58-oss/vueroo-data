# Alternative: Cron-based approach (if preferred)
# Or manual daily trigger via command

## Quick Commands:

### Trigger research session manually:
```powershell
& "C:\Users\impro\.openclaw\workspace\opportunity-research\scripts\daily-research-trigger.ps1" -ResearchMode manual
```

### View scheduled task:
```powershell
Get-ScheduledTask -TaskName "OpenClaw-Daily-Research" | Get-ScheduledTaskInfo
```

### Disable scheduled task:
```powershell
Disable-ScheduledTask -TaskName "OpenClaw-Daily-Research"
```

### Enable scheduled task:
```powershell
Enable-ScheduledTask -TaskName "OpenClaw-Daily-Research"
```

### Remove scheduled task:
```powershell
Unregister-ScheduledTask -TaskName "OpenClaw-Daily-Research" -Confirm:$false
```

---

## Alternative: OpenClaw Cron (if configured)

Add to OpenClaw cron:
```
0 9 * * * cd /workspace/opportunity-research && python3 scripts/daily-trigger.py
```

---

## Manual Daily Workflow (No automation)

1. Open terminal at 09:00
2. Navigate to opportunity-research
3. Review yesterday's offshoots
4. Run research session
5. Update logs and commit

*Choose your preferred method above*
