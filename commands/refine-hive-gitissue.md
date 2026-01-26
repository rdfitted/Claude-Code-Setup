---
description: Refine a GitHub issue using multi-agent Hive coordination
argument-hint: "<issue-number> [rewrite|comment]"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Refine Hive Git Issue - Multi-Agent Issue Refinement

Launch a Hive session to reassess and refine an existing GitHub issue.

## Arguments

- `<issue-number>`: GitHub issue number to refine
- `[rewrite|comment]`: Optional - "rewrite" to update the issue body, "comment" to add a comment (default: comment)

## Workflow

### Step 1: Check Prerequisites

```bash
mprocs --version
```

If mprocs not installed, tell user to install it and STOP.

### Step 2: Parse Arguments

Extract:
- `ISSUE_NUMBER`: The issue number
- `REFINE_MODE`: "rewrite" or "comment" (default: comment)

### Step 3: Fetch Issue Details

```bash
gh issue view {ISSUE_NUMBER} --json title,body,labels,state,comments,createdAt,author
```

Extract all issue details including existing comments.

### Step 4: Generate Session

```bash
powershell -Command "Get-Date -Format 'yyyyMMdd-HHmmss'"
powershell -NoProfile -Command "(Get-Location).Path"
```

```
TIMESTAMP = result of Get-Date
SESSION_ID = {TIMESTAMP}-refine-issue-{ISSUE_NUMBER}
SESSION_PATH = .hive/sessions/{SESSION_ID}
PROJECT_ROOT_WINDOWS = PowerShell path (e.g., D:\Code Projects\MyProject)
GEMINI_MODEL = "gemini-3-flash-preview"  # Refinement = research, use Flash
```

**CRITICAL - Path Format for mprocs.yaml:**
- mprocs on Windows REQUIRES Windows-style paths with escaped backslashes
- Use `PROJECT_ROOT_WINDOWS` (from PowerShell) for the `cwd` field
- Format in YAML: `"D:\\Code Projects\\MyProject"` (double backslashes)
- NEVER use Git Bash paths like `/d/Code Projects/...` - mprocs will fail!

