---
description: Resolve PR comments using multi-agent Hive coordination (lightweight)
argument-hint: "<pr-number>" [--quality-only]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task, TodoWrite]
---

# Resolve Hive Comments - Lightweight PR Comment Resolution

Resolve PR comments with 6-agent validation and dynamic Grok workers (one per validated comment).

Supports two modes:
- **Full mode** (default): Validate comments → Resolve with workers → Code Quality Loop
- **Quality-only mode** (`--quality-only`): Skip straight to Code Quality Loop (for PRs with existing reviewer comments)

## Architecture

```
PHASE 1: VALIDATION (Task agents - 6 per comment) [skipped with --quality-only]
┌─────────────────────────────────────────────────────────────┐
│  Comment 1    Comment 2    Comment 3    ...                 │
│  ┌───────┐    ┌───────┐    ┌───────┐                       │
│  │6 agents│   │6 agents│   │6 agents│                       │
│  └───┬───┘    └───┬───┘    └───┬───┘                       │
│      ↓            ↓            ↓                            │
│  VALID/MISTAKEN   ...         ...                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
PHASE 2: RESOLUTION (mprocs - dynamic Grok workers)
┌─────────────────────────────────────────────────────────────┐
│                        QUEEN                                │
│                    (Opus 4.5)                               │
│                         │                                   │
│    ┌────────────────────┼────────────────────┐             │
│    ↓                    ↓                    ↓             │
│  grok-1              grok-2              grok-N            │
│ (comment 1)         (comment 2)         (comment N)        │
│                         │                                   │
│                    WORKER-4                                 │
│                  (Codex GPT-5.2)                            │
│                 Code Simplification                         │
│                         │                                   │
│                    TESTER-1                                 │
│                  (Codex GPT-5.2)                            │
│                         │                                   │
│              /curate-learnings                              │
│                         │                                   │
│                git commit/push                              │
└─────────────────────────────────────────────────────────────┘
```

## Arguments

- `<pr-number>`: Pull request number (e.g., `123`)
- `[--quality-only]`: Skip validation and worker phases, jump straight to Code Quality Loop
  - Use when PR already has reviewer comments you want to automate resolving
  - Example: `/resolve-hive-comments 123 --quality-only`

## Workflow

### Mode Detection

**If `--quality-only` is present:**
- Skip to [QUALITY-ONLY MODE](#quality-only-mode) section below
- Goes directly to Code Quality Loop (Phase 6)

**Otherwise:**
- Execute full workflow (Phases 1-6)

### Step 1: Check Prerequisites

```bash
mprocs --version
```

If mprocs not installed, tell user to install it and STOP.

### Step 2: Fetch PR Comments

```bash
gh pr view {PR_NUMBER} --json title,body,comments,reviewDecision,reviews
```

Extract:
- `PR_TITLE`
- `PR_BODY`
- `PR_COMMENTS` - Array of review comments to validate
- `PR_BRANCH` - The branch to push to

Also get the current branch:
```bash
gh pr view {PR_NUMBER} --json headRefName -q '.headRefName'
```

### Step 3: Generate Session Variables

**Run as a single block:**
```bash
TIMESTAMP=$(powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'")
PROJECT_ROOT_WINDOWS=$(powershell -NoProfile -Command "(Get-Location).Path")
MPROCS_PORT=$((4000 + ${TIMESTAMP: -4}))
SESSION_ID="${TIMESTAMP}-resolve-pr-${PR_NUMBER}"
```

**Variables:**
```
TIMESTAMP = e.g., 20260120-143052
SESSION_ID = {TIMESTAMP}-resolve-pr-{PR_NUMBER}
PROJECT_ROOT_WINDOWS = Windows-style path from PowerShell (e.g., D:\Code Projects\MyProject)
MPROCS_PORT = 4000 + last 4 digits (e.g., 143052 → 3052 → port 7052)
```

**Port range:** 4000-9959 (unique per session, no conflicts)

**CRITICAL - Path Format for mprocs.yaml:**
- mprocs on Windows REQUIRES Windows-style paths with escaped backslashes
- Use `PROJECT_ROOT_WINDOWS` (from PowerShell) for the `cwd` field
- Format in YAML: `"D:\\Code Projects\\MyProject"` (double backslashes)
- NEVER use Git Bash paths like `/d/Code Projects/...` - mprocs will fail!

### Step 4: Create Session Directory

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
```

---

## PHASE 1: Multi-Agent Validation (4 OpenCode agents per comment)

### Step 5: Spawn Validation Agents in Parallel

**For EVERY review comment, spawn exactly 4 OpenCode agents.**

Launch ALL agents in PARALLEL using a SINGLE message with multiple Task tool calls.

**Agent 1 - OpenCode BigPickle (Deep Analysis):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase verification scout using OpenCode BigPickle.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle \"Search codebase for evidence related to this PR comment: {COMMENT_TEXT}. Find files that address this concern, existing implementations, and evidence for whether the requested change is needed.\"

Report back:
- Files found that address this concern
- Existing implementations that contradict or support the comment
- Evidence for whether the change is needed

Verdict: VALID (needs work) or MISTAKEN (already addressed)"
)
```

**Agent 2 - OpenCode GLM 4.7 (Pattern Recognition):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase verification scout using OpenCode GLM 4.7.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free \"Search codebase for evidence related to this PR comment: {COMMENT_TEXT}. Find existing implementations and patterns that address this concern.\"

Report back:
- Files found that address this concern
- Existing implementations that contradict or support the comment
- Evidence for whether the change is needed

Verdict: VALID (needs work) or MISTAKEN (already addressed)"
)
```

**Agent 3 - OpenCode Grok Code (Quick Search):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase verification scout using OpenCode Grok Code.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code \"Search codebase for evidence related to this PR comment: {COMMENT_TEXT}. Identify existing implementations, test coverage, and code patterns that address this concern.\"

Report back:
- Files found that address this concern
- Existing implementations that contradict or support the comment
- Evidence for whether the change is needed

Verdict: VALID (needs work) or MISTAKEN (already addressed)"
)
```

