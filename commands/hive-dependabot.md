---
description: B-Thread - Resolve ALL Dependabot PRs with spawn-on-demand workers, reviewers, resolver, and tester
argument-hint: "[repo-owner/repo-name]"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task, TodoWrite]
---

# Hive Dependabot - Spawn-on-Demand PR Resolution

Resolve all open Dependabot PRs with spawn-on-demand workers, reviewers, resolver, and tester.

## Thread Type: B-Thread (Big/Meta) + L-Thread (Long Duration)

- **Spawn-on-demand**: Only Queen starts, workers spawned as needed
- **One Codex per PR**: Each worker merges their PR, logs changes
- **Test conflicts**: Run build/tests after merges
- **Reviewers**: BigPickle + Grok review all changes
- **Resolver**: Address reviewer findings + any conflicts
- **Clean exit**: Merge to consolidated branch, close all PRs

## Arguments

- `[repo-owner/repo-name]`: Optional. Defaults to current repo.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  MAIN CLAUDE (runs /hive-dependabot)                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 1. Fetch all open Dependabot PRs                               │  │
│  │ 2. Write task files for each PR                                │  │
│  │ 3. Write queen-prompt.md                                       │  │
│  │ 4. Launch mprocs (Queen only)                                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    QUEEN (Opus 4.5) - Orchestrator                  │
│                                                                     │
│   Phase 1: Spawn Codex Workers (1 per PR, sequential)               │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                        │
│   │ Codex-1 │ → │ Codex-2 │ → │ Codex-N │                          │
│   │  PR #X  │    │  PR #Y  │    │  PR #Z  │                        │
│   └─────────┘    └─────────┘    └─────────┘                        │
│                                                                     │
│   Phase 2: Test for Conflicts                                       │
│   ┌─────────────────────────────────┐                              │
│   │ Run build + tests               │                              │
│   └─────────────────────────────────┘                              │
│                                                                     │
│   Phase 3: Reviewers (parallel)                                     │
│   ┌─────────────┐    ┌─────────────┐                               │
│   │ BigPickle   │    │    Grok     │                               │
│   │ Deep Review │    │ Quick Review│                               │
│   └─────────────┘    └─────────────┘                               │
│                                                                     │
│   Phase 4: Resolver                                                 │
│   ┌─────────────────────────────────┐                              │
│   │ Resolver (Opus 4.5)             │                              │
│   │ Fix conflicts + reviewer issues │                              │
│   └─────────────────────────────────┘                              │
│                                                                     │
│   Phase 5: Tester                                                   │
│   ┌─────────────────────────────────┐                              │
│   │ Tester (Codex GPT-5.2)          │                              │
│   │ Run tests, fix failures         │                              │
│   └─────────────────────────────────┘                              │
│                                                                     │
│   Phase 6: Merge + Close all PRs                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Workflow

### Step 1: Check Prerequisites

```bash
mprocs --version
```

If mprocs not installed, tell user to install it and STOP.

### Step 2: Fetch All Dependabot PRs

```bash
# If no repo argument, get current repo
gh repo view --json nameWithOwner --jq '.nameWithOwner'

# Fetch all open Dependabot PRs
gh pr list --repo {REPO} --author "app/dependabot" --json number,title,headRefName,url --state open
```

Parse results into:
```
DEPENDABOT_PRS = [
  { number: 188, title: "...", branch: "dependabot/...", url: "..." },
  ...
]
PR_COUNT = length of array
```

**If PR_COUNT is 0**: Output "No open Dependabot PRs found." and STOP.

### Step 3: Generate Session Variables

```bash
TIMESTAMP=$(powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'")
PROJECT_ROOT_WINDOWS=$(powershell -NoProfile -Command "(Get-Location).Path")
MPROCS_PORT=$((4000 + ${TIMESTAMP: -4}))
SESSION_ID="${TIMESTAMP}-hive-dependabot"
BASE_BRANCH=$(git branch --show-current)
CONSOLIDATED_BRANCH="dependabot/hive-${SESSION_ID}"
```

**CRITICAL - Path Format for mprocs.yaml:**
- mprocs on Windows REQUIRES Windows-style paths with escaped backslashes
- Format in YAML: `"D:\\Code Projects\\MyProject"` (double backslashes)
- NEVER use Git Bash paths like `/d/Code Projects/...`

