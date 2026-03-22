# Health Check Skill - With Ollama Auto-Recovery

Monitor system health and **automatically restart Ollama** if it gets stuck. Designed for hands-off operation.

## Quick Start

```bash
# Check everything including Ollama
healthcheck run

# Check and auto-fix Ollama if stuck
healthcheck check ollama

# Check all components
healthcheck check all
```

## Features

- **🔧 Auto-Restart Ollama:** Detects when local LLM is stuck and restarts it automatically
- **🌐 Gateway Monitor:** Checks if OpenClaw gateway is running
- **💾 System Resources:** CPU, memory, disk usage monitoring
- **📊 Light Resource Usage:** Uses `llama3` model for health checks (faster, lighter)
- **📝 Detailed Logging:** Everything logged to `%TEMP%\healthcheck.log`

## Auto-Recovery Behavior

When the cron job runs (every 10 minutes):

1. **Test Ollama:** Tries to connect to `localhost:11434/api/version`
2. **If stuck:** Kills all `ollama` processes and restarts `ollama serve`
3. **Wait for ready:** Polls up to 60 seconds for Ollama to respond
4. **Log result:** Success or failure written to log

## Commands

### Manual Check
```powershell
# Full system check
.\healthcheck.ps1

# Just Ollama with auto-fix
.\healthcheck.ps1 -Component "ollama" -AutoFix:$true

# No auto-fix (just report)
.\healthcheck.ps1 -Component "ollama" -AutoFix:$false
```

### Check Specific Component
```powershell
.\healthcheck.ps1 -Component "gateway"
.\healthcheck.ps1 -Component "disk"
.\healthcheck.ps1 -Component "memory"
.\healthcheck.ps1 -Component "cpu"
```

## Scheduled Checks

**Ollama Recovery Check** runs every **10 minutes**:
- Uses lightweight `llama3` model (not your main `kimi-k2.5`)
- No Telegram notifications (silent operation)
- Logs to: `%TEMP%\healthcheck.log`

View logs:
```powershell
Get-Content $env:TEMP\healthcheck.log -Tail 50
```

## Output

```
2026-03-18 17:45:57 [INFO] === Health Check Started (AutoFix: True) ===
2026-03-18 17:45:57 [INFO] Checking Ollama...
2026-03-18 17:45:57 [SUCCESS] ✅ Ollama: Running and responsive (PID 3816)
2026-03-18 17:45:57 [INFO] Status: HEALTHY
```

If Ollama was stuck and restarted:
```
2026-03-18 17:40:12 [ERROR] ❌ Ollama: Process exists but not responding (stuck)
2026-03-18 17:40:12 [WARN] Attempting to restart Ollama...
2026-03-18 17:40:12 [INFO] Found 1 ollama process(es), stopping...
2026-03-18 17:40:15 [SUCCESS] Ollama serve started
2026-03-18 17:40:25 [SUCCESS] Ollama is now responsive
```

## Log Rotation

Logs automatically rotate when they exceed 10MB. Old logs saved as `healthcheck.log.old`.

## Troubleshooting

**Ollama keeps getting stuck:**
- Check available memory: `healthcheck check memory`
- Consider switching to a smaller model like `llama3` for less resource usage

**Health check not running:**
- Check cron jobs: `openclaw cron list`
- View job runs: `openclaw cron runs <job-id>`

**Manual restart needed:**
```powershell
# Kill stuck Ollama
Get-Process ollama | Stop-Process -Force

# Restart
ollama serve

# Then restart OpenClaw gateway
openclaw gateway restart
```
