---
description: EXPERIMENTAL - Hive using Cursor CLI for Opus agents (Queen, Worker-1, Resolver)
argument-hint: "{session-name}" [worker-count]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob]
---

# Hive Experimental - Cursor CLI for Opus Agents

Same as `/hive` but uses **Cursor CLI** instead of Claude Code for all Opus 4.5 agents:
- Queen
- Worker 1 (Backend/Architecture)
- Resolver
- Code Quality agents

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

## Changes from Standard /hive

### Queen Spawn (mprocs.yaml)

```yaml
queen:
  cmd: ["cmd", "/c", "wsl", "-d", "Ubuntu", "/root/.local/bin/agent", "--force", "You are the QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md and execute."]
  cwd: "{PROJECT_ROOT_WINDOWS}"
```

### Worker/Resolver Spawns (via .bat files)

Queen creates `.bat` files in the session directory and executes them:

**spawn-worker1.bat:**
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read .hive/sessions/{SESSION_ID}/worker-1-task.md and execute.\\\"\", \"name\": \"worker-1\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**spawn-resolver.bat:**
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read .hive/sessions/{SESSION_ID}/resolver-task.md and execute.\\\"\", \"name\": \"resolver\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

---

## Full Workflow

Follow all steps from `/hive` but with these modifications:

### Step 9: Generate mprocs.yaml (MODIFIED)

```yaml
# Experimental Hive - Cursor CLI for Opus agents
# Session: {SESSION_ID}

server: 127.0.0.1:{MPROCS_PORT}

procs:
  queen:
    cmd: ["cmd", "/c", "wsl", "-d", "Ubuntu", "/root/.local/bin/agent", "--force", "You are the QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md and execute."]
    cwd: "{PROJECT_ROOT_WINDOWS}"
    env:
      HIVE_ROLE: "queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Get-ChildItem .hive/sessions/{SESSION_ID} -Filter *.log -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('=== ' + $_.Name + ' ===') -ForegroundColor Cyan; Get-Content $_.FullName -Tail 8 -ErrorAction SilentlyContinue }; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS}"
```

### Step 7: Generate Queen Prompt (MODIFIED - .bat file approach)

```markdown
# Queen Agent - Cursor CLI Hive

You are the **Queen** orchestrating a Cursor CLI hive.

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/queen.log
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}

## Spawn Commands (.bat file approach)

**IMPORTANT**: To spawn workers, create a `.bat` file and execute it. This avoids shell quoting issues.

### Spawning Cursor CLI Agents (Worker 1, Resolver, Code Quality)

**Step 1: Write the .bat file**

Write to `.hive/sessions/{SESSION_ID}/spawn-worker1.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read .hive/sessions/{SESSION_ID}/worker-1-task.md and execute.\\\"\", \"name\": \"worker-1\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**Step 2: Execute the .bat file (from WSL)**
```bash
cmd.exe /c "{PROJECT_ROOT_WINDOWS}\\.hive\\sessions\\{SESSION_ID}\\spawn-worker1.bat"
```

**Note**: You're running in WSL, so use `cmd.exe /c` to execute Windows .bat files.

### Spawning Other CLI Agents (Gemini, OpenCode, Codex)

These can use direct mprocs commands (quoting is simpler):

**Worker 2 (Gemini):**
Write to `.hive/sessions/{SESSION_ID}/spawn-worker2.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"gemini -m gemini-3-pro-preview -y -i \\\"Read .hive/sessions/{SESSION_ID}/worker-2-task.md and execute.\\\"\", \"name\": \"worker-2\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**Worker 3 (OpenCode Grok):**
Write to `.hive/sessions/{SESSION_ID}/spawn-worker3.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"opencode -m opencode/grok-code --prompt \\\"Read .hive/sessions/{SESSION_ID}/worker-3-task.md and execute.\\\"\", \"name\": \"worker-3\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\", \"env\": {\"OPENCODE_YOLO\": \"true\"}}"
```

**Worker 4 (Codex):**
Write to `.hive/sessions/{SESSION_ID}/spawn-worker4.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \\\"Read .hive/sessions/{SESSION_ID}/worker-4-task.md and execute.\\\"\", \"name\": \"worker-4\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**Resolver (Cursor CLI):**
Write to `.hive/sessions/{SESSION_ID}/spawn-resolver.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read .hive/sessions/{SESSION_ID}/resolver-task.md and execute.\\\"\", \"name\": \"resolver\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**Code Quality (Cursor CLI):**
Write to `.hive/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read .hive/sessions/{SESSION_ID}/code-quality-{N}-task.md and execute.\\\"\", \"name\": \"code-quality-{N}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

## Workflow

1. Write spawn .bat files to session directory
2. Execute them in order (worker-1, worker-2 parallel, then worker-3, worker-4 sequential)
3. Monitor logs for COMPLETED
4. Spawn reviewers, then resolver, then tester
```

---

## Agent Distribution

| Agent | CLI | Model | Spawn Method |
|-------|-----|-------|--------------|
| Queen | **Cursor CLI** | Opus 4.5 | mprocs.yaml |
| Worker 1 | **Cursor CLI** | Opus 4.5 | .bat file |
| Worker 2 | Gemini | gemini-3-pro-preview | .bat file |
| Worker 3 | OpenCode | grok-code | .bat file |
| Worker 4 | Codex | gpt-5.2 | .bat file |
| Reviewer BigPickle | OpenCode | big-pickle | .bat file |
| Reviewer Grok | OpenCode | grok-code | .bat file |
| Resolver | **Cursor CLI** | Opus 4.5 | .bat file |
| Tester | Codex | gpt-5.2 | .bat file |
| Code Quality | **Cursor CLI** | Opus 4.5 | .bat file |

---

## Path Format Notes

- **PROJECT_ROOT_WINDOWS**: `C:\Users\USERNAME\Project` (for mprocs.yaml cwd)
- **PROJECT_ROOT_FORWARD_SLASH**: `C:/Users/USERNAME/Project` (for .bat file JSON)

---

## Usage

```bash
/hive-experimental "test-session"     # Test with 4 workers
/hive-experimental "quick-test" 2     # Minimal test with 2 workers
```

## Notes

- Cursor CLI uses a **global model setting** - all Cursor windows share Opus 4.5
- `--force` flag enables auto-approval (like Claude's `--dangerously-skip-permissions`)
- .bat file approach is required to avoid shell quoting issues with mprocs
- If you need different models, use the standard `/hive` command
- **WSL interop must be enabled** - Queen runs in WSL and needs `cmd.exe` access to execute .bat files

## WSL Interop Setup (if needed)

If Queen can't execute .bat files, enable WSL interop:

```bash
# In WSL Ubuntu, create /etc/wsl.conf:
echo -e '[interop]\nenabled = true\nappendWindowsPath = true' | sudo tee /etc/wsl.conf

# Then restart WSL from Windows:
wsl --shutdown
```
