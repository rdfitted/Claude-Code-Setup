# Spawn Templates

**Placeholders to replace:**
- `{SESSION_ID}` - Session identifier
- `{MPROCS_PORT}` - mprocs server port
- `{PROJECT_ROOT}` - Absolute path with forward slashes (e.g., `C:/Users/USERNAME/Code Projects/my-project`)
- `{PROJECT_ROOT_WINDOWS}` - Windows path with backslashes (e.g., `C:\Users\USERNAME\Code Projects\my-project`)
- `{X}` - Planner letter (a, b, c, d)

**IMPORTANT**: All spawn commands use ABSOLUTE paths and set `cwd` to ensure agents start in the correct directory.

---

## Spawn Methods

### Method 1: .bat File (RECOMMENDED for Cursor CLI)

Shell quoting with mprocs is complex. The reliable approach is to write spawn commands to `.bat` files and execute them.

**Pattern:**
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"COMMAND \\\"PROMPT\\\"\", \"name\": \"agent-name\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

**Key escaping rules:**
- Outer JSON uses `\"` for quotes
- Inner prompt uses `\\\"` (triple-escaped)
- Use forward slashes in paths inside JSON

### Method 2: Direct Command (simpler CLIs only)

For CLIs without complex quoting needs (OpenCode, Codex):
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "COMMAND \"PROMPT\"", "name": "agent-name", "cwd": "{PROJECT_ROOT}"}'
```

### Method 3: Execute .bat from WSL (Cursor CLI agents spawning more agents)

When a Cursor CLI agent (running in WSL) needs to spawn other agents, it uses `cmd.exe` to execute the `.bat` file:

```bash
cmd.exe /c "{PROJECT_ROOT_WINDOWS}\\.hive\\sessions\\{SESSION_ID}\\spawn-worker1.bat"
```

**Requirements:**
- WSL interop must be enabled (`/etc/wsl.conf` with `[interop] enabled = true`)
- Use Windows paths with double backslashes in the cmd.exe argument

**Path conversion:**
- `{PROJECT_ROOT}` (forward slashes): `C:/Users/USERNAME/Code Projects/my-project`
- `{PROJECT_ROOT_WINDOWS}` (backslashes): `C:\Users\USERNAME\Code Projects\my-project`
- `{PROJECT_ROOT_WSL}` (WSL mount): `/mnt/c/Users/USERNAME/Code Projects/my-project`

---

## Cursor CLI Spawns (via .bat files)

### Planner (Cursor CLI - Opus 4.5)
Write to `.swarm/sessions/{SESSION_ID}/spawn-planner-{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-{X}-prompt.md and execute.\\\"\", \"name\": \"planner-{X}\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

### Worker 1{X} - Backend (Cursor CLI - Opus 4.5)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-1{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-1{X}-task.md and execute.\\\"\", \"name\": \"worker-1{X}\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

### Resolver {X} (Cursor CLI - Opus 4.5)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-resolver-{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/resolver-{X}-task.md and execute.\\\"\", \"name\": \"resolver-{X}\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

### Integration Resolver (Cursor CLI - Opus 4.5)
Write to `.swarm/sessions/{SESSION_ID}/spawn-integration-resolver.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/integration-resolver-task.md and execute.\\\"\", \"name\": \"integration-resolver\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

---

## Claude Code Spawns (Orchestration Only)

**Note**: Queen and Planners use Claude Code for orchestration. Workers, Resolvers, and Code Quality use Cursor CLI.

### Planner (Claude Opus) - Orchestrates domain workers
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-{X}-prompt.md and execute.\"", "name": "planner-{X}", "cwd": "{PROJECT_ROOT}"}'
```

### Queen (Claude Opus) - Top-level orchestrator
Spawned via mprocs.yaml, not --ctl command.

---

## Gemini Spawns

### Worker 2{X} - Frontend (Gemini Pro)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-2{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"gemini -m gemini-3-pro-preview -y -i \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-2{X}-task.md and execute.\\\"\", \"name\": \"worker-2{X}\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

**Fallback (Flash model):**
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"gemini -m gemini-3-flash-preview -y -i \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-2{X}-task.md and execute.\\\"\", \"name\": \"worker-2{X}\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

---

## OpenCode Spawns

### Worker 3{X} - Coherence (Grok)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-3{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"opencode -m opencode/grok-code --prompt \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-3{X}-task.md and execute.\\\"\", \"name\": \"worker-3{X}\", \"cwd\": \"{PROJECT_ROOT}\", \"env\": {\"OPENCODE_YOLO\": \"true\"}}"
```

### Reviewer {X} (BigPickle)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-reviewer-{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"opencode -m opencode/big-pickle --prompt \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/reviewer-{X}-task.md and execute.\\\"\", \"name\": \"reviewer-{X}\", \"cwd\": \"{PROJECT_ROOT}\", \"env\": {\"OPENCODE_YOLO\": \"true\"}}"
```

### Integration Reviewer (BigPickle)
Write to `.swarm/sessions/{SESSION_ID}/spawn-integration-reviewer.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"opencode -m opencode/big-pickle --prompt \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/integration-reviewer-task.md and execute.\\\"\", \"name\": \"integration-reviewer\", \"cwd\": \"{PROJECT_ROOT}\", \"env\": {\"OPENCODE_YOLO\": \"true\"}}"
```

---

## Codex Spawns

### Worker 4{X} - Simplify (Codex GPT-5.2)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-4{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-4{X}-task.md and execute.\\\"\", \"name\": \"worker-4{X}\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

### Tester {X} (Codex GPT-5.2)
Write to `.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-tester-{X}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/tester-{X}-task.md and execute.\\\"\", \"name\": \"tester-{X}\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

### Integration Tester (Codex GPT-5.2)
Write to `.swarm/sessions/{SESSION_ID}/spawn-integration-tester.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \\\"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/integration-tester-task.md and execute.\\\"\", \"name\": \"integration-tester\", \"cwd\": \"{PROJECT_ROOT}\"}"
```

---

## Pre-Scan Agents (Main Claude runs before mprocs)

### Architecture Scanner (BigPickle)
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle "Scan this codebase for: {TASK_DESCRIPTION}. Identify: 1) Main architecture patterns, 2) Key modules and their relationships, 3) Critical files for this task. Return file paths with brief descriptions."
```

### Organization Scanner (GLM 4.7)
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Analyze this codebase for: {TASK_DESCRIPTION}. Focus on: 1) Code organization patterns, 2) High coupling files, 3) Configuration and environment files. Return file paths with observations."
```

### Entry Points Scanner (Grok Code)
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "Scout this codebase for: {TASK_DESCRIPTION}. Identify: 1) Entry points and main flows, 2) Test files, 3) Package definitions. Return file paths with notes."
```