### Step 5: Create Session Directory

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
```

### Step 6: Create tasks.json

Write to `.hive/sessions/{SESSION_ID}/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "session_status": "active",
  "queen_status": "initializing",
  "task_type": "refine-issue",
  "refine_mode": "{REFINE_MODE}",
  "github_issue": {
    "number": "{ISSUE_NUMBER}",
    "title": "{ISSUE_TITLE}",
    "body": "{ISSUE_BODY}",
    "labels": "{ISSUE_LABELS}",
    "comments": "{EXISTING_COMMENTS}"
  },
  "workers": {
    "worker-1": {
      "provider": "claude-opus-4.5",
      "specialty": "backend-architecture",
      "status": "active"
    },
    "worker-2": {
      "provider": "gemini-3-pro",
      "specialty": "ui-frontend",
      "status": "active"
    },
    "worker-3": {
      "provider": "codex-gpt-5.2",
      "specialty": "code-simplification",
      "status": "active"
    },
    "worker-4": {
      "provider": "codex-gpt-5.2",
      "specialty": "bugfix-debugging",
      "status": "active"
    }
  },
  "tasks": [],
  "synthesis": {
    "status": "pending",
    "result_file": "results.md"
  }
}
```

### Step 7: Create Queen Prompt for Issue Refinement

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen Agent - Refine GitHub Issue

You are the **Queen** orchestrating a Hive to refine GitHub issue #{ISSUE_NUMBER}.

## Your Mission

Reassess and refine this existing GitHub issue. Mode: **{REFINE_MODE}**

- **rewrite**: Update the issue body with improved content
- **comment**: Add a detailed comment with new findings/context

## Current Issue

**Issue #{ISSUE_NUMBER}**: {ISSUE_TITLE}

### Original Body
{ISSUE_BODY}

### Existing Comments
{EXISTING_COMMENTS}

### Labels
{ISSUE_LABELS}

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: {SESSION_PATH}
- **Refine Mode**: {REFINE_MODE}
- **Your Log**: {SESSION_PATH}/queen.log

## Your Team

| Worker | Provider | Strengths |
|--------|----------|-----------|
| worker-1 | Opus 4.5 | Deep analysis, architecture review, complex reasoning, finding gaps in documentation |
| worker-2 | Gemini 3 Pro | UI/UX perspective, user-facing impact, frontend considerations |
| worker-3 | Codex GPT-5.2 | Code simplification - review and simplify code changes from this session |
| worker-4 | Codex GPT-5.2 | Bug verification, reproduction steps, edge cases, technical accuracy |

**You have full autonomy to delegate as needed.**

## Refinement Process

### Phase 1: Reassess Current State

Ask yourself and your workers:
- Has the codebase changed since this issue was created?
- Is the issue still relevant?
- Is the description accurate and complete?
- Are there missing details, reproduction steps, or context?
- Have related issues or PRs been created?
- Are there new edge cases or considerations?

### Phase 2: Investigate

**Task Assignment Format** (add to tasks array in tasks.json):
```json
{
  "id": "task-1",
  "assigned_to": "worker-1",
  "status": "pending",
  "description": "Task description here",
  "created": "ISO_TIMESTAMP",
  "poll_interval": 75
}
```

**Poll Interval Options** (set based on task complexity):

| Task Size | `poll_interval` | When to Use |
|-----------|-----------------|-------------|
| Quick task | `75` | Simple verifications, quick checks |
| Medium task | `180` | Moderate complexity, multi-file investigation |
| Large task | `300` | Complex analysis, extensive codebase review |

**Worker Dismissal** (optional - dismiss unneeded workers):

If a worker's specialty is not needed for this refinement, assign them a shutdown task:
```json
{
  "id": "shutdown-worker-2",
  "assigned_to": "worker-2",
  "status": "pending",
  "description": "SHUTDOWN: This issue refinement doesn't need frontend expertise.",
  "created": "ISO_TIMESTAMP"
}
```

Workers recognize tasks starting with "SHUTDOWN:" and will exit immediately.

Delegate tasks to gather updated information:
- "Verify the current state of [affected code]"
- "Check if [described behavior] still occurs"
- "Find any new related files or changes"
- "Identify missing context or reproduction steps"

### Phase 3: Synthesize Refinements

Based on worker findings, determine what refinements are needed:
- Corrections to inaccurate information
- Additional context or details
- Updated reproduction steps
- New findings or edge cases
- Links to related code or issues
- Revised scope or priority recommendations

### Phase 4: Apply Refinement

**If mode is "rewrite":**
```bash
gh issue edit {ISSUE_NUMBER} --body "NEW_BODY_CONTENT"
```

Write a completely updated issue body that:
- Preserves valid original information
- Corrects any inaccuracies
- Adds new findings and context
- Improves structure and clarity

**If mode is "comment":**
```bash
gh issue comment {ISSUE_NUMBER} --body "COMMENT_CONTENT"
```

Write a detailed comment that:
- Summarizes the reassessment
- Highlights what has changed
- Provides new findings
- Suggests any scope/priority changes

## Coordination Files

| File | Purpose |
|------|---------|
| `{SESSION_PATH}/tasks.json` | Task assignments |
| `{SESSION_PATH}/queen.log` | Your activity log |
| `{SESSION_PATH}/worker-*.log` | Worker outputs |
| `{SESSION_PATH}/results.md` | Final refinement content |

### Phase 5: Session Termination (CRITICAL)

**When refinement is complete, you MUST signal session end:**

Update `tasks.json` to set:
```json
"session_status": "complete"
```

This tells all workers to stop polling and exit gracefully.

## Begin

1. Read the current issue carefully
2. Delegate reassessment tasks to workers
3. Gather findings about current codebase state
4. Synthesize refinements
5. Apply the refinement (rewrite or comment)
6. Set session_status to "complete"
7. Report completion

Start by announcing: "Queen initialized for issue refinement. Reassessing issue #{ISSUE_NUMBER}: {ISSUE_TITLE} (Mode: {REFINE_MODE})"
```

### Step 8: Create Worker Prompts

Create these worker prompt files in `.hive/sessions/{SESSION_ID}/`:

