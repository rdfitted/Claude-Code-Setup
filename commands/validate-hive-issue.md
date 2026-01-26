---
description: Validate a GitHub issue using multi-agent Hive coordination
argument-hint: "<issue-number-or-url>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Validate Hive Issue - Multi-Agent GitHub Issue Validation

Launch a Hive session to collaboratively validate whether a GitHub issue is well-formed, accurate, and actionable.

## Purpose

This command validates an issue by:
1. Checking if the described problem/feature actually exists in the codebase
2. Verifying file paths, line numbers, and code references
3. Assessing if the issue is clear, actionable, and complete
4. Determining if the issue should be accepted, needs refinement, or rejected

## Arguments

- `<issue-number-or-url>`: GitHub issue number (e.g., `123`) or full URL

## Workflow

### Step 1: Check Prerequisites

```bash
mprocs --version
```

If mprocs not installed, tell user to install it and STOP.

### Step 2: Fetch Issue Details

```bash
gh issue view {ISSUE_NUMBER} --json title,body,labels,state,comments
```

Extract:
- `ISSUE_TITLE`
- `ISSUE_BODY`
- `ISSUE_LABELS`

### Step 3: Generate Session Variables

```bash
# Get timestamp
powershell -Command "Get-Date -Format 'yyyyMMdd-HHmmss'"

# Get current working directory in Windows format
powershell -NoProfile -Command "(Get-Location).Path"
```

Set variables:
```
TIMESTAMP = result of Get-Date command
SESSION_ID = {TIMESTAMP}-validate-issue-{ISSUE_NUMBER}
PROJECT_ROOT_WINDOWS = PowerShell path (e.g., D:\Code Projects\MyProject)
GEMINI_MODEL = "gemini-3-flash-preview"  # Validation = investigation, use Flash
```

**CRITICAL - Path Format for mprocs.yaml:**
- mprocs on Windows REQUIRES Windows-style paths with escaped backslashes
- Use `PROJECT_ROOT_WINDOWS` (from PowerShell) for the `cwd` field
- Format in YAML: `"D:\\Code Projects\\MyProject"` (double backslashes)
- NEVER use Git Bash paths like `/d/Code Projects/...` - mprocs will fail!