### Step 6: Categorize Comments Using Agent Results

**Consensus logic:**
- 3/3 agents agree "needs work" → VALID (high confidence)
- 2/3 agents agree "needs work" → VALID (medium confidence)
- 3/3 agents found already addressed → MISTAKEN (high confidence)
- 2/3 agents found already addressed → MISTAKEN (medium confidence)
- **Tie** → Claude (orchestrator) reviews all evidence and makes final call

Store list of **VALID comments** - these will each get a Grok worker.

```
VALID_COUNT = number of VALID comments
```

If VALID_COUNT = 0, report that all comments were already addressed and STOP.

### Step 6b: Learning Scout Agent (GLM 4.7) - BEFORE WORKERS

**Purpose**: Extract relevant learnings from past sessions and project DNA to guide this session's workers.

**Spawn Learning Scout (Task agent):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a Learning Scout using OpenCode GLM 4.7.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free \"You are a Learning Scout. Extract relevant learnings for resolving PR #{PR_NUMBER} comments.

VALIDATED COMMENTS: {LIST_OF_VALIDATED_COMMENTS}

1. Read .ai-docs/learnings.jsonl (if exists) - extract entries with keywords matching these PR comments
2. Read .ai-docs/project-dna.md (if exists) - extract relevant principles and patterns
3. Read .ai-docs/bug-patterns.md (if exists) - extract bug fix patterns that might apply
4. Read CLAUDE.md (if exists) - extract coding standards and project instructions

OUTPUT FORMAT (write to stdout):
---SESSION-GUIDELINES-START---
## Relevant Past Learnings
- [learning 1 from similar past tasks]
- [learning 2]

## Project DNA Principles
- [principle 1 relevant to these comments]
- [principle 2]

## Coding Standards
- [standard 1]
- [standard 2]

## Suggested Guidelines for This Session
1. [guideline based on learnings]
2. [guideline based on project DNA]
3. [guideline based on standards]
---SESSION-GUIDELINES-END---
\"

Capture the output between the markers and report it back."
)
```

**Timeout**: 3 minutes (180000ms)

### Step 6c: Codify Session Guidelines

After Learning Scout completes:
1. Extract the output between `---SESSION-GUIDELINES-START---` and `---SESSION-GUIDELINES-END---`
2. Write to `.hive/sessions/{SESSION_ID}/session-guidelines.md`:

```markdown
# Session Guidelines for PR #{PR_NUMBER} Comments

## PR
{PR_TITLE}

## Validated Comments
{LIST_OF_VALIDATED_COMMENTS}

{LEARNING_SCOUT_OUTPUT}

## Codified Guidelines (Main Claude's Directives)

Based on the above learnings and project DNA, ALL workers in this session MUST:

1. {GUIDELINE_1}
2. {GUIDELINE_2}
3. {GUIDELINE_3}