**worker-1-prompt.md:**
```markdown
# Worker 1 - Deep Analysis Specialist

You are **Worker 1** in a Hive session refining GitHub issue #{ISSUE_NUMBER}.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-1
- **Your Log**: {SESSION_PATH}/worker-1.log
- **Specialty**: Deep analysis, architecture review, complex reasoning

## Task Loop (CRITICAL - FOLLOW EXACTLY)

You MUST run this loop continuously until session ends:

```
next_sleep = 75  # Default poll interval
WHILE session is active:
  1. Read tasks.json
  2. Check for tasks assigned to "worker-1" with status "pending"
  3. IF task found:
     - IF task description starts with "SHUTDOWN:":
       - Update task status to "completed" in tasks.json
       - Announce "Worker 1 dismissed by Queen. Exiting." and EXIT
     - Update task status to "in-progress" in tasks.json
     - Execute the task thoroughly
     - Log progress to your log file
     - Update task status to "completed" with summary in tasks.json
     - IF task has "poll_interval" field: next_sleep = poll_interval
  4. IF no pending tasks:
     - Check if tasks.json has "session_status": "complete"
     - IF complete: announce "Worker 1 signing off" and EXIT
     - IF not complete: Run `Start-Sleep -Seconds {next_sleep}` then CONTINUE loop
  5. REPEAT from step 1
```

### Shutdown Tasks

If Queen assigns a task with description starting with "SHUTDOWN:", exit immediately after marking it complete.

### Dynamic Polling Interval

Queen sets `poll_interval` in task assignments:
- `75` = Quick tasks (default)
- `180` = Medium tasks (3 min)
- `300` = Large tasks (5 min)

### IMPORTANT: Do Not Exit Early

- **DO NOT** stop polling just because you completed a task
- **DO NOT** exit if tasks.json has no tasks for you yet
- **DO NOT** terminate until you see "session_status": "complete" in tasks.json

## Begin

Announce: "Worker 1 ready for issue #{ISSUE_NUMBER} refinement. Starting task polling loop..."
```

**worker-2-prompt.md:**
```markdown
# Worker 2 - UI/UX Perspective Specialist

You are **Worker 2** in a Hive session refining GitHub issue #{ISSUE_NUMBER}.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-2
- **Your Log**: {SESSION_PATH}/worker-2.log
- **Specialty**: UI/UX perspective, user-facing impact, frontend considerations

## Task Loop (CRITICAL - FOLLOW EXACTLY)

You MUST run this loop continuously until session ends:

```
next_sleep = 75  # Default poll interval
WHILE session is active:
  1. Read tasks.json
  2. Check for tasks assigned to "worker-2" with status "pending"
  3. IF task found:
     - IF task description starts with "SHUTDOWN:":
       - Update task status to "completed" in tasks.json
       - Announce "Worker 2 dismissed by Queen. Exiting." and EXIT
     - Update task status to "in-progress" in tasks.json
     - Execute the task thoroughly
     - Log progress to your log file
     - Update task status to "completed" with summary in tasks.json
     - IF task has "poll_interval" field: next_sleep = poll_interval
  4. IF no pending tasks:
     - Check if tasks.json has "session_status": "complete"
     - IF complete: announce "Worker 2 signing off" and EXIT
     - IF not complete: Run `Start-Sleep -Seconds {next_sleep}` then CONTINUE loop
  5. REPEAT from step 1
```

### Shutdown Tasks

If Queen assigns a task with description starting with "SHUTDOWN:", exit immediately after marking it complete.

### Dynamic Polling Interval

Queen sets `poll_interval` in task assignments:
- `75` = Quick tasks (default)
- `180` = Medium tasks (3 min)
- `300` = Large tasks (5 min)

**CRITICAL**: Use `Start-Sleep` - it blocks locally with NO API requests during wait.

### IMPORTANT: Do Not Exit Early

- **DO NOT** stop polling just because you completed a task
- **DO NOT** exit if tasks.json has no tasks for you yet
- **DO NOT** terminate until you see "session_status": "complete" in tasks.json

## Begin

Announce: "Worker 2 ready for issue #{ISSUE_NUMBER} refinement. Starting task polling loop..."
```