### Step 4: Create Session Directory

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
mkdir -p ".hive/sessions/{SESSION_ID}/reviews"
mkdir -p ".hive/sessions/{SESSION_ID}/logs"
```

### Step 5: Create Consolidated Branch

```bash
git checkout -b {CONSOLIDATED_BRANCH}
```

### Step 6: Create tasks.json

Write to `.hive/sessions/{SESSION_ID}/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "B-Thread (Hive Dependabot)",
  "repo": "{REPO}",
  "consolidated_branch": "{CONSOLIDATED_BRANCH}",
  "base_branch": "{BASE_BRANCH}",
  "pr_count": {PR_COUNT},
  "prs": [
    {
      "number": 188,
      "title": "...",
      "branch": "dependabot/...",
      "worker": "codex-1",
      "status": "pending"
    }
  ],
  "workflow": "spawn-on-demand-sequential",
  "phases": {
    "workers": ["codex-1", "codex-2", ...],
    "reviewers": ["reviewer-bigpickle", "reviewer-grok"],
    "resolver": "resolver",
    "tester": "tester"
  }
}
```

### Step 7: Write Worker Task Files

**For each Dependabot PR, create a task file.**

**codex-{N}-task.md:**
```markdown
# Codex Worker {N} - PR #{PR_NUMBER} Resolution

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/codex-{N}.log

## Your Assignment

**PR**: #{PR_NUMBER}
**Title**: {PR_TITLE}
**Branch**: {PR_BRANCH}

## Task

Merge this Dependabot PR branch into the consolidated branch.

## Structured Logging Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/codex-{N}.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] CODEX-{N}: message'"
```

**Required log entries:**
- `STARTED`
- `MERGING: {branch}`
- `MERGE_RESULT: SUCCESS/CONFLICT - {details}`
- `PACKAGE_CHANGE: {package} {old_version} → {new_version}`
- `COMPLETED`

## Instructions

1. Log STARTED
2. Fetch and merge the PR branch:
   ```bash
   git fetch origin {PR_BRANCH}
   git merge origin/{PR_BRANCH} --no-edit
   ```
3. Log MERGE_RESULT
4. Log any PACKAGE_CHANGE entries
5. If merge conflict, log details and attempt to resolve
6. Log COMPLETED
7. **DO NOT commit or push** - Queen handles git

## Begin
Execute your merge task now.
```

### Step 8: Write Reviewer Task Files

**reviewer-bigpickle-task.md:**
```markdown
# Reviewer Task - BigPickle (Deep Analysis)

## Session
- **Session ID**: {SESSION_ID}
- **Your Review File**: .hive/sessions/{SESSION_ID}/reviews/bigpickle.md

## Context

{PR_COUNT} Dependabot PRs have been merged. Review all changes for:
- Breaking changes in dependencies
- Security concerns
- Compatibility issues between packages
- Configuration changes needed

## Read All Worker Logs

```powershell
Get-ChildItem ".hive/sessions/{SESSION_ID}/logs/codex-*.log" | ForEach-Object { Write-Host "=== $($_.Name) ==="; Get-Content $_ }
```

## Review Output Format

Write findings to your review file:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/reviews/bigpickle.md' -Value 'finding'"
```

**Format each finding as:**
```
## FINDING: {title}
**Severity**: HIGH / MEDIUM / LOW
**Package**: {package name}
**Issue**: {description}
**Suggested Fix**: {how to fix}
```

## Instructions

1. Read all codex worker logs
2. Review package.json / requirements.txt changes
3. Check for breaking changes in changelogs
4. Write findings to your review file
5. End with `COMPLETED`

## Begin
Execute your review now.
```

**reviewer-grok-task.md:**
```markdown
# Reviewer Task - Grok (Quick Observations)

## Session
- **Session ID**: {SESSION_ID}
- **Your Review File**: .hive/sessions/{SESSION_ID}/reviews/grok.md

## Context

{PR_COUNT} Dependabot PRs merged. Quick review for obvious issues.

## Read Worker Logs

```powershell
Get-ChildItem ".hive/sessions/{SESSION_ID}/logs/codex-*.log" | ForEach-Object { Get-Content $_ -Tail 10 }
```

## Your Focus
- Obvious conflicts
- Version mismatches
- Quick wins

## Instructions

1. Read worker logs
2. Quick review of dependency changes
3. Write observations
4. End with `COMPLETED`

## Begin
Execute your review now.
```

### Step 9: Write Resolver Task File

**resolver-task.md:**
```markdown
# Resolver Task - Fix Conflicts + Reviewer Issues

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/resolver.log

## CRITICAL: Read All Reviewer Findings