---
Generated by: Learning Scout (GLM 4.7) + Main Claude
```

**IMPORTANT**: Main Claude reviews the Learning Scout output and adds/refines guidelines.

---

## PHASE 2: Resolution Hive (mprocs)

### Step 7: Create tasks.json

Write to `.hive/sessions/{SESSION_ID}/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "session_status": "active",
  "queen_status": "initializing",
  "task_type": "resolve-pr-comments",
  "pull_request": {
    "number": "{PR_NUMBER}",
    "title": "{PR_TITLE}",
    "branch": "{PR_BRANCH}"
  },
  "validated_comments": [
    {
      "id": "comment-1",
      "text": "{COMMENT_TEXT}",
      "assigned_worker": "grok-1",
      "status": "pending"
    }
  ],
  "workers": {
    "grok-1": {
      "provider": "opencode/grok-code",
      "assigned_comment": "comment-1",
      "status": "active",
      "can_commit": false
    }
  },
  "testers": {
    "tester-1": {
      "provider": "codex-gpt-5.2",
      "status": "active",
      "initial_delay": 600,
      "can_commit": false
    }
  },
  "tasks": [],
  "synthesis": {
    "status": "pending",
    "result_file": "results.md"
  }
}
```

### Step 8: Create Queen Prompt (Spawn-on-Demand)

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen Agent - Resolve PR #{PR_NUMBER} Comments

You are the **Queen** orchestrating a spawn-on-demand hive to resolve validated PR comments.

**Task files have already been written by Main Claude.** Your job is to spawn workers at the right time and monitor their progress.

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/queen.log
- **PR Branch**: {PR_BRANCH}
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}

## Validated Comments (from Phase 1)

These comments were verified by 6 agents each and confirmed as VALID:

{LIST_OF_VALIDATED_COMMENTS}

## Session Guidelines (CRITICAL - READ FIRST!)

A Learning Scout has extracted relevant learnings and project DNA for this PR:
`.hive/sessions/{SESSION_ID}/session-guidelines.md`

**BEFORE spawning ANY workers, you MUST:**
1. Read the session-guidelines.md file completely
2. Internalize the guidelines - they apply to ALL workers
3. These guidelines are already embedded in each worker's task file

## Your Team

| Worker | Provider | Assigned Comment |
|--------|----------|------------------|
{DYNAMIC_WORKER_TABLE}

| Simplifier | Provider | Role |
|------------|----------|------|
| worker-4 | Codex GPT-5.2 | Code simplification |

| Tester | Provider | Role |
|--------|----------|------|
| tester-1 | Codex GPT-5.2 | Final testing |

| Code Quality | Provider | Role |
|--------------|----------|------|
| code-quality-{N} | **Cursor CLI** (Opus 4.5) | PR comment resolution (up to 5 cycles) |

## Spawn Commands

**IMPORTANT**: Use forward slashes in paths. Escape inner quotes with backslash.

### Grok Worker (one per validated comment)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read .hive/sessions/{SESSION_ID}/grok-{N}-task.md and execute.\"", "name": "grok-{N}", "env": {"OPENCODE_YOLO": "true"}}'
```

### Worker-4 (Codex GPT-5.2 - Code Simplification)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .hive/sessions/{SESSION_ID}/worker-4-task.md and execute.\"", "name": "worker-4"}'
```

### Tester (Codex GPT-5.2)
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .hive/sessions/{SESSION_ID}/tester-task.md and execute.\"", "name": "tester-1"}'
```

### Code Quality Agent (Cursor CLI - Opus 4.5)

**Use .bat files for Cursor CLI spawns:**

Write to `.hive/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat`:
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.hive/sessions/{SESSION_ID}/code-quality-{N}-task.md and execute.\\\"\", \"name\": \"code-quality-{N}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

Execute:
```bash
.hive/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat
```

## CLI-Specific Formats

| CLI | Format |
|-----|--------|
| OpenCode | `-m MODEL --prompt "PROMPT"` + `OPENCODE_YOLO=true` |
| Codex | `--dangerously-bypass-approvals-and-sandbox -m gpt-5.2 "PROMPT"` |
| Cursor CLI | `cmd /c wsl -d Ubuntu /root/.local/bin/agent --force "PROMPT"` via .bat file |

## Log Protocol