**worker-3-prompt.md:**
```markdown
# Worker 3 - Code Simplification Specialist

You are **Worker 3** in a Hive session refining GitHub issue #{ISSUE_NUMBER}.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-3
- **Your Log**: {SESSION_PATH}/worker-3.log
- **Specialty**: Code simplification, cleanup, readability improvements

## Your Mission

After other workers implement fixes, you review and simplify the code they produced. Enhance clarity, consistency, and maintainability while preserving exact functionality.

**IMPORTANT**: Use the `code-simplifier` skill to perform simplification. Invoke it with `/code-simplifier` when you have code to review.

### Simplification Principles

1. **Preserve Functionality**: Never change what the code does - only how it does it
2. **Reduce Complexity**: Eliminate unnecessary nesting, redundant code, and over-abstraction
3. **Improve Readability**: Clear variable names, explicit logic, avoid clever one-liners
4. **Apply Standards**: Follow project conventions from CLAUDE.md
5. **Minimal Changes**: Only simplify code modified in this session

## Task Loop (CRITICAL - FOLLOW EXACTLY)

You MUST run this loop continuously until session ends:

```
first_poll = true
next_sleep = 75  # Default poll interval
WHILE session is active:
  1. IF first_poll:
     - Announce: "Worker 3 starting with 3-minute initial wait (letting others produce code first)..."
     - Run `Start-Sleep -Seconds 180` (3 minutes)
     - first_poll = false
  2. Read tasks.json
  3. Check for tasks assigned to "worker-3" with status "pending"
  4. IF task found:
     - IF task description starts with "SHUTDOWN:":
       - Update task status to "completed" in tasks.json
       - Announce "Worker 3 dismissed by Queen. Exiting." and EXIT
     - Update task status to "in-progress" in tasks.json
     - Execute the task: review and simplify code changes from this session
     - Log progress to your log file
     - Update task status to "completed" with summary in tasks.json
     - IF task has "poll_interval" field: next_sleep = poll_interval
  5. IF no pending tasks:
     - Check if tasks.json has "session_status": "complete"
     - IF complete: announce "Worker 3 signing off" and EXIT
     - IF not complete: Run `Start-Sleep -Seconds {next_sleep}` then CONTINUE loop
  6. REPEAT from step 2
```

### Shutdown Tasks

If Queen assigns a task with description starting with "SHUTDOWN:", exit immediately after marking it complete.

### CRITICAL: Initial 3-Minute Wait

**Worker 3 waits 3 minutes before first poll.** This allows:
- Other workers to produce code first
- Queen to analyze what needs simplification
- Code to be ready before simplification review

### Dynamic Polling Interval

Queen sets `poll_interval` in task assignments:
- `75` = Quick tasks (default)
- `180` = Medium tasks (3 min)
- `300` = Large tasks (5 min)

### IMPORTANT: Do Not Exit Early

- **DO NOT** stop polling just because you completed a task
- **DO NOT** exit if tasks.json has no tasks for you yet
- **DO NOT** terminate until you see "session_status": "complete" in tasks.json

## Begin

Announce: "Worker 3 ready for code simplification. Starting with 3-minute initial wait..."
```

**worker-4-prompt.md:**
```markdown
# Worker 4 - Technical Accuracy Specialist

You are **Worker 4** in a Hive session refining GitHub issue #{ISSUE_NUMBER}.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-4
- **Your Log**: {SESSION_PATH}/worker-4.log
- **Specialty**: Bug verification, reproduction steps, edge cases, technical accuracy

## Task Loop (CRITICAL - FOLLOW EXACTLY)

You MUST run this loop continuously until session ends:

```
first_poll = true
next_sleep = 75  # Default poll interval
WHILE session is active:
  1. IF first_poll:
     - Announce: "Worker 4 starting with 5-minute initial wait (others investigate first)..."
     - Run `Start-Sleep -Seconds 300` (5 minutes)
     - first_poll = false
  2. Read tasks.json
  3. Check for tasks assigned to "worker-4" with status "pending"
  4. IF task found:
     - IF task description starts with "SHUTDOWN:":
       - Update task status to "completed" in tasks.json
       - Announce "Worker 4 dismissed by Queen. Exiting." and EXIT
     - Update task status to "in-progress" in tasks.json
     - Execute the task thoroughly
     - Log progress to your log file
     - Update task status to "completed" with summary in tasks.json
     - IF task has "poll_interval" field: next_sleep = poll_interval
  5. IF no pending tasks:
     - Check if tasks.json has "session_status": "complete"
     - IF complete: announce "Worker 4 signing off" and EXIT
     - IF not complete: Run `Start-Sleep -Seconds {next_sleep}` then CONTINUE loop
  6. REPEAT from step 2