```powershell
Get-Content ".hive/sessions/{SESSION_ID}/reviews/bigpickle.md"
Get-Content ".hive/sessions/{SESSION_ID}/reviews/grok.md"
```

## Also Check Worker Logs for Conflicts

```powershell
Get-ChildItem ".hive/sessions/{SESSION_ID}/logs/codex-*.log" | ForEach-Object { Select-String -Path $_ -Pattern "CONFLICT" }
```

## Your Task

1. Address ALL reviewer findings
2. Fix any merge conflicts logged by workers
3. Ensure package.json/lock files are consistent
4. Run `npm install` or equivalent to update lock file

## Structured Logging Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/resolver.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] RESOLVER: message'"
```

**Required log entries:**
- `STARTED`
- `ADDRESSING: {finding or conflict}`
- `FIXED: {description}`
- `SKIPPED: {item} - RATIONALE: {why}`
- `FILE_CHANGED: {path}`
- `COMPLETED`

## Instructions

1. Log STARTED
2. Read ALL reviewer findings
3. Check for any CONFLICT entries in worker logs
4. Fix each issue, logging your work
5. Run `npm install` to regenerate lock file
6. Log COMPLETED
7. **DO NOT commit or push** - Queen handles git

## Begin
Read findings and resolve issues.
```

### Step 10: Write Tester Task File

**tester-task.md:**
```markdown
# Tester Task - Verify All Dependencies Work

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/tester.log

## Your Task

1. Run the full test suite
2. Fix any failures caused by dependency updates
3. Verify build succeeds
4. Document any issues that couldn't be resolved

## Structured Logging Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/tester.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] TESTER: message'"
```

**Required log entries:**
- `STARTED`
- `TEST_RUN: {command}`
- `TEST_RESULT: PASS/FAIL - {summary}`
- `BUILD_RUN: {command}`
- `BUILD_RESULT: PASS/FAIL`
- `FIXING: {description}`
- `FILE_CHANGED: {path}`
- `DIFFICULTY: {description}` - Issues that couldn't be resolved
- `COMPLETED`

## Instructions

1. Log STARTED
2. Run `npm install` (or pip install, etc.)
3. Run lint: `npm run lint`
4. Run typecheck: `npm run typecheck` (if applicable)
5. Run tests: `npm test`
6. Run build: `npm run build`
7. Fix any failures, log FIXING entries
8. Re-run until passing (max 3 attempts)
9. Log any DIFFICULTY entries
10. Log COMPLETED
11. **DO NOT commit or push** - Queen handles git

## Begin
Run tests and fix failures.
```

### Step 11: Write Queen Prompt

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen Agent - Hive Dependabot Orchestrator

You are the **Queen** orchestrating a spawn-on-demand hive to resolve {PR_COUNT} Dependabot PRs.

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/queen.log
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}
- **Repository**: {REPO}
- **Consolidated Branch**: {CONSOLIDATED_BRANCH}
- **Base Branch**: {BASE_BRANCH}

## Dependabot PRs to Resolve

| # | PR | Title | Worker |
|---|-----|-------|--------|
{PR_TABLE}

## Workflow: Spawn-on-Demand Sequential

### Phase 1: Spawn Codex Workers (Sequential)

**IMPORTANT**: Spawn workers ONE AT A TIME to avoid merge conflicts.

**For each PR, spawn a Codex worker:**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .hive/sessions/{SESSION_ID}/codex-{N}-task.md and execute.\"", "name": "codex-{N}"}'
```

Wait for COMPLETED in codex-{N}.log before spawning next worker:
```powershell
Select-String -Path ".hive/sessions/{SESSION_ID}/logs/codex-{N}.log" -Pattern "COMPLETED"
```

### Phase 2: Test for Conflicts

After all workers complete, run initial test:
```bash
npm install
npm run build
```

Log any failures for the Resolver.

### Phase 3: Reviewers (Parallel)

**Spawn both reviewers:**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read .hive/sessions/{SESSION_ID}/reviewer-bigpickle-task.md and execute.\"", "name": "reviewer-bigpickle", "env": {"OPENCODE_YOLO": "true"}}'

mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read .hive/sessions/{SESSION_ID}/reviewer-grok-task.md and execute.\"", "name": "reviewer-grok", "env": {"OPENCODE_YOLO": "true"}}'
```

Wait for COMPLETED in both review files.

### Phase 4: Resolver

**Spawn Resolver (Cursor CLI - Opus 4.5 - fixes conflicts + findings):**

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

### Phase 5: Tester

**Spawn Tester (Codex - runs tests, fixes failures):**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .hive/sessions/{SESSION_ID}/tester-task.md and execute.\"", "name": "tester"}'
```