**APPEND-ONLY**: Use PowerShell explicitly.

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Message\""
```

## Git Workflow (QUEEN ONLY)

**YOU are the ONLY agent who commits and pushes.**

## Resolution Process

### Phase 0: Setup (DO THIS FIRST!)

**Step 0a: Checkout PR Branch**
```bash
git checkout {PR_BRANCH}
git pull origin {PR_BRANCH}
```

**Step 0b: Verify Session Guidelines**
Read and log that you've reviewed the session guidelines:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Reviewed session-guidelines.md - {number} guidelines codified\""
```

### Phase 1: Spawn Grok Workers (Parallel)

Spawn all grok workers in parallel - each has one comment to resolve:
1. Spawn grok-1, grok-2, ... grok-N simultaneously
2. Monitor logs for COMPLETED

### Phase 2: Spawn Worker-4 (Code Simplification)

When all grok workers show COMPLETED:
1. Spawn worker-4 (Codex GPT-5.2 - code simplifier)
2. Monitor worker-4.log for COMPLETED

### Phase 3: Spawn Tester

When worker-4 shows COMPLETED:
1. Spawn tester-1
2. Monitor tester-1.log for COMPLETED

### Phase 4: Curate Learnings (QUEEN REVIEWS LOGS FIRST!)

**BEFORE running curate-learnings, YOU (Queen) must:**

1. **Read ALL grok worker logs:**
```powershell
Get-ChildItem ".hive/sessions/{SESSION_ID}/grok-*.log" | ForEach-Object { Write-Host "=== $($_.Name) ==="; Get-Content $_ }
```

2. **Read worker-4 and tester logs:**
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/worker-4.log"
Get-Content ".hive/sessions/{SESSION_ID}/tester-1.log"
```

3. **Synthesize key insights** - What worked? What didn't? What patterns emerged?

4. **Log your synthesis:**
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: SESSION SYNTHESIS - {key insights}\""
```

5. **Curate learnings yourself** - Append to `.ai-docs/learnings.jsonl`:
```powershell
$learning = @{
    date = (Get-Date -Format "yyyy-MM-dd")
    session = "{SESSION_ID}"
    task = "Resolve PR #{PR_NUMBER} comments"
    outcome = "success"
    keywords = @("{keyword1}", "{keyword2}")
    insight = "{YOUR_SYNTHESIS}"
    files_touched = @("{file1}", "{file2}")
} | ConvertTo-Json -Compress
Add-Content -Path ".ai-docs/learnings.jsonl" -Value $learning
```

If `.ai-docs/` doesn't exist, note that user should run `/init-project-dna`.

### Phase 5: Commit, Push (QUEEN ONLY)

```bash
git add .
git commit -m "fix: address PR review comments

Changes:
- {change 1}
- {change 2}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
Co-Authored-By: Grok Code <noreply@xai.com>
Co-Authored-By: Codex GPT-5.2 <noreply@openai.com>"

git push origin {PR_BRANCH}
```

### Phase 6: Code Quality Loop (Automated PR Comment Resolution)

**⚠️ MANDATORY - DO NOT SKIP THIS PHASE ⚠️**

After commit/push, external reviewers (Gemini, Codex, Code Rabbit) will comment on the PR.
This phase automates resolving those comments iteratively using **Cursor CLI** (Opus 4.5).

**Loop parameters:**
- **Wait time per cycle**: 10 minutes
- **Maximum cycles**: 5
- **Total max wait**: 50 minutes

#### Phase 6.1: Wait for External Reviews (10 minutes)

**⚠️ YOU MUST ACTUALLY WAIT - DO NOT SKIP ⚠️**

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Code Quality Loop - Cycle 1. Waiting 10 minutes for external reviewers...\"; Start-Sleep -Seconds 600; Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Wait complete. Checking for comments...\""
```

**DO NOT proceed until this command completes (10 minutes).**

#### Phase 6.2: Check for New Comments

```bash
# Check for new comments on the PR
NEW_COMMENTS=$(gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --jq 'length')
```

**If NEW_COMMENTS = 0**: Log "No new comments. PR is ready for review." and END loop.

#### Phase 6.3: Write and Spawn Code Quality Agent (Cursor CLI - Opus 4.5)

**Phase 6.3a: Write iteration-specific task file**

Copy the template and fill in iteration details:
```powershell
$template = Get-Content ".hive/sessions/{SESSION_ID}/code-quality-task-template.md" -Raw
$taskContent = $template -replace '\{N\}', '{N}' -replace '\{PR_NUMBER\}', '{PR_NUMBER}'
Set-Content -Path ".hive/sessions/{SESSION_ID}/code-quality-{N}-task.md" -Value $taskContent
```

**Phase 6.3b: Create empty log file**
```powershell
New-Item -Path ".hive/sessions/{SESSION_ID}/code-quality-{N}.log" -ItemType File -Force
```

**Phase 6.3c: Spawn code-quality-{N} agent via MPROCS (Cursor CLI)**

**⚠️ YOU MUST USE MPROCS - NOT TASK TOOL ⚠️**

Do NOT use the Task tool. You MUST spawn a visible mprocs agent:

**Step 1: Write spawn .bat file**
```powershell
Set-Content -Path ".hive/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.hive/sessions/{SESSION_ID}/code-quality-{N}-task.md and execute.\\\"\", \"name\": \"code-quality-{N}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

