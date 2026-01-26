---
description: B-Thread - Large-scale refactoring with spawn-on-demand workers, sequential execution, reviewers, resolver, and tester
argument-hint: "<files-or-module-to-refactor>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task, TodoWrite]
---

# Hive Refactor - Spawn-on-Demand Refactoring

Launch a spawn-on-demand hive for large-scale refactoring with sequential workers, reviewers, resolver, and tester.

## Thread Type: B-Thread (Big/Meta)

- **Spawn-on-demand**: Only Queen starts, workers spawned as needed
- **Sequential execution**: Workers run one at a time, each reads previous logs
- **Structured logging**: Decisions, rationale, and ideology passed downstream
- **Review + Resolve**: Reviewers find issues, Resolver addresses them
- **Clean exit**: Commit to PR, comment on difficulties (no infinite loops)

## Arguments

- `<files-or-module-to-refactor>`: Path(s) to refactor (e.g., "src/legacy/", "src/api/*.ts", "the auth module")

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  MAIN CLAUDE (runs /hive-refactor)                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 1. Analyze refactoring scope                                   │  │
│  │ 2. Write task files for each worker                            │  │
│  │ 3. Write queen-prompt.md                                       │  │
│  │ 4. Launch mprocs (Queen only)                                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    QUEEN (Opus 4.5) - Orchestrator                  │
│                                                                     │
│   Phase 1: Sequential Workers (each reads previous logs)            │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                        │
│   │Worker-1 │ → │Worker-2 │ → │Worker-3 │                          │
│   │ Opus    │    │ Gemini  │    │  GLM    │                        │
│   │Backend  │    │Frontend │    │Cohertic │                        │
│   └─────────┘    └─────────┘    └─────────┘                        │
│                                                                     │
│   Phase 2: Reviewers (parallel)                                     │
│   ┌─────────────┐    ┌─────────────┐                               │
│   │ BigPickle   │    │    Grok     │                               │
│   │ Deep Review │    │ Quick Review│                               │
│   └─────────────┘    └─────────────┘                               │
│                                                                     │
│   Phase 3: Resolver                                                 │
│   ┌─────────────────────────────────┐                              │
│   │ Resolver (Opus 4.5)             │                              │
│   │ Reads reviewer logs, fixes all  │                              │
│   └─────────────────────────────────┘                              │
│                                                                     │
│   Phase 4: Tester                                                   │
│   ┌─────────────────────────────────┐                              │
│   │ Tester (Codex GPT-5.2)          │                              │
│   │ Runs tests, fixes failures      │                              │
│   └─────────────────────────────────┘                              │
│                                                                     │
│   Phase 5: Commit + PR + Comments on difficulties                   │
└─────────────────────────────────────────────────────────────────────┘
```

## Team Composition

| Worker | Model | Specialty | Runs After |
|--------|-------|-----------|------------|
| worker-1 | Opus 4.5 | Complex logic, architecture, APIs | - |
| worker-2 | Gemini 3 Pro | Patterns, modern syntax, UI | worker-1 |
| worker-3 | Grok Code | Backend/frontend coherence | worker-2 |
| reviewer-bigpickle | BigPickle | Edge cases, deep analysis | worker-3 |
| reviewer-grok | Grok Code | Quick observations | worker-3 |
| resolver | Opus 4.5 | Address all reviewer findings | reviewers |
| tester | Codex GPT-5.2 | Run tests, fix failures | resolver |

## Workflow

### Step 1: Check Prerequisites

```bash
mprocs --version
git rev-parse --is-inside-work-tree
```

### Step 2: Parse Input & Analyze Scope

```bash
# Count files to refactor
find {REFACTOR_PATH} -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.py" \) | wc -l

