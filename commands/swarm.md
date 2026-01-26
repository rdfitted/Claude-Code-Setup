---
description: Launch hierarchical multi-agent swarm with Planners orchestrating mini-hives under Queen
argument-hint: "{session-name}" [planner-count]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
---

# Swarm - Hierarchical Multi-Agent Orchestration

Launch multiple mini-hives, each led by a **Planner** (Opus 4.5), orchestrated by a **Queen** who handles final code review and PR pushing.

## Architecture

```
Queen (Opus 4.5) → Planners (Opus 4.5) → Workers (mixed models)
```

## Arguments

- `{session-name}`: Name for this session (required, kebab-case)
- `[planner-count]`: Number of Planners (optional, default: 2, max: 4)

---

## Step 1: Check Prerequisites

```bash
mprocs --version
```

If fails: "Install mprocs: `scoop install mprocs` or `npm install -g mprocs`" - STOP.

## Step 2: Generate Session Variables

```bash
TIMESTAMP=$(powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'")
PROJECT_ROOT_WINDOWS=$(powershell -NoProfile -Command "(Get-Location).Path")
MPROCS_PORT=$((4000 + ${TIMESTAMP: -4}))
SESSION_ID="${TIMESTAMP}-{SESSION_NAME}"
```

## Step 3: Create Session Directory

```bash
mkdir -p ".swarm/sessions/{SESSION_ID}/docs"
mkdir -p ".swarm/sessions/{SESSION_ID}/phases"
mkdir -p ".swarm/sessions/{SESSION_ID}/state"
mkdir -p ".swarm/sessions/{SESSION_ID}/tasks/planner-a"
mkdir -p ".swarm/sessions/{SESSION_ID}/tasks/planner-b"
mkdir -p ".swarm/sessions/{SESSION_ID}/logs"
```

## Step 4: Copy Templates

Copy from `~/.claude/swarm-templates/` to session folder:

**To `docs/`:**
- `model-selection.md`
- `spawn-templates.md` (replace `{SESSION_ID}` and `{MPROCS_PORT}`)
- `log-protocol.md` (replace `{SESSION_ID}`)

**To `phases/`:**
- `phase-1-planning.md`
- `phase-2-execution.md`
- `phase-3-review.md`
- `phase-4-integration.md`
- `phase-5-commit.md`

(Replace placeholders in all files)

## Step 5: Pre-Scan (3 OpenCode Agents)

Launch in parallel via Task tool:

**Agent 1 - Architecture (BigPickle):**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle "Scan codebase for: {TASK}. Return architecture patterns, key modules, critical files."
```

**Agent 2 - Organization (GLM 4.7):**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Analyze codebase for: {TASK}. Return code organization, high coupling files, config files."
```

**Agent 3 - Entry Points (Grok):**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "Scout codebase for: {TASK}. Return entry points, test files, package definitions."
```

Merge results → write to `state/prescan-results.md`

## Step 6: Learning Scout (GLM 4.7)

```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Extract learnings from .ai-docs/ for: {TASK}. Output: ---SESSION-GUIDELINES-START--- ... ---SESSION-GUIDELINES-END---"
```

Write to `state/session-guidelines.md`

## Step 7: Define Responsibilities

Analyze task and assign domains to Planners.

Write to `state/responsibility-matrix.md`:

```markdown
## Swarm Responsibility Matrix

### Task
{FULL_TASK_DESCRIPTION}

### Planner A - {DOMAIN_A}
**Domain**: {description}
**Scope**: {high-level areas}

### Planner B - {DOMAIN_B}
**Domain**: {description}
**Scope**: {high-level areas}

### Cross-Cutting Concerns
{list}
```

## Step 8: File Scouts (2 per domain)

For each Planner domain, spawn GLM + Grok scouts to identify file ownership.

Merge results → write to `state/file-ownership.md`:

```markdown
# File Ownership

## Planner A - {DOMAIN_A}
### Exclusive Files
- path/to/file.ts

## Planner B - {DOMAIN_B}
### Exclusive Files
- path/to/file.ts

## Shared Files
| File | Owned By | Notes |
|------|----------|-------|
```

## Step 9: Write Context

Write to `state/context.md`:

```markdown
# Task Context

## Description
{FULL_TASK_FROM_USER}

## Pre-Scan Summary
{KEY_FINDINGS}

## Session
- ID: {SESSION_ID}
- Planners: {PLANNER_COUNT}
```

## Step 10: Generate Queen Prompt (THIN with absolute paths + inlined spawn commands)

Write to `.swarm/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen

**Role**: Top-level swarm orchestrator.

## Session
- **ID**: {SESSION_ID}
- **Project Root**: {PROJECT_ROOT}
- **Log**: logs/queen.log (relative from project root)
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}
- **Planners**: {PLANNER_COUNT}

## Read for Context (ABSOLUTE PATHS)
1. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/context.md`
2. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/responsibility-matrix.md`
3. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/file-ownership.md`
4. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/session-guidelines.md`
5. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/log-protocol.md`

## Log Protocol
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: {MESSAGE}\""
```

Coordination with Planners:
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/coordination.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: [DIRECTIVE] {MESSAGE}\""
```

---

## SPAWN COMMANDS - EXECUTE VIA BASH TOOL

**CRITICAL**: You MUST use the Bash tool to execute these commands. Do NOT just read them - actually RUN them.

### Spawn Planner A
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-a-prompt.md and execute.\"", "name": "planner-a", "cwd": "{PROJECT_ROOT}"}'
```

### Spawn Planner B
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-b-prompt.md and execute.\"", "name": "planner-b", "cwd": "{PROJECT_ROOT}"}'
```

### Spawn Planner C (if needed)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-c-prompt.md and execute.\"", "name": "planner-c", "cwd": "{PROJECT_ROOT}"}'
```

### Spawn Planner D (if needed)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-d-prompt.md and execute.\"", "name": "planner-d", "cwd": "{PROJECT_ROOT}"}'
```

### Spawn Integration Reviewer (after all Planners complete)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/integration-reviewer-task.md and execute.\"", "name": "integration-reviewer", "cwd": "{PROJECT_ROOT}", "env": {"OPENCODE_YOLO": "true"}}'
```

### Spawn Integration Tester
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/integration-tester-task.md and execute.\"", "name": "integration-tester", "cwd": "{PROJECT_ROOT}"}'
```

---

## Execute Phases

### Phase 1: Write Planner Prompts + Spawn
1. Read context files above
2. Write `planner-{X}-prompt.md` for each Planner
3. **USE BASH TOOL** to execute SPAWN COMMANDS above - copy-paste each command exactly

### Phase 2: Monitor Planners
- Watch `logs/planner-*.log` for PLANNER_COMPLETE
- Use `logs/coordination.log` to communicate

### Phase 3: Integration Review
- See `phases/phase-4-integration.md`

### Phase 4: Commit and PR
- See `phases/phase-5-commit.md`

### Phase 5: PR Quality
- See `phases/phase-6-code-quality.md`

## Capabilities
| Action | You Can |
|--------|---------|
| Spawn Planners | YES (use commands above) |
| Monitor all logs | YES |
| Run integration cycle | YES |
| Commit code | YES |
| Push PR | YES (only you) |

## Begin
1. Log STARTED to queen.log
2. Read context files
3. Write Planner prompts
4. Run spawn commands
```

## Step 11: Generate Planner Prompts (THIN with absolute paths + inlined spawn commands)

For each Planner, write to `.swarm/sessions/{SESSION_ID}/planner-{X}-prompt.md`:

```markdown
# Planner {X} - {DOMAIN}

**Role**: Mini-queen for {DOMAIN} domain.

## Session
- **ID**: {SESSION_ID}
- **Project Root**: {PROJECT_ROOT}
- **Log**: logs/planner-{X}.log (relative from project root)
- **Tasks**: tasks/planner-{X}/
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}

## Read for Context (ABSOLUTE PATHS)
1. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/context.md`
2. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/responsibility-matrix.md` - Find your domain
3. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/file-ownership.md` - Find your files
4. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/session-guidelines.md`
5. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/log-protocol.md`

## Log Protocol
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/planner-{X}.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] PLANNER-{X}: {MESSAGE}\""
```

Coordination with Queen:
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/coordination.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] PLANNER-{X}: [STATUS] {MESSAGE}\""
```

---

## SPAWN COMMANDS - EXECUTE VIA BASH TOOL

**CRITICAL**: You MUST use the Bash tool to execute these commands. Do NOT just read them - actually RUN them.

### Worker 1{X} - Backend (Cursor CLI - Opus 4.5)

**Step 1: Write spawn .bat file**
```powershell
Set-Content -Path ".swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-1{X}.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-1{X}-task.md and execute.\\\"\", \"name\": \"worker-1{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

**Step 2: Execute**
```bash
.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-1{X}.bat
```

### Worker 2{X} - Frontend (Gemini)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "gemini -m gemini-3-pro-preview -y -i \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-2{X}-task.md and execute.\"", "name": "worker-2{X}", "cwd": "{PROJECT_ROOT}"}'
```