### Step 4: Create Session Directory

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
```

### Step 5: Create tasks.json

Write to `.hive/sessions/{SESSION_ID}/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "queen_status": "initializing",
  "task_type": "validate-issue",
  "github_issue": {
    "number": "{ISSUE_NUMBER}",
    "title": "{ISSUE_TITLE}",
    "body": "{ISSUE_BODY}",
    "labels": "{ISSUE_LABELS}"
  },
  "workers": {
    "worker-1": {
      "provider": "claude-opus-4.5",
      "specialty": "technical-validation",
      "status": "active"
    },
    "worker-2": {
      "provider": "gemini-3-pro",
      "specialty": "file-verification",
      "status": "active"
    },
    "worker-3": {
      "provider": "codex-gpt-5.2",
      "specialty": "code-simplification",
      "status": "active"
    },
    "worker-4": {
      "provider": "codex-gpt-5.2",
      "specialty": "accuracy-checking",
      "status": "active"
    }
  },
  "tasks": [],
  "synthesis": {
    "status": "pending",
    "result_file": "validation-report.md"
  }
}
```

### Step 6: Create Queen Prompt for Issue Validation

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen Agent - Validate GitHub Issue

You are the **Queen** orchestrating a Hive to validate GitHub issue #{ISSUE_NUMBER}.

## Your Mission

Validate this GitHub issue and produce a validation report determining whether the issue is:
- **VALID**: Well-formed, accurate, and actionable
- **NEEDS_REFINEMENT**: Has issues but salvageable with updates
- **INVALID**: Should be closed or rejected

## Issue Details

**Issue #{ISSUE_NUMBER}**: {ISSUE_TITLE}

{ISSUE_BODY}

**Labels**: {ISSUE_LABELS}

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Task Type**: Validate GitHub Issue
- **Your Log**: .hive/sessions/{SESSION_ID}/queen.log

## Your Team

You have 4 specialized workers for validation. Here are their strengths:

| Worker | Provider | Validation Focus |
|--------|----------|------------------|
| worker-1 | Opus 4.5 | Technical accuracy - verify code references, architecture claims, API descriptions |
| worker-2 | Gemini 3 Pro | File verification - check if files exist, paths are correct, line numbers valid |
| worker-3 | Codex GPT-5.2 | Code simplification - review and simplify code changes from this session |
| worker-4 | Codex GPT-5.2 | Problem verification - confirm the bug exists or feature is missing, test reproducibility |

**You have full autonomy to delegate validation tasks as you see fit.**

## Validation Checklist

The workers should collectively verify:

### 1. Issue Clarity
- [ ] Title clearly describes the problem/feature
- [ ] Description is detailed enough to act on
- [ ] Acceptance criteria are defined (if applicable)
- [ ] Steps to reproduce are provided (for bugs)

### 2. Technical Accuracy
- [ ] File paths mentioned exist in the codebase
- [ ] Line numbers are accurate
- [ ] Code snippets are correct
- [ ] API/function names are accurate
- [ ] Technical claims can be verified

### 3. Problem/Feature Validity
- [ ] The described problem actually exists
- [ ] The feature is actually missing
- [ ] Not a duplicate of existing issue
- [ ] Not already fixed in codebase

### 4. Actionability
- [ ] Scope is reasonable for a single issue
- [ ] Not too vague or too broad
- [ ] Implementation path is feasible
- [ ] No blocking dependencies

## Validation Process

### Phase 1: Understand the Issue
1. Read the issue details above
2. Identify key claims to verify
3. Plan your delegation strategy

### Phase 2: Delegate Verification Tasks
Assign specific verification tasks to workers. They should INVESTIGATE ONLY (not implement).

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
| Medium task | `180` | Moderate complexity, multi-file verification |
| Large task | `300` | Complex investigation, extensive verification |

**Worker Dismissal** (optional - dismiss unneeded workers):

If a worker's specialty is not needed for this validation, assign them a shutdown task:
```json
{
  "id": "shutdown-worker-2",
  "assigned_to": "worker-2",
  "status": "pending",
  "description": "SHUTDOWN: This issue validation doesn't need frontend expertise.",
  "created": "ISO_TIMESTAMP"
}
```

Workers recognize tasks starting with "SHUTDOWN:" and will exit immediately.

Example tasks:
- "Verify file `src/auth/login.ts` exists and contains the function `handleLogin`"
- "Check if the bug described at line 42 is reproducible"
- "Verify the API endpoint `/api/users` behaves as described"
- "Search for existing issues or PRs related to this problem"

### Phase 3: Monitor & Coordinate
Watch worker logs for findings.

### Phase 4: Synthesize Validation Report
Compile all findings into a validation report.

## Coordination Files

| File | Purpose |
|------|---------|
| `.hive/sessions/{SESSION_ID}/tasks.json` | Task assignments |
| `.hive/sessions/{SESSION_ID}/queen.log` | Your activity log |
| `.hive/sessions/{SESSION_ID}/worker-*.log` | Worker outputs |
| `.hive/sessions/{SESSION_ID}/validation-report.md` | Final validation report |

## Final Report Format

Write to `.hive/sessions/{SESSION_ID}/validation-report.md`:

```markdown
# Issue Validation Report: #{ISSUE_NUMBER}

## Summary

**Issue**: {ISSUE_TITLE}
**Verdict**: VALID | NEEDS_REFINEMENT | INVALID
**Confidence**: HIGH | MEDIUM | LOW

## Validation Results