**Step 2: Execute**
```bash
.hive/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat
```

The code-quality agent will handle the PR comments. Your job is to SPAWN and MONITOR, not to do the work yourself.

#### Phase 6.4: Monitor and Loop (Up to 3 Cycles)

1. Wait for `COMPLETED` in code-quality-{N}.log
2. Commit and push the code-quality agent's changes
3. Wait another 10 minutes for new reviews
4. Check for new comments
5. If new comments exist AND N < 5, spawn code-quality-{N+1}
6. Repeat until no new comments OR max 5 cycles

**Loop termination conditions:**
- No new comments after 10-minute wait → SUCCESS
- Maximum 5 iterations reached → END (alert user if still comments)

#### Phase 6.5: Log Completion

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Code Quality Loop complete. {N} iterations. PR is ready for human review.\""
```

## Error Handling

**If a worker seems stuck:**
1. Read their full log for clues
2. Remove the stuck worker: `remove-proc`
3. Spawn a replacement with clearer instructions

## Begin

Announce: "Queen initialized for PR #{PR_NUMBER}. Checking out branch and spawning {WORKER_COUNT} Grok workers..."
```

### Step 9: Create Worker Task Files (Dynamic)

**Main Claude writes task files BEFORE launching mprocs.** Workers read their task file when spawned.

For each validated comment, create `.hive/sessions/{SESSION_ID}/grok-{N}-task.md`:

```markdown
# Grok Worker {N} Task - PR Comment Resolution

## PR
Resolving comment on PR #{PR_NUMBER}: {PR_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/grok-{N}.log

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines throughout your work.**

## Your Assignment

**Resolve this PR comment:**

{COMMENT_TEXT}

## Log Protocol
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/grok-{N}.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] GROK-{N}: Message\""
```

**Required:** Log STARTED, PROGRESS, COMPLETED

## Instructions
1. Log STARTED
2. Find the relevant file(s) mentioned in the comment
3. Implement the requested fix
4. Log COMPLETED when done
5. **DO NOT commit or push** - Queen handles git

## Begin
Execute your task now.
```

### Step 10: Create Worker-4 Task File (Code Simplification)

**Main Claude writes worker-4 task file BEFORE launching mprocs.**

Write to `.hive/sessions/{SESSION_ID}/worker-4-task.md`:

```markdown
# Worker 4 Task - Code Simplification

## PR
Simplifying code from PR #{PR_NUMBER}: {PR_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-4.log

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines - especially coding standards - during simplification.**

## CRITICAL: Read All Grok Worker Logs First

```powershell
Get-ChildItem ".hive/sessions/{SESSION_ID}/grok-*.log" | ForEach-Object { Write-Host "=== $($_.Name) ==="; Get-Content $_ }
```

Understand:
- What files were modified by each grok worker
- What changes were made to resolve comments

## Your Specialty: Code Simplification

Reference the code-simplifier skill principles:

### Principles
- **Preserve functionality**: Do not change what the code does
- **Apply project standards** from CLAUDE.md
- **Enhance clarity**: Reduce nesting, remove redundant code, improve naming, consolidate related logic, remove obvious comments, avoid nested ternaries
- **Maintain balance**: Avoid over-simplifying, overly clever solutions, merging too many concerns, or removing helpful abstractions
- **Focus scope**: Refine only recently modified code (files touched by grok workers)

### Workflow
1. Identify files modified by grok workers (check their logs)
2. Review for simplification opportunities and standard alignment
3. Apply minimal, safe refactors and keep interfaces stable
4. Verify behavior is unchanged
5. Report only significant readability changes

