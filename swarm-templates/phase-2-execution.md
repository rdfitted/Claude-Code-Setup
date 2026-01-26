# Phase 2: Worker Execution

## Overview

Planners spawn workers sequentially based on task dependencies. Workers execute their tasks and log completion.

---

## ⏱️ CRITICAL: Model Timing - READ FIRST

**Different models have VASTLY different startup times. DO NOT assume a worker is stuck.**

| Worker | Model | Startup Time | Expected Total |
|--------|-------|--------------|----------------|
| Worker 1{X} | Cursor CLI (Opus) | 30-60s | 2-5 min |
| Worker 2{X} | **Gemini** | **60-90s** | **3-8 min** |
| Worker 3{X} | Grok | 10s | 1-3 min |
| Worker 4{X} | **Codex** | **90-120s** | **5-15 min** |

### Patience Rules

1. **Gemini (Worker 2{X})**: Wait at least **3 minutes** before first log check. It initializes slowly.
2. **Codex (Worker 4{X})**: Wait at least **5 minutes** before first log check. Codex is **slow throughout** - not just startup. Log updates may be 2-3 minutes apart even during active work. This is deliberate, methodical execution, NOT a hang.
3. **Do NOT respawn** unless worker shows no activity for:
   - Gemini: 8 minutes
   - Codex: 12 minutes
   - Others: 5 minutes

### Recommended Polling Pattern

```powershell
# For Gemini/Codex workers - patient polling
$maxWait = 600  # 10 minutes for Gemini, 15 for Codex
$interval = 60  # Check every 60 seconds
$elapsed = 0

while ($elapsed -lt $maxWait) {
    Start-Sleep -Seconds $interval
    $elapsed += $interval
    $result = Select-String -Path 'worker-log.log' -Pattern 'COMPLETED' -Quiet
    if ($result) { break }
    Write-Host "[$elapsed s] Still waiting for worker..."
}
```

---

## For Planners

### Input Files
- `tasks/planner-{X}/tasks.json` - Your task breakdown
- `docs/spawn-templates.md` - Spawn commands
- `docs/log-protocol.md` - How to log

### Execution Order

Workers have dependencies. Spawn in order:

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Worker 1{X} + Worker 2{X}                           │
│         (parallel if no dependencies between them)          │
│                                                             │
│ Step 2: Wait for both COMPLETED                             │
├─────────────────────────────────────────────────────────────┤
│ Step 3: Worker 3{X} (coherence)                             │
│         Needs 1{X} + 2{X} output to verify consistency      │
│                                                             │
│ Step 4: Wait for COMPLETED                                  │
├─────────────────────────────────────────────────────────────┤
│ Step 5: Worker 4{X} (simplify)                              │
│         Needs 3{X} coherence fixes before cleanup           │
│                                                             │
│ Step 6: Wait for COMPLETED                                  │
└─────────────────────────────────────────────────────────────┘
```

### Spawning Workers

For each worker:

1. **Get spawn command** from `docs/spawn-templates.md`
2. **Replace placeholders**: `{SESSION_ID}`, `{MPROCS_PORT}`, `{X}`
3. **Run via Bash tool**
4. **Monitor log** for COMPLETED

### Example Spawn Sequence

**Step 1a: Spawn Worker 1{X} (Cursor CLI - Opus 4.5)**

Write spawn .bat file:
```powershell
Set-Content -Path ".swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-1{X}.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-1{X}-task.md and execute.\\\"\", \"name\": \"worker-1{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

Execute:
```bash
.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-1{X}.bat
```

**Step 1b: Spawn Worker 2{X} (parallel - Gemini)**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "gemini -m gemini-3-pro-preview -y -i \"Read .swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-2{X}-task.md and execute.\"", "name": "worker-2{X}"}'
```

### Checking Completion

```powershell
# Check Worker 1{X}
Select-String -Path '.swarm/sessions/{SESSION_ID}/logs/worker-1{X}.log' -Pattern 'COMPLETED'

# Check Worker 2{X}
Select-String -Path '.swarm/sessions/{SESSION_ID}/logs/worker-2{X}.log' -Pattern 'COMPLETED'
```

**Wait for BOTH before spawning Worker 3{X}.**

### Handling Worker Failures

**⚠️ PATIENCE FIRST**: Workers are NOT stuck just because they're quiet.

| Worker | Model | Wait THIS LONG before considering "stuck" |
|--------|-------|-------------------------------------------|
| Worker 1{X} | Cursor/Opus | 5 minutes |
| Worker 2{X} | **Gemini** | **8 minutes** (slow startup is NORMAL) |
| Worker 3{X} | Grok | 5 minutes |
| Worker 4{X} | **Codex** | **12 minutes** (slow but thorough) |

**Only if worker is truly stuck** (no log updates after the times above):

1. Check their log for actual errors (not just silence)
2. Log your decision: "Worker 2a no activity for 10 minutes, respawning"
3. Remove process:
   ```bash
   mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "remove-proc", "name": "worker-{N}{X}"}'
   ```
4. Update task file if needed
5. Respawn

**DO NOT respawn Gemini or Codex workers just because they're slow.** This wastes resources and restarts the slow initialization.

**Codex specifically**: Sparse log updates (2-3 min gaps) are NORMAL. Codex is deliberate and methodical. It's working, not stuck. Only respawn if there's an actual error in the log.

### Coordination During Execution

**Announce major file modifications** to coordination.log:

```powershell
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/coordination.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] PLANNER-{X}: [TOUCHING] src/api/auth.ts - implementing login\""
```

**Check for Queen directives** periodically:

```powershell
Get-Content '.swarm/sessions/{SESSION_ID}/logs/coordination.log' -Tail 10
```

### Phase 2 Complete (Planner)
- All 4 workers show COMPLETED in their logs
- No unresolved conflicts
- Log: "Phase 2 complete. All workers done."
- Proceed to Phase 3