# List files
ls -la {REFACTOR_PATH}
```

Extract:
- `REFACTOR_TARGET`: What to refactor
- `FILE_LIST`: All files in scope
- `TOTAL_FILES`: Count of files

### Step 3: Generate Session Variables

```bash
TIMESTAMP=$(powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'")
PROJECT_ROOT_WINDOWS=$(powershell -NoProfile -Command "(Get-Location).Path")
MPROCS_PORT=$((4000 + ${TIMESTAMP: -4}))
SESSION_ID="${TIMESTAMP}-hive-refactor"
BASE_BRANCH=$(git branch --show-current)
```

**CRITICAL - Path Format for mprocs.yaml:**
- mprocs on Windows REQUIRES Windows-style paths with escaped backslashes
- Format in YAML: `"D:\\Code Projects\\MyProject"` (double backslashes)
- NEVER use Git Bash paths like `/d/Code Projects/...`

### Step 4: Create Refactor Branch

```bash
git checkout -b refactor/{SESSION_ID}
```

### Step 5: Create Session Directory

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
mkdir -p ".hive/sessions/{SESSION_ID}/reviews"
mkdir -p ".hive/sessions/{SESSION_ID}/logs"
```

### Step 6: Create tasks.json

Write to `.hive/sessions/{SESSION_ID}/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "B-Thread (Hive Refactor)",
  "refactor": {
    "target": "{REFACTOR_TARGET}",
    "total_files": "{TOTAL_FILES}",
    "branch": "refactor/{SESSION_ID}"
  },
  "base_branch": "{BASE_BRANCH}",
  "workflow": "sequential-with-logging",
  "phases": {
    "workers": ["worker-1", "worker-2", "worker-3"],
    "reviewers": ["reviewer-bigpickle", "reviewer-grok"],
    "resolver": "resolver",
    "tester": "tester"
  }
}
```

### Step 7: Write Worker Task Files

**CRITICAL: Each worker logs decisions/rationale for downstream workers.**

**worker-1-task.md (Backend/Architecture - Opus):**
```markdown
# Worker 1 Task - Backend/Architecture Refactoring

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/worker-1.log

## Refactoring Target
{REFACTOR_TARGET}

## Files in Scope
{FILE_LIST}

## Your Specialty
Complex logic, architecture changes, API redesign, tricky edge cases.

## Structured Logging Protocol

**CRITICAL**: Log your decisions and rationale so downstream workers understand your approach.

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/worker-1.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] WORKER-1: message'"
```

**Required log entries:**
1. `STARTED` - When you begin
2. `DECISION: {description}` - Each significant decision
3. `RATIONALE: {why}` - Why you made that decision
4. `FILE_CHANGED: {path}` - Each file modified
5. `APPROACH: {description}` - Your overall approach/ideology
6. `COMPLETED` - When finished

**Example:**
```
[14:30:01] WORKER-1: STARTED - Analyzing refactoring scope
[14:30:15] WORKER-1: DECISION: Extract auth logic into separate module
[14:30:15] WORKER-1: RATIONALE: Current auth is tightly coupled with routes, making testing difficult
[14:30:45] WORKER-1: APPROACH: Using repository pattern for data access, dependency injection for testability
[14:31:20] WORKER-1: FILE_CHANGED: src/auth/repository.ts - Created new auth repository
[14:35:00] WORKER-1: COMPLETED
```

## Instructions

1. Log STARTED
2. Analyze files and plan your approach
3. Log your APPROACH and key DECISIONS with RATIONALE
4. Make changes, logging each FILE_CHANGED
5. Log COMPLETED when done
6. **DO NOT commit or push** - Queen handles git

## Begin
Execute your refactoring task now.
```

**worker-2-task.md (Patterns/Frontend - Gemini):**
```markdown
# Worker 2 Task - Patterns & Modernization

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/worker-2.log

## CRITICAL: Read Worker-1's Log First

Before starting, understand what Worker-1 did:
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
```

Pay attention to:
- Their APPROACH and ideology
- Their DECISIONS and RATIONALE
- Files they changed (avoid conflicts, build on their work)

## Refactoring Target
{REFACTOR_TARGET}

## Your Specialty
Pattern application, modern syntax, creative restructuring, type improvements.

## Structured Logging Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/worker-2.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] WORKER-2: message'"
```

**Required log entries:** STARTED, DECISION, RATIONALE, FILE_CHANGED, APPROACH, COMPLETED

## Shell Command Rules (CRITICAL)

- **NEVER use chained commands** (`&&`, `||`, `;`)
- Run each shell command separately
- Example: Instead of `type file1 && type file2`, run `type file1` then `type file2` as separate commands
- This ensures YOLO mode works correctly for autonomous execution

## Instructions

1. Log STARTED
2. **Read Worker-1's log completely**
3. Build on their approach - don't contradict their decisions
4. Log your APPROACH and DECISIONS with RATIONALE
5. Make changes, logging each FILE_CHANGED
6. Log COMPLETED when done
7. **DO NOT commit or push** - Queen handles git

## Begin
Read Worker-1's log, then execute your task.
```

**worker-3-task.md (Coherence - Grok Code):**
```markdown
# Worker 3 Task - Backend/Frontend Coherence

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/worker-3.log

## CRITICAL: Read Previous Workers' Logs First

```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-2.log"
```

Understand:
- Worker-1's backend approach and decisions
- Worker-2's frontend/pattern approach
- Where they might not align

## Your Specialty
Ensure backend and frontend changes are coherent. Fix any misalignments.

## Structured Logging Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/worker-3.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] WORKER-3: message'"
```

**Required log entries:** STARTED, DECISION, RATIONALE, FILE_CHANGED, COHERENCE_FIX, COMPLETED

## Instructions

1. Log STARTED
2. **Read Worker-1 and Worker-2 logs completely**
3. Check for coherence issues (API contracts, data flows, type mismatches)
4. Log any COHERENCE_FIX entries with RATIONALE
5. Make fixes, logging each FILE_CHANGED
6. Log COMPLETED when done
7. **DO NOT commit or push** - Queen handles git

## Begin
Read previous logs, then verify coherence.
```

### Step 8: Write Reviewer Task Files

**reviewer-bigpickle-task.md:**
```markdown
# Reviewer Task - BigPickle (Deep Analysis)

## Session
- **Session ID**: {SESSION_ID}
- **Your Review File**: .hive/sessions/{SESSION_ID}/reviews/bigpickle.md

## Read All Worker Logs

```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-2.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-3.log"
```

## Your Focus
- Edge cases and error handling
- Security implications
- Performance concerns
- Architectural issues
- Breaking changes

## Review Output Format

Write findings to your review file:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/reviews/bigpickle.md' -Value 'finding'"
```

**Format each finding as:**
```
## FINDING: {title}
**Severity**: HIGH / MEDIUM / LOW
**File**: {path}
**Issue**: {description}
**Suggested Fix**: {how to fix}
```

## Instructions

1. Read all worker logs
2. Review changed files (use `git diff`)
3. Write findings to your review file
4. End with `COMPLETED`

## Begin
Execute your review now.
```

**reviewer-grok-task.md:**
```markdown
# Reviewer Task - Grok (Quick Observations)

## Session
- **Session ID**: {SESSION_ID}
- **Your Review File**: .hive/sessions/{SESSION_ID}/reviews/grok.md

## Read Worker Logs

```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-1.log" -Tail 30
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-2.log" -Tail 30
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-3.log" -Tail 30
```

## Your Focus
- Obvious bugs
- Quick wins
- Code style consistency
- Simple improvements

## Review Output Format

Write to your review file:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/reviews/grok.md' -Value 'finding'"
```

## Instructions

1. Read worker logs
2. Quick review of changes
3. Write observations
4. End with `COMPLETED`

## Begin
Execute your review now.
```

### Step 9: Write Resolver Task File

**resolver-task.md:**
```markdown
# Resolver Task - Address All Reviewer Findings

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/resolver.log

## CRITICAL: Read All Reviewer Findings

```powershell
Get-Content ".hive/sessions/{SESSION_ID}/reviews/bigpickle.md"
Get-Content ".hive/sessions/{SESSION_ID}/reviews/grok.md"
```

## Also Read Worker Logs for Context

```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-2.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-3.log"
```

## Your Task

Address EVERY finding from the reviewers:
- Fix HIGH severity issues
- Fix MEDIUM severity issues
- Consider LOW severity issues
- Document any findings you intentionally skip (with rationale)

## Structured Logging Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/resolver.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] RESOLVER: message'"
```

**Required log entries:**
- `STARTED`
- `ADDRESSING: {finding title}` - Each finding you address
- `FIXED: {description}` - How you fixed it
- `SKIPPED: {finding title} - RATIONALE: {why}` - If intentionally skipping
- `FILE_CHANGED: {path}`
- `COMPLETED`

## Instructions

1. Log STARTED
2. Read ALL reviewer findings
3. Address each finding, logging your work
4. Log COMPLETED when done
5. **DO NOT commit or push** - Queen handles git

## Begin
Read reviewer findings and resolve them.
```

### Step 10: Write Tester Task File

**tester-task.md:**
```markdown
# Tester Task - Run Tests and Fix Failures

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/tester.log

## Read Previous Logs for Context

```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/resolver.log"
Get-Content ".hive/sessions/{SESSION_ID}/reviews/bigpickle.md" -Tail 20
Get-Content ".hive/sessions/{SESSION_ID}/reviews/grok.md" -Tail 20
```

## Your Task

1. Run the test suite
2. Fix any failures
3. Run tests again until passing
4. Document any issues that couldn't be resolved

## Structured Logging Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/tester.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] TESTER: message'"
```

**Required log entries:**
- `STARTED`
- `TEST_RUN: {command}` - Test command executed
- `TEST_RESULT: PASS/FAIL - {summary}`
- `FIXING: {description}` - What you're fixing
- `FILE_CHANGED: {path}`
- `DIFFICULTY: {description}` - Issues that couldn't be fully resolved
- `COMPLETED`

## Instructions

1. Log STARTED
2. Run tests: `npm test` or appropriate command
3. If failures, fix them and log FIXING entries
4. Re-run tests until passing (or max 3 attempts)
5. Log any DIFFICULTY entries for unresolved issues
6. Log COMPLETED
7. **DO NOT commit or push** - Queen handles git

## Begin
Run tests and fix failures.
```

### Step 11: Write Queen Prompt

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen Agent - Hive Refactor Orchestrator

You are the **Queen** orchestrating a spawn-on-demand refactoring hive.

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/queen.log
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}
- **Refactor Branch**: refactor/{SESSION_ID}
- **Base Branch**: {BASE_BRANCH}