## Log Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/worker-4.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] WORKER-4: message'"
```

**Required log entries:**
- `STARTED`
- `REVIEWING: {file_path}` - Each file you review
- `SIMPLIFIED: {description}` - What you simplified
- `SKIPPED: {file_path} - RATIONALE: {why}` - If leaving unchanged
- `FILE_CHANGED: {path}`
- `COMPLETED`

## Instructions

1. Log STARTED
2. **Read all grok worker logs completely**
3. Identify all files that were modified
4. Review each modified file for simplification opportunities
5. Apply minimal, safe refactors (do not change behavior!)
6. Log SIMPLIFIED or SKIPPED for each file
7. Log COMPLETED when done
8. **DO NOT commit or push** - Queen handles git

## Begin
Read grok worker logs, then simplify the modified code.
```

### Step 11: Create Tester Task File

**Main Claude writes tester task file BEFORE launching mprocs.** Tester reads task file when spawned.

Write to `.hive/sessions/{SESSION_ID}/tester-task.md`:

```markdown
# Tester Task - Final Quality Gate

## PR
Testing PR #{PR_NUMBER}: {PR_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/tester-1.log

## Session Guidelines (Test Against These!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**Ensure tests validate adherence to these guidelines.**

## Your Task

Verify that grok workers resolved their comments correctly:
- Run tests and verify implementations
- Check for any issues or regressions
- Fix any problems found

## Read Worker Logs

```powershell
Get-ChildItem ".hive/sessions/{SESSION_ID}/grok-*.log" | ForEach-Object { Write-Host "=== $($_.Name) ==="; Get-Content $_ -Tail 20 }
```

## Log Protocol
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/tester-1.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] TESTER-1: Message\""
```

**Required:** Log STARTED, test results, fixes applied, COMPLETED

## Instructions
1. Log STARTED
2. Read all grok worker logs to understand changes made
3. Run project tests (npm test, pytest, etc.)
4. Fix any failures or issues
5. Log COMPLETED when done
6. **DO NOT commit or push** - Queen handles git

## Begin
Execute your task now.
```

### Step 11b: Create Code Quality Task Template

**Main Claude writes code-quality-task-template.md BEFORE launching mprocs.** Queen copies and fills in for each iteration.

Write to `.hive/sessions/{SESSION_ID}/code-quality-task-template.md`:

```markdown
# Code Quality Task - Iteration {N}

## PR
Resolving PR #{PR_NUMBER} comments (Iteration {N})

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/code-quality-{N}.log
- **PR Branch**: {PR_BRANCH}

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

## Your Task

Resolve ALL new comments on PR #{PR_NUMBER}.

### Step 1: Fetch PR Comments

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments
```

### Step 2: Understand Each Comment

For each comment:
1. Read the file and line being commented on
2. Understand what the reviewer is asking for
3. Implement the requested change

### Step 3: Resolve Comments

For each unresolved comment:
1. Make the requested change
2. Log what you changed

### Step 4: Commit and Push (IMPORTANT!)

**You MUST commit and push your changes** so external reviewers can see them:

```bash
git add .
git commit -m "fix: address PR review comments (iteration {N})

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push origin {PR_BRANCH}
```

## Log Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/code-quality-{N}.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] CODE-QUALITY-{N}: message'"
```

**Required log entries:**
- `STARTED`
- `COMMENT: {summary}` - Each comment you're addressing
- `FIXED: {description}` - What you changed
- `COMMITTED: {commit_hash}` - After you commit
- `PUSHED` - After you push
- `COMPLETED`

## Instructions

1. Log STARTED
2. Fetch all PR comments
3. For each unresolved comment:
   - Read the relevant file
   - Make the requested change
   - Log FIXED
4. Commit and push your changes
5. Log COMMITTED and PUSHED
6. Log COMPLETED

## Begin
Resolve the PR comments now.
```

### Step 12: Generate mprocs.yaml (Spawn-on-Demand)

**Only Queen spawns at startup. Queen spawns workers dynamically.**

**CRITICAL PATH FORMAT**: The `cwd` field MUST use Windows-style paths with escaped backslashes.
- Correct: `cwd: "D:\\Code Projects\\MyProject"`
- WRONG: `cwd: "/d/Code Projects/MyProject"` (Git Bash style - will fail!)

Write to `.hive/mprocs.yaml`:

```yaml
# Spawn-on-Demand Hive - PR Comment Resolution
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
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Get-ChildItem .hive/sessions/{SESSION_ID} -Filter *.log -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('=== ' + $_.Name + ' ===') -ForegroundColor Cyan; Get-Content $_.FullName -Tail 8 -ErrorAction SilentlyContinue }; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

