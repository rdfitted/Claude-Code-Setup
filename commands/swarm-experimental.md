---
description: EXPERIMENTAL - Swarm using Cursor CLI for Opus agents (Queen, Planners, Resolvers)
argument-hint: "{session-name}" [planner-count]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
---

# Swarm Experimental - Cursor CLI for Opus Agents

Same as `/swarm` but uses **Cursor CLI** instead of Claude Code for all Opus 4.5 agents:
- Queen
- All Planners (A, B, C, D)
- Worker 1X (Backend workers)
- Resolver per Planner
- Integration Resolver

**Purpose**: Reduce Claude Code usage by offloading Opus workloads to Cursor CLI.

## Cursor CLI Spawn Pattern (WORKING)

**Use .bat files to avoid shell quoting issues:**

```batch
@echo off
mprocs --server 127.0.0.1:{PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"PROMPT\\\"\", \"name\": \"agent-name\", \"cwd\": \"C:/Path/To/Project\"}"
```

**Key points:**
- Write spawn command to `.bat` file
- Use double quotes for JSON with `\"`
- Triple-escape inner quotes: `\\\"`
- Add `--force` flag for auto-approval
- Execute the `.bat` file

---

## Changes from Standard /swarm

### Queen Spawn (mprocs.yaml)

```yaml
queen:
  cmd: ["cmd", "/c", "wsl", "-d", "Ubuntu", "/root/.local/bin/agent", "--force", "Read {PROJECT_ROOT}\\.swarm\\sessions\\{SESSION_ID}\\queen-prompt.md and execute."]
  cwd: "{PROJECT_ROOT_WINDOWS}"
```

### Planner/Resolver Spawns (via .bat files)

Queen and Planners create `.bat` files and execute them.

---

## Full Workflow

Follow all steps from `/swarm` but with these modifications:

### Step 14: Generate mprocs.yaml (MODIFIED)

```yaml
server: 127.0.0.1:{MPROCS_PORT}

procs:
  queen:
    cmd: ["cmd", "/c", "wsl", "-d", "Ubuntu", "/root/.local/bin/agent", "--force", "Read {PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\queen-prompt.md and execute."]
    cwd: "{PROJECT_ROOT_WINDOWS}"
    env:
      SWARM_SESSION: "{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}"

  coordination:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== COORDINATION ===' -ForegroundColor Green; Get-Content '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\logs\\coordination.log' -Tail 25 -ErrorAction SilentlyContinue; Start-Sleep 2 }"]
    cwd: "{PROJECT_ROOT_WINDOWS}"

  logs:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== LOGS ===' -ForegroundColor Cyan; Get-Content '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\logs\\queen.log' -Tail 3 -ErrorAction SilentlyContinue; Get-ChildItem '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\logs\\planner-*.log' | ForEach-Object { Write-Host $_.BaseName -ForegroundColor Yellow; Get-Content $_.FullName -Tail 2 -ErrorAction SilentlyContinue }; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS}"
```

### Step 10: Generate Queen Prompt (MODIFIED - .bat file approach)

Include these spawn templates in the Queen prompt:

```markdown
## Spawn Commands (.bat file approach)

**IMPORTANT**: To spawn agents, create a `.bat` file and execute it via `cmd.exe`. This avoids shell quoting issues.

**Execute .bat files from WSL:**
```bash
cmd.exe /c "{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\spawn-planner-a.bat"
```

### Spawning Planners (Cursor CLI)

**Planner A:**
Write to `.swarm/sessions/{SESSION_ID}/spawn-planner-a.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/planner-a-prompt.md and execute.\\\"\", \"name\": \"planner-a\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**Planner B:**
Write to `.swarm/sessions/{SESSION_ID}/spawn-planner-b.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/planner-b-prompt.md and execute.\\\"\", \"name\": \"planner-b\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**Planner C (if needed):**
Write to `.swarm/sessions/{SESSION_ID}/spawn-planner-c.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/planner-c-prompt.md and execute.\\\"\", \"name\": \"planner-c\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**Planner D (if needed):**
Write to `.swarm/sessions/{SESSION_ID}/spawn-planner-d.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/planner-d-prompt.md and execute.\\\"\", \"name\": \"planner-d\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

### Integration Agents

**Integration Reviewer (OpenCode BigPickle):**
Write to `.swarm/sessions/{SESSION_ID}/spawn-integration-reviewer.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"opencode -m opencode/big-pickle --prompt \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/integration-reviewer-task.md and execute.\\\"\", \"name\": \"integration-reviewer\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\", \"env\": {\"OPENCODE_YOLO\": \"true\"}}"
```

**Integration Tester (Codex):**
Write to `.swarm/sessions/{SESSION_ID}/spawn-integration-tester.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/integration-tester-task.md and execute.\\\"\", \"name\": \"integration-tester\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**Integration Resolver (Cursor CLI):**
Write to `.swarm/sessions/{SESSION_ID}/spawn-integration-resolver.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/integration-resolver-task.md and execute.\\\"\", \"name\": \"integration-resolver\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```
```

### Step 11: Generate Planner Prompts (MODIFIED - .bat file approach)

Include these spawn templates in each Planner prompt:

```markdown
## Spawn Commands (.bat file approach)