Wait for COMPLETED in tester.log.

### Phase 6: Commit, Push & Close PRs

**Collect difficulties:**
```powershell
Select-String -Path ".hive/sessions/{SESSION_ID}/logs/tester.log" -Pattern "DIFFICULTY"
```

**Commit and push:**
```bash
git add -A
git commit -m "deps: resolve {PR_COUNT} Dependabot PRs

PRs resolved:
{list of PR numbers and titles}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

git push -u origin {CONSOLIDATED_BRANCH}
```

**Create PR:**
```bash
gh pr create --base {BASE_BRANCH} --title "deps: Resolve {PR_COUNT} Dependabot PRs via Hive" --body "$(cat <<'EOF'
## Summary
Resolved {PR_COUNT} Dependabot dependency updates.

## PRs Resolved
{list with links}

## Difficulties Encountered
{from tester log, or "None"}

## Session
{SESSION_ID}

Generated by Hive multi-agent system
EOF
)"
```

**Close all Dependabot PRs:**
```bash
# For each PR
gh pr close {PR_NUMBER} --repo {REPO} --comment "Resolved via hive-dependabot session {SESSION_ID}. Changes merged to {CONSOLIDATED_BRANCH}."
```

## Log Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Message\""
```

## Error Handling

**If a worker reports CONFLICT:**
1. Log it for the Resolver phase
2. Continue with next worker

**If build fails after merges:**
1. Log failures for Resolver
2. Resolver will attempt to fix

## Begin

Announce: "Queen initialized for {PR_COUNT} Dependabot PRs. Starting Phase 1: Sequential Codex workers..."
```

### Step 12: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# Spawn-on-Demand Hive Dependabot
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
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== HIVE DEPENDABOT LOGS ===' -ForegroundColor Cyan; Write-Host \"PRs: {PR_COUNT}\" -ForegroundColor Yellow; Get-ChildItem .hive/sessions/{SESSION_ID}/logs -Filter *.log -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('--- ' + $_.Name + ' ---') -ForegroundColor Yellow; Get-Content $_.FullName -Tail 3 -ErrorAction SilentlyContinue }; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

### Step 13: Create Log Files

```bash
cd "{PROJECT_ROOT}"
type nul > ".hive/sessions/{SESSION_ID}/logs/queen.log"
# For each PR:
type nul > ".hive/sessions/{SESSION_ID}/logs/codex-1.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/codex-2.log"
# ... continue for all PRs
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
## Hive Dependabot Launched!

**Session**: {SESSION_ID}
**Repository**: {REPO}
**PRs to Resolve**: {PR_COUNT}
**Consolidated Branch**: {CONSOLIDATED_BRANCH}

### Architecture: Spawn-on-Demand Sequential

```
Queen (Opus)
    │
    ├─► Codex-1 (PR #X) ──► merge + log
    │       ↓ (sequential)
    ├─► Codex-2 (PR #Y) ──► merge + log
    │       ↓ (sequential)
    ├─► Codex-N (PR #Z) ──► merge + log
    │       ↓
    ├─► Test for conflicts (build)
    │       ↓
    ├─► Reviewers (BigPickle + Grok) ──► findings
    │       ↓
    ├─► Resolver (Opus) ──► fix conflicts + findings
    │       ↓
    ├─► Tester (Codex) ──► tests + fixes
    │       ↓
    ├─► Commit + PR
    │       ↓
    └─► Close all Dependabot PRs
```

### Dependabot PRs

| # | PR | Title | Worker |
|---|-----|-------|--------|
{PR_TABLE}

### Key Features

- **Sequential merges**: One PR at a time to avoid conflicts
- **Review phase**: BigPickle + Grok review all changes
- **Resolver fixes**: Conflicts + reviewer findings addressed
- **Clean exit**: All PRs closed after successful merge

### Session Files

| File | Purpose |
|------|---------|
| `logs/queen.log` | Queen orchestration |
| `logs/codex-*.log` | Worker merge logs |
| `logs/resolver.log` | How issues were fixed |
| `logs/tester.log` | Test results |
| `reviews/*.md` | Reviewer findings |

Watch {PR_COUNT} Dependabot PRs get resolved!
```

## Usage

```bash
# Current repo
/hive-dependabot

# Specific repo
/hive-dependabot "owner/repo-name"
```