**Example `cwd` values:**
- If `PROJECT_ROOT_WINDOWS` = `D:\Code Projects\MyProject`
- Then `cwd` in YAML = `"D:\\Code Projects\\MyProject"`

**Workers are spawned on-demand by Queen** using mprocs TCP commands.

### Step 13: Create Log Files

```bash
cd "{PROJECT_ROOT}"
type nul > ".hive/sessions/{SESSION_ID}/queen.log"
type nul > ".hive/sessions/{SESSION_ID}/worker-4.log"
type nul > ".hive/sessions/{SESSION_ID}/tester-1.log"
# Create grok-{N}.log for each validated comment
```

### Step 14: Launch mprocs

```bash
powershell -Command "Start-Process powershell -WorkingDirectory '{PROJECT_ROOT_WINDOWS}' -ArgumentList '-NoExit', '-Command', 'mprocs --config .hive/mprocs.yaml'"
```

### Step 15: Output Status

```markdown
## Hive PR Comment Resolver Launched!

**Session**: {SESSION_ID}
**PR**: #{PR_NUMBER} - {PR_TITLE}
**Branch**: {PR_BRANCH}

### Phase 1: Validation Complete (3 OpenCode Agents per Comment)

| Comment | BigPickle | GLM 4.7 | Grok Code | Verdict |
|---------|-----------|---------|-----------|--------------|---------|
{VALIDATION_RESULTS_TABLE}

**Validated Comments**: {VALID_COUNT}
**Ties Resolved by Claude**: {TIE_COUNT}

### Phase 2: Resolution Hive

| Pane | Provider | Assignment |
|------|----------|------------|
| queen | Opus 4.5 | Orchestrator (commits/pushes) |
{DYNAMIC_WORKER_TABLE}
| worker-4 | Codex GPT-5.2 | Code simplification |
| tester-1 | Codex GPT-5.2 | Final testing |
| code-quality-{N} | **Cursor CLI** (Opus 4.5) | PR comment resolution (up to 5 cycles) |

### Workflow

1. Queen checks out PR branch
2. Grok workers resolve their assigned comments (parallel)
3. Worker-4 simplifies code (after grok workers complete)
4. Tester verifies
5. Queen curates learnings (appends to .ai-docs/learnings.jsonl)
6. Queen commits, pushes to PR branch
7. **Code Quality Loop** (up to 5 x 10-minute cycles):
   - Wait 10 minutes for external reviewers
   - Spawn code-quality-{N} agent (Cursor CLI + Opus 4.5)
   - Agent resolves comments, commits, pushes
   - Repeat until no new comments or max 5 cycles
```

---

## QUALITY-ONLY MODE

When `--quality-only` flag is present, skip Phases 1-5 and go directly to Code Quality Loop.

**Use case**: PR already has 15+ reviewer comments from external tools (Gemini, Codex, Code Rabbit) and you want to automate resolving them.

### Step 1: Check Prerequisites (same as full mode)

```bash
mprocs --version
```

### Step 2: Fetch PR Details

```bash
gh pr view {PR_NUMBER} --json title,headRefName
```

Extract:
- `PR_TITLE`
- `PR_BRANCH` (headRefName)

### Step 3: Generate Session Variables

```bash
TIMESTAMP=$(powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'")
PROJECT_ROOT_WINDOWS=$(powershell -NoProfile -Command "(Get-Location).Path")
MPROCS_PORT=$((4000 + ${TIMESTAMP: -4}))
SESSION_ID="${TIMESTAMP}-quality-loop-${PR_NUMBER}"
```

### Step 4: Create Session Directory

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
```

### Step 5: Create Minimal Queen Prompt (Quality Loop Only)

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen Agent - Quality Loop Only for PR #{PR_NUMBER}

You are the **Queen** running ONLY the Code Quality Loop for an existing PR.

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/queen.log
- **PR Number**: {PR_NUMBER}
- **PR Branch**: {PR_BRANCH}
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}

## Mode: QUALITY-ONLY

This is a lightweight session - no workers, no validation. Your ONLY job is to run the Code Quality Loop.

## Log Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Message\""
```

## Git Setup

```bash
git checkout {PR_BRANCH}
git pull origin {PR_BRANCH}
```

## Code Quality Loop (Up to 5 Cycles)