### Worker 3{X} - Coherence (Grok)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-3{X}-task.md and execute.\"", "name": "worker-3{X}", "cwd": "{PROJECT_ROOT}", "env": {"OPENCODE_YOLO": "true"}}'
```

### Worker 4{X} - Simplify (Codex)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-4{X}-task.md and execute.\"", "name": "worker-4{X}", "cwd": "{PROJECT_ROOT}"}'
```

### Reviewer {X} (after workers complete)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/reviewer-{X}-task.md and execute.\"", "name": "reviewer-{X}", "cwd": "{PROJECT_ROOT}", "env": {"OPENCODE_YOLO": "true"}}'
```

### Tester {X}
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/tester-{X}-task.md and execute.\"", "name": "tester-{X}", "cwd": "{PROJECT_ROOT}"}'
```

---

## Execute Phases

### Phase 1: Break Domain into Tasks
1. Read context files above
2. Break your domain into 2-4 worker tasks
3. Write task files to `tasks/planner-{X}/` (use relative paths in task content)

### Phase 2: Spawn Workers
1. Spawn workers SEQUENTIALLY (wait for dependencies)
2. **USE BASH TOOL** to execute SPAWN COMMANDS above - copy-paste each command exactly
3. Monitor worker logs for COMPLETED

### Phase 3: Review Cycle
1. When all workers complete, spawn Reviewer + Tester
2. Address any issues found
3. Log PLANNER_COMPLETE to coordination.log

## Capabilities
| Action | You Can |
|--------|---------|
| Break down tasks | YES |
| Write worker task files | YES |
| Spawn workers | YES (use commands above) |
| Run review cycle | YES |
| Commit code | YES |
| Push PR | NO (Queen only) |

## Begin
1. Log STARTED to planner-{X}.log
2. Read context files
3. Execute Phase 1
```

## Step 12: Generate tasks.json

Write to `state/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "planners": {PLANNER_COUNT},
  "planner_domains": {
    "a": "{DOMAIN_A}",
    "b": "{DOMAIN_B}"
  }
}
```

## Step 13: Create Empty Logs

```bash
type nul > ".swarm/sessions/{SESSION_ID}/logs/queen.log"
type nul > ".swarm/sessions/{SESSION_ID}/logs/coordination.log"
type nul > ".swarm/sessions/{SESSION_ID}/logs/planner-a.log"
type nul > ".swarm/sessions/{SESSION_ID}/logs/planner-b.log"
```

## Step 14: Generate mprocs.yaml

**IMPORTANT**: Use absolute paths so mprocs can find files regardless of working directory.

Write to `.swarm/mprocs.yaml`:

```yaml
server: 127.0.0.1:{MPROCS_PORT}

procs:
  queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "Read {PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\queen-prompt.md and execute."]
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

## Step 15: Launch mprocs

```bash
powershell -Command "Start-Process powershell -WorkingDirectory '{PROJECT_ROOT_WINDOWS}' -ArgumentList '-NoExit', '-Command', 'mprocs --config .swarm/mprocs.yaml'"
```

## Step 16: Output Status

```markdown
## Swarm Launched!

**Session**: {SESSION_ID}
**Planners**: {PLANNER_COUNT}
**Path**: .swarm/sessions/{SESSION_ID}/

### Architecture
```
Queen (Opus)
├── Planner A ({DOMAIN_A}) → Workers 1a-4a, Reviewer, Tester
└── Planner B ({DOMAIN_B}) → Workers 1b-4b, Reviewer, Tester
```

### Session Structure
```
.swarm/sessions/{SESSION_ID}/
├── docs/           # Reference docs (model selection, spawn templates)
├── phases/         # Phase instructions
├── state/          # Current state (responsibilities, file ownership)
├── tasks/          # Generated task files
├── logs/           # Agent logs
└── *-prompt.md     # Thin agent prompts
```

### Key Files
- `state/responsibility-matrix.md` - Domain assignments
- `state/file-ownership.md` - Who owns which files
- `logs/coordination.log` - Queen ↔ Planner communication

mprocs opened in new window. Watch the swarm coordinate!
```

---

## Usage

```bash
/swarm "big-refactor"         # 2 Planners
/swarm "full-rewrite" 4       # 4 Planners
```