### Worker 1{X} - Backend (Cursor CLI)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-1{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-1{X}-task.md and execute.\\\"\", \"name\": \"worker-1{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

### Worker 2{X} - Frontend (Gemini)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-2{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"gemini -m gemini-3-pro-preview -y -i \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-2{X}-task.md and execute.\\\"\", \"name\": \"worker-2{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

### Worker 3{X} - Coherence (OpenCode Grok)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-3{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"opencode -m opencode/grok-code --prompt \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-3{X}-task.md and execute.\\\"\", \"name\": \"worker-3{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\", \"env\": {\"OPENCODE_YOLO\": \"true\"}}"
```

### Worker 4{X} - Simplify (Codex)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-4{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-4{X}-task.md and execute.\\\"\", \"name\": \"worker-4{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

### Reviewer {X} (OpenCode BigPickle)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-reviewer-{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"opencode -m opencode/big-pickle --prompt \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/reviewer-{X}-task.md and execute.\\\"\", \"name\": \"reviewer-{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\", \"env\": {\"OPENCODE_YOLO\": \"true\"}}"
```

### Resolver {X} (Cursor CLI)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-resolver-{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/resolver-{X}-task.md and execute.\\\"\", \"name\": \"resolver-{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

### Tester {X} (Codex)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-tester-{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/tester-{X}-task.md and execute.\\\"\", \"name\": \"tester-{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```
```

---

## Agent Distribution

| Agent | CLI | Model | Spawn Method |
|-------|-----|-------|--------------|
| Queen | **Cursor CLI** | Opus 4.5 | mprocs.yaml |
| Planner A-D | **Cursor CLI** | Opus 4.5 | .bat file |
| Worker 1X | **Cursor CLI** | Opus 4.5 | .bat file |
| Worker 2X | Gemini | gemini-3-pro-preview | .bat file |
| Worker 3X | OpenCode | grok-code | .bat file |
| Worker 4X | Codex | gpt-5.2 | .bat file |
| Reviewer X | OpenCode | big-pickle | .bat file |
| Resolver X | **Cursor CLI** | Opus 4.5 | .bat file |
| Tester X | Codex | gpt-5.2 | .bat file |
| Integration Reviewer | OpenCode | big-pickle | .bat file |
| Integration Tester | Codex | gpt-5.2 | .bat file |
| Integration Resolver | **Cursor CLI** | Opus 4.5 | .bat file |

---

## Path Format Notes

- **PROJECT_ROOT_WINDOWS**: `C:\Users\USERNAME\Project` (for mprocs.yaml cwd, use `\\`)
- **PROJECT_ROOT_FORWARD_SLASH**: `C:/Users/USERNAME/Project` (for .bat file JSON cwd)

---

## Usage

```bash
/swarm-experimental "test-session"     # 2 Planners (default)
/swarm-experimental "big-refactor" 4   # 4 Planners
```

## Notes

- Cursor CLI uses a **global model setting** - all Cursor windows share Opus 4.5
- `--force` flag enables auto-approval (like Claude's `--dangerously-skip-permissions`)
- .bat file approach is required to avoid shell quoting issues with mprocs
- This significantly reduces Claude Code usage for large swarm operations
- **WSL interop must be enabled** - Queen/Planners run in WSL and need `cmd.exe` access to execute .bat files

## WSL Interop Setup (if needed)

If agents can't execute .bat files, enable WSL interop:

```bash
# In WSL Ubuntu, create /etc/wsl.conf:
echo -e '[interop]\nenabled = true\nappendWindowsPath = true' | sudo tee /etc/wsl.conf

# Then restart WSL from Windows:
wsl --shutdown
```