**Loop Parameters:**
- **Wait time per cycle**: 10 minutes
- **Maximum cycles**: 5
- **Total max wait**: 50 minutes

### For N = 1 to 5:

#### Step 1: Wait for Reviews (First cycle: skip wait, subsequent: 10 min)

**Cycle 1:** Skip wait - comments already exist
**Cycles 2-5:**
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Code Quality Loop - Cycle {N}. Waiting 10 minutes...\"; Start-Sleep -Seconds 600"
```

#### Step 2: Check for Comments

```bash
NEW_COMMENTS=$(gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments --jq 'length')
```

If NEW_COMMENTS = 0 → END (success)

#### Step 3: Write and Spawn Code Quality Agent (Cursor CLI)

**Write task file** `.hive/sessions/{SESSION_ID}/code-quality-{N}-task.md`:

```markdown
# Code Quality Task - Iteration {N}

## PR
Resolving PR #{PR_NUMBER} comments (Iteration {N})

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/code-quality-{N}.log
- **PR Branch**: {PR_BRANCH}

## Your Task

Resolve ALL comments on PR #{PR_NUMBER}.

### Step 1: Fetch PR Comments

```bash
gh api repos/{owner}/{repo}/pulls/{PR_NUMBER}/comments
```

### Step 2: For Each Comment

1. Read the file and line
2. Understand what reviewer wants
3. Implement the change
4. Log FIXED

### Step 3: Commit and Push

```bash
git add .
git commit -m "fix: address PR review comments (iteration {N})

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push origin {PR_BRANCH}
```

## Log Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/code-quality-{N}.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] CODE-QUALITY-{N}: message'"
```

**Required:** STARTED, COMMENT:, FIXED:, COMMITTED:, PUSHED, COMPLETED

## Begin
Resolve the PR comments now.
```

**Create log file:**
```powershell
New-Item -Path ".hive/sessions/{SESSION_ID}/code-quality-{N}.log" -ItemType File -Force
```

**Write spawn .bat:**
```powershell
Set-Content -Path ".hive/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.hive/sessions/{SESSION_ID}/code-quality-{N}-task.md and execute.\\\"\", \"name\": \"code-quality-{N}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

**Execute:**
```bash
.hive/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat
```

#### Step 4: Monitor

Wait for COMPLETED in code-quality-{N}.log, then loop.

### Loop Termination

- No comments after wait → SUCCESS
- N = 5 → END (max reached)

## Begin

1. Log STARTED
2. Checkout PR branch
3. Start Code Quality Loop at Cycle 1 (skip initial wait)
```

### Step 6: Create Log Files

```bash
type nul > ".hive/sessions/{SESSION_ID}/queen.log"
```

### Step 7: Generate mprocs.yaml (Minimal)

```yaml
server: 127.0.0.1:{MPROCS_PORT}

procs:
  queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS}"
    env:
      HIVE_ROLE: "queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Get-ChildItem .hive/sessions/{SESSION_ID} -Filter *.log -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('=== ' + $_.Name + ' ===') -ForegroundColor Cyan; Get-Content $_.FullName -Tail 8 -ErrorAction SilentlyContinue }; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS}"
```

### Step 8: Launch mprocs

```bash
powershell -Command "Start-Process powershell -WorkingDirectory '{PROJECT_ROOT_WINDOWS}' -ArgumentList '-NoExit', '-Command', 'mprocs --config .hive/mprocs.yaml'"
```

### Step 9: Output Status

```markdown
## Quality-Only Loop Launched!

**Session**: {SESSION_ID}
**PR**: #{PR_NUMBER} - {PR_TITLE}
**Branch**: {PR_BRANCH}
**Mode**: QUALITY-ONLY (Code Quality Loop only)

### Loop Parameters
- **Wait per cycle**: 10 minutes (first cycle: immediate)
- **Max cycles**: 5
- **Agent**: Cursor CLI (Opus 4.5)

### Workflow
1. Queen checks out PR branch
2. Fetches existing comments
3. Spawns code-quality-1 agent (immediate - no wait)
4. Agent resolves comments, commits, pushes
5. Wait 10 min, check for new comments
6. Repeat up to 5 cycles

This will automate resolving your PR's review comments!
```

---

## Usage

```bash
# Full mode - validate comments, resolve with workers, then quality loop
/resolve-hive-comments 123

# Quality-only mode - skip straight to code quality loop
/resolve-hive-comments 123 --quality-only
```