### Issue Clarity
| Criterion | Status | Notes |
|-----------|--------|-------|
| Clear title | PASS/FAIL | ... |
| Detailed description | PASS/FAIL | ... |
| Acceptance criteria | PASS/FAIL/NA | ... |
| Reproduction steps | PASS/FAIL/NA | ... |

### Technical Accuracy
| Claim | Verified | Notes |
|-------|----------|-------|
| File: path/to/file.ts | YES/NO | ... |
| Line numbers | YES/NO | ... |
| Code snippets | YES/NO | ... |

### Problem/Feature Validity
- **Problem exists**: YES/NO/PARTIALLY
- **Not a duplicate**: YES/NO (link if duplicate)
- **Not already fixed**: YES/NO (PR if fixed)

### Actionability
- **Reasonable scope**: YES/NO
- **Feasible implementation**: YES/NO
- **Blocking dependencies**: NONE/LIST

## Worker Findings

### Worker 1 (Technical Validation)
{Summary of findings}

### Worker 2 (File Verification)
{Summary of findings}

### Worker 3 (Problem Verification)
{Summary of findings}

## Recommendations

### If VALID:
- Ready to work on
- Suggested priority: HIGH/MEDIUM/LOW

### If NEEDS_REFINEMENT:
1. [Specific correction needed]
2. [Missing information to add]
3. [Clarification required]

### If INVALID:
- Reason: [Why the issue should be closed]
- Suggested action: [Close as duplicate / Close as not reproducible / etc.]

---
*Validated by Hive session {SESSION_ID}*
*Workers: 3 | Checks: N | Confidence: HIGH/MEDIUM/LOW*
```

## Begin

Start by announcing: "Queen initialized for issue validation. Analyzing issue #{ISSUE_NUMBER}: {ISSUE_TITLE}"
```

### Step 7: Create Worker Prompts

Create these worker prompt files in `.hive/sessions/{SESSION_ID}/`:

**worker-1-prompt.md:**
```markdown
# Worker 1 - Technical Validation Specialist

You are **Worker 1** in a Hive session validating GitHub issue #{ISSUE_NUMBER}.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-1
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-1.log
- **Specialty**: Technical accuracy, code verification, architecture claims

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
- Queen may assign tasks sequentially - you MUST keep polling

## Begin

Announce: "Worker 1 ready for issue #{ISSUE_NUMBER} validation. Starting task polling loop..."
```

**worker-2-prompt.md:**
```markdown
# Worker 2 - File Verification Specialist

You are **Worker 2** in a Hive session validating GitHub issue #{ISSUE_NUMBER}.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-2
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-2.log
- **Specialty**: File existence, path verification, line number accuracy

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
- Queen assigns tasks SEQUENTIALLY - your task may come AFTER worker-1 finishes

## Begin

Announce: "Worker 2 ready for issue #{ISSUE_NUMBER} validation. Starting task polling loop..."
```

**worker-3-prompt.md:**
```markdown
# Worker 3 - Code Simplification Specialist

You are **Worker 3** in a Hive session validating GitHub issue #{ISSUE_NUMBER}.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-3
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-3.log
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
- Queen assigns tasks SEQUENTIALLY - your task may come after implementation

## Begin

Announce: "Worker 3 ready for code simplification. Starting with 3-minute initial wait..."
```

**worker-4-prompt.md:**
```markdown
# Worker 4 - Problem Verification Specialist

You are **Worker 4** in a Hive session validating GitHub issue #{ISSUE_NUMBER}.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-4
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-4.log
- **Specialty**: Problem reproduction, bug verification, accuracy checking

## Task Loop (CRITICAL - FOLLOW EXACTLY)

You MUST run this loop continuously until session ends:

```
first_poll = true
next_sleep = 75  # Default poll interval
WHILE session is active:
  1. IF first_poll:
     - Announce: "Worker 4 starting with 5-minute initial wait (others verify first)..."
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

If Queen assigns a task with description starting with "SHUTDOWN:", exit immediately after marking it complete. (Rare for verification worker.)