### File Scout - GLM (per domain)
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "You are a File Scout for domain: {DOMAIN}. Task: {TASK}. Identify files owned by this domain. Output: ---FILE-OWNERSHIP-START--- / ---FILE-OWNERSHIP-END---"
```

### File Scout - Grok (per domain)
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "You are a File Scout for domain: {DOMAIN}. Task: {TASK}. Identify files by architecture patterns. Output: ---FILE-OWNERSHIP-START--- / ---FILE-OWNERSHIP-END---"
```

### Learning Scout (GLM 4.7)
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Extract relevant learnings from .ai-docs/ for: {TASK}. Output: ---SESSION-GUIDELINES-START--- / ---SESSION-GUIDELINES-END---"
```

### Validation Agent (3 per concern)
```bash
# BigPickle
OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle "Search codebase for evidence related to: {CONCERN}. Verdict: VALID (needs work) or MISTAKEN (already implemented)"

# GLM 4.7
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Search codebase for evidence related to: {CONCERN}. Verdict: VALID or MISTAKEN"

# Grok Code
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "Search codebase for evidence related to: {CONCERN}. Verdict: VALID or MISTAKEN"
```

---

## CLI Quick Reference

| CLI | Auto-Approve Flag | Model Flag |
|-----|-------------------|------------|
| Claude Code | `--dangerously-skip-permissions` | `--model opus` |
| Cursor CLI | `--force` | (global setting) |
| Gemini | `-y` | `-m gemini-3-pro-preview` |
| OpenCode | env `OPENCODE_YOLO=true` | `-m opencode/MODEL` |
| Codex | `--dangerously-bypass-approvals-and-sandbox` | `-m gpt-5.2` |
