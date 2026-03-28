## Shell Command Issue Investigation — 2026-03-28
**Time:** 11:01-11:03 UTC
**Problem:** `exec` tool not returning output
**Context:** Started March 27 during V24 → V15 transition

### What Works:
- ✅ User runs commands directly — returns output
- ✅ File read/write — functional
- ✅ Gateway running stable
- ✅ Telegram/Discord messaging

### What Doesn't Work:
- ❌ Agent `exec` calls — no output returned
- ❌ Shell commands from agent session — silent failure

### Configuration Checked:
- ✅ `tools.profile`: "coding" (allows exec)
- ✅ Gateway: running on port 18001
- ✅ Auth: token configured
- ✅ Session: webchat connected

### Hypothesis:
The agent session may be in **embedded mode** (direct Ollama connection) rather than **gateway mode** (full tool bridge). In embedded mode, tools like `exec` that require host system access may be restricted for security.

### Evidence:
- Logs show "embedded run" entries
- No exec error messages in logs (silent failure)
- Gateway is running but agent isn't using it for tools

### Potential Fixes:
1. **Restart session** — Force reconnection to gateway
2. **Check session mode** — Verify not in restricted embedded mode
3. **Gateway service mode** — Running as service may limit interactive tools
4. **Tool profile** — Verify "coding" profile allows exec on this host

### Next Step:
Need to determine if this is a **security restriction** (by design) or a **session bug** (needs fix).

---
*Documented by: Lumina*
*Time: 2026-03-28 11:03 UTC*