### CRITICAL: Initial 5-Minute Wait

**Worker 4 waits 5 minutes before first poll.** This allows:
- Other workers to complete initial verification
- Queen to analyze and assign reproduction tasks
- Dependencies to be ready before problem verification

### Dynamic Polling Interval

Queen sets `poll_interval` in task assignments:
- `75` = Quick tasks (default)
- `180` = Medium tasks (3 min)
- `300` = Large tasks (5 min)

### IMPORTANT: Do Not Exit Early

- **DO NOT** stop polling just because you completed a task
- **DO NOT** exit if tasks.json has no tasks for you yet
- **DO NOT** terminate until you see "session_status": "complete" in tasks.json
- Queen assigns tasks SEQUENTIALLY - your task may come LAST

## Begin

Announce: "Worker 4 ready for issue #{ISSUE_NUMBER} validation. Starting with 5-minute initial wait..."
```

### Step 8: Generate mprocs.yaml (CRITICAL - FOLLOW EXACTLY)

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

  worker-1-technical:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are WORKER 1. Read .hive/sessions/{SESSION_ID}/worker-1-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "worker"
      HIVE_WORKER_ID: "1"
      HIVE_SPECIALTY: "technical-validation"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      HIVE_SESSION_ID: "{SESSION_ID}"

  worker-2-files:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER 2. Read .hive/sessions/{SESSION_ID}/worker-2-prompt.md'"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "worker"
      HIVE_WORKER_ID: "2"
      HIVE_SPECIALTY: "file-verification"
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

  worker-4-accuracy:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER 4. Read .hive/sessions/{SESSION_ID}/worker-4-prompt.md'"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "worker"
      HIVE_WORKER_ID: "4"
      HIVE_SPECIALTY: "accuracy-checking"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      HIVE_SESSION_ID: "{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 10 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

**SUBSTITUTION RULES:**
- Replace `{SESSION_ID}` with the actual session ID (e.g., `20260114-123456-validate-issue-42`)
- Replace `{PROJECT_ROOT}` with the current working directory path
- Do NOT modify any other part of the YAML
- Keep all single quotes exactly as shown
- Keep all escaped single quotes (`''`) exactly as shown

### Step 9: Create Empty Log Files

```bash
cd "{PROJECT_ROOT}" && type nul > ".hive/sessions/{SESSION_ID}/queen.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-1.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-2.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-3.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-4.log"
```

### Step 10: Launch mprocs

Launch mprocs in a new PowerShell window from the PROJECT_ROOT:

```bash
powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd \"{PROJECT_ROOT}\"; mprocs --config .hive/mprocs.yaml'"
```

**Note**: If PROJECT_ROOT contains spaces, ensure it's properly quoted in the command.

### Step 11: Output Status

```markdown
## Hive Issue Validator Launched!

**Session**: {SESSION_ID}
**Task**: Validate GitHub Issue #{ISSUE_NUMBER}
**Title**: {ISSUE_TITLE}
**Working Directory**: {PROJECT_ROOT}

### Team

| Pane | Provider | Validation Role |
|------|----------|-----------------|
| queen | Opus 4.5 | Orchestrator - Coordinates validation |
| worker-1 | Opus 4.5 | Technical validation - code accuracy |
| worker-2 | Gemini 3 Pro | File verification - paths & existence |
| worker-3 | Codex GPT-5.2 | Code simplification - cleanup & readability |
| worker-4 | Codex GPT-5.2 | Problem verification - reproducibility |

### Validation Flow

1. Queen analyzes the issue
2. Queen delegates verification tasks
3. Workers verify claims and report findings
4. Queen synthesizes validation report
5. Final verdict in validation-report.md

### Expected Output

The validation report will contain:
- **VALID**: Issue is ready to work on
- **NEEDS_REFINEMENT**: Issue needs corrections before work
- **INVALID**: Issue should be closed

The Queen will orchestrate the validation. Watch the hive work!
```