```

### Shutdown Tasks

If Queen assigns a task with description starting with "SHUTDOWN:", exit immediately after marking it complete. (Rare for accuracy checking worker.)

### CRITICAL: Initial 5-Minute Wait

**Worker 4 waits 5 minutes before first poll.** This allows:
- Other workers to complete initial investigation
- Queen to analyze and assign verification tasks
- Dependencies to be ready before accuracy checking

### Dynamic Polling Interval

Queen sets `poll_interval` in task assignments:
- `75` = Quick tasks (default)
- `180` = Medium tasks (3 min)
- `300` = Large tasks (5 min)

### IMPORTANT: Do Not Exit Early

- **DO NOT** stop polling just because you completed a task
- **DO NOT** exit if tasks.json has no tasks for you yet
- **DO NOT** terminate until you see "session_status": "complete" in tasks.json

## Begin

Announce: "Worker 4 ready for issue #{ISSUE_NUMBER} refinement. Starting with 5-minute initial wait..."
```

### Step 9: Get PROJECT_ROOT

```bash
# Get current working directory (this is PROJECT_ROOT)
pwd
```

### Step 10: Generate mprocs.yaml (CRITICAL - FOLLOW EXACTLY)

**IMPORTANT**: Generate the mprocs.yaml file by writing THIS EXACT CONTENT with only `{SESSION_ID}` and `{PROJECT_ROOT}` substituted:

Use the Write tool to create `.hive/mprocs.yaml` with this content:

```yaml
# mprocs configuration for Hive session: {SESSION_ID}
# Gemini CLI: using latest installed version
procs:
  queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      HIVE_SESSION_ID: "{SESSION_ID}"

  worker-1-backend:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are WORKER 1. Read .hive/sessions/{SESSION_ID}/worker-1-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "worker"
      HIVE_WORKER_ID: "1"
      HIVE_SPECIALTY: "backend-architecture"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      HIVE_SESSION_ID: "{SESSION_ID}"

  worker-2-frontend:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER 2. Read .hive/sessions/{SESSION_ID}/worker-2-prompt.md'"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "worker"
      HIVE_WORKER_ID: "2"
      HIVE_SPECIALTY: "ui-frontend"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      HIVE_SESSION_ID: "{SESSION_ID}"

  worker-3-simplify:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER 3. Read .hive/sessions/{SESSION_ID}/worker-3-prompt.md'"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "worker"
      HIVE_WORKER_ID: "3"
      HIVE_SPECIALTY: "code-simplification"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      HIVE_SESSION_ID: "{SESSION_ID}"

  worker-4-bugfix:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER 4. Read .hive/sessions/{SESSION_ID}/worker-4-prompt.md'"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "worker"
      HIVE_WORKER_ID: "4"
      HIVE_SPECIALTY: "bugfix-debugging"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      HIVE_SESSION_ID: "{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 10 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

**SUBSTITUTION RULES:**
- Replace `{SESSION_ID}` with the actual session ID (e.g., `20260114-123456-refine-issue-42`)
- Replace `{PROJECT_ROOT}` with the current working directory path
- Do NOT modify any other part of the YAML
- Keep all single quotes exactly as shown
- Keep all escaped single quotes (`''`) exactly as shown

### Step 11: Create Empty Log Files

```bash
cd "{PROJECT_ROOT}" && type nul > ".hive/sessions/{SESSION_ID}/queen.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-1.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-2.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-3.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-4.log"
```

### Step 12: Launch mprocs

Launch mprocs in a new PowerShell window from the PROJECT_ROOT:

```bash
powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd \"{PROJECT_ROOT}\"; mprocs --config .hive/mprocs.yaml'"
```

**Note**: If PROJECT_ROOT contains spaces, ensure it's properly quoted in the command.

### Step 13: Output Status

```markdown
## Hive Issue Refiner Launched!

**Session**: {SESSION_ID}
**Task**: Refine GitHub Issue #{ISSUE_NUMBER}
**Mode**: {REFINE_MODE}
**Title**: {ISSUE_TITLE}

### Team

| Pane | Provider | Role |
|------|----------|------|
| queen | Opus 4.5 | Orchestrator - Reassessing and refining |
| worker-1 | Opus 4.5 | Deep analysis and verification |
| worker-2 | Gemini 3 Pro | UI/UX perspective |
| worker-3 | Codex GPT-5.2 | Code simplification - cleanup & readability |
| worker-4 | Codex GPT-5.2 | Technical accuracy and edge cases |

### Refinement Flow

1. Queen reviews current issue state
2. Workers investigate current codebase
3. Queen synthesizes findings
4. Queen applies refinement ({REFINE_MODE})

The hive will reassess and refine the issue!
```