## Refactoring Target

{REFACTOR_TARGET}

## Workflow: Sequential Workers with Logging

**CRITICAL**: Workers run SEQUENTIALLY. Each reads the previous worker's log.

### Phase 1: Sequential Workers

**Step 1: Spawn Worker-1 (Cursor CLI - Opus 4.5 - Backend/Architecture)**

Write spawn .bat file:
```powershell
Set-Content -Path ".hive/sessions/{SESSION_ID}/spawn-worker1.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.hive/sessions/{SESSION_ID}/worker-1-task.md and execute.\\\"\", \"name\": \"worker-1\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

Execute:
```bash
.hive/sessions/{SESSION_ID}/spawn-worker1.bat
```

Wait for COMPLETED in worker-1.log:
```powershell
Select-String -Path ".hive/sessions/{SESSION_ID}/logs/worker-1.log" -Pattern "COMPLETED"
```

**Step 2: Spawn Worker-2 (Gemini - Patterns)**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "gemini -m gemini-3-pro-preview -y -i \"Read .hive/sessions/{SESSION_ID}/worker-2-task.md and execute.\"", "name": "worker-2"}'
```

Wait for COMPLETED in worker-2.log.

**Step 3: Spawn Worker-3 (Grok - Coherence)**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read .hive/sessions/{SESSION_ID}/worker-3-task.md and execute.\"", "name": "worker-3", "env": {"OPENCODE_YOLO": "true"}}'
```

Wait for COMPLETED in worker-3.log.

### Phase 2: Reviewers (Parallel)

**Spawn both reviewers simultaneously:**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read .hive/sessions/{SESSION_ID}/reviewer-bigpickle-task.md and execute.\"", "name": "reviewer-bigpickle", "env": {"OPENCODE_YOLO": "true"}}'

mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read .hive/sessions/{SESSION_ID}/reviewer-grok-task.md and execute.\"", "name": "reviewer-grok", "env": {"OPENCODE_YOLO": "true"}}'
```

Wait for COMPLETED in both review files.

### Phase 3: Resolver

**Spawn Resolver (Cursor CLI - Opus 4.5 - addresses all findings):**

Write spawn .bat file:
```powershell
Set-Content -Path ".hive/sessions/{SESSION_ID}/spawn-resolver.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.hive/sessions/{SESSION_ID}/resolver-task.md and execute.\\\"\", \"name\": \"resolver\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

Execute:
```bash
.hive/sessions/{SESSION_ID}/spawn-resolver.bat
```

Wait for COMPLETED in resolver.log.

### Phase 4: Tester

**Spawn Tester (Codex - runs tests, fixes failures):**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .hive/sessions/{SESSION_ID}/tester-task.md and execute.\"", "name": "tester"}'
```

Wait for COMPLETED in tester.log.

### Phase 5: Commit, Push & Create PR

**Collect difficulties from tester log:**
```powershell
Select-String -Path ".hive/sessions/{SESSION_ID}/logs/tester.log" -Pattern "DIFFICULTY"
```

**Commit and push:**
```bash
git add -A
git commit -m "refactor: {REFACTOR_TARGET}

{summary of changes}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

git push -u origin refactor/{SESSION_ID}
```

**Create PR with difficulties noted:**
```bash
gh pr create --base {BASE_BRANCH} --title "refactor: {REFACTOR_TARGET}" --body "$(cat <<'EOF'
## Summary
{summary}

## Workers
- Worker-1 (Opus): Backend/architecture changes
- Worker-2 (Gemini): Pattern/modernization
- Worker-3 (Grok): Coherence verification
- Resolver (Opus): Addressed reviewer findings
- Tester (Codex): Tests passing

## Difficulties Encountered
{difficulties from tester log, or "None"}

## Session
{SESSION_ID}

Generated by Hive multi-agent system
EOF
)"
```

## Log Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Message\""
```

## Error Handling

**If a worker seems stuck:**
1. Read their log for clues
2. Remove: `mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "remove-proc", "proc": "worker-name"}'`
3. Spawn replacement

**If Gemini fails with quota:**
1. Remove worker-2
2. Respawn with flash: `gemini -m gemini-3-flash-preview`

## Begin

Announce: "Queen initialized for refactoring {REFACTOR_TARGET}. Starting Phase 1: Sequential workers..."
```

### Step 12: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# Spawn-on-Demand Hive Refactor
# Session: {SESSION_ID}

server: 127.0.0.1:{MPROCS_PORT}

procs:
  queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      MPROCS_SERVER: "127.0.0.1:{MPROCS_PORT}"

  logs:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== HIVE REFACTOR LOGS ===' -ForegroundColor Cyan; Get-ChildItem .hive/sessions/{SESSION_ID}/logs -Filter *.log -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('--- ' + $_.Name + ' ---') -ForegroundColor Yellow; Get-Content $_.FullName -Tail 5 -ErrorAction SilentlyContinue }; Write-Host '--- REVIEWS ---' -ForegroundColor Magenta; Get-ChildItem .hive/sessions/{SESSION_ID}/reviews -Filter *.md -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_.Name; Get-Content $_.FullName -Tail 3 -ErrorAction SilentlyContinue }; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

### Step 13: Create Log Files

```bash
cd "{PROJECT_ROOT}"
type nul > ".hive/sessions/{SESSION_ID}/logs/queen.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/worker-2.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/worker-3.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/resolver.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/tester.log"
type nul > ".hive/sessions/{SESSION_ID}/reviews/bigpickle.md"
type nul > ".hive/sessions/{SESSION_ID}/reviews/grok.md"
```

### Step 14: Launch mprocs

```bash
powershell -Command "Start-Process powershell -WorkingDirectory '{PROJECT_ROOT_WINDOWS}' -ArgumentList '-NoExit', '-Command', 'mprocs --config .hive/mprocs.yaml'"
```

### Step 15: Output Status

```markdown
## Hive Refactor Launched!

**Session**: {SESSION_ID}
**Target**: {REFACTOR_TARGET}
**Branch**: refactor/{SESSION_ID}
**Files**: {TOTAL_FILES}

### Architecture: Spawn-on-Demand with Sequential Workers

```
Queen (Opus)
    │
    ├─► Worker-1 (Opus) ──► logs decisions + changes
    │       ↓ (sequential)
    ├─► Worker-2 (Gemini) ──► reads W1 logs, logs own
    │       ↓ (sequential)
    ├─► Worker-3 (Grok) ──► coherence check
    │       ↓
    ├─► Reviewers (BigPickle + Grok) ──► findings
    │       ↓
    ├─► Resolver (Opus) ──► addresses all findings
    │       ↓
    ├─► Tester (Codex) ──► tests + fixes
    │       ↓
    └─► Commit + PR + difficulty comments
```

### Key Features

- **Sequential execution**: Each worker reads previous logs
- **Structured logging**: Decisions, rationale, approach passed downstream
- **Review + Resolve**: Reviewers find issues, Resolver addresses them
- **Clean exit**: PR includes difficulties encountered

### Session Files

| File | Purpose |
|------|---------|
| `logs/queen.log` | Queen orchestration |
| `logs/worker-*.log` | Worker decisions and changes |
| `logs/resolver.log` | How findings were addressed |
| `logs/tester.log` | Test results and difficulties |
| `reviews/*.md` | Reviewer findings |

Watch the sequential refactoring unfold!
```

## Usage

```bash
/hive-refactor "src/legacy/"
/hive-refactor "src/api/*.ts"
/hive-refactor "the authentication module"
```
