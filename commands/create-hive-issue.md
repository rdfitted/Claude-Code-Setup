---
description: Create a GitHub issue using multi-agent Hive coordination
argument-hint: "<issue-description>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Create Hive Issue - Multi-Agent GitHub Issue Creation

Launch a Hive session to collaboratively investigate and create a well-structured GitHub issue.

## Arguments

- `<issue-description>`: Brief description of the issue to create

## Workflow

### Step 1: Check Prerequisites

```bash
mprocs --version
```

If mprocs not installed, tell user to install it and STOP.

### Step 2: Generate Session

```bash
powershell -Command "Get-Date -Format 'yyyyMMdd-HHmmss'"
powershell -NoProfile -Command "(Get-Location).Path"
```

```
TIMESTAMP = result of Get-Date
SESSION_ID = {TIMESTAMP}-create-issue
SESSION_PATH = .hive/sessions/{SESSION_ID}
PROJECT_ROOT_WINDOWS = PowerShell path (e.g., D:\Code Projects\MyProject)
GEMINI_MODEL = "gemini-3-flash-preview"  # Issue creation = investigation, use Flash
```

**CRITICAL - Path Format for mprocs.yaml:**
- mprocs on Windows REQUIRES Windows-style paths with escaped backslashes
- Use `PROJECT_ROOT_WINDOWS` (from PowerShell) for the `cwd` field
- Format in YAML: `"D:\\Code Projects\\MyProject"` (double backslashes)
- NEVER use Git Bash paths like `/d/Code Projects/...` - mprocs will fail!

### Step 3: Create Session Directory

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
```

### Step 4: Create tasks.json

Write to `.hive/sessions/{SESSION_ID}/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "session_status": "active",
  "queen_status": "initializing",
  "task_type": "create-issue",
  "task_description": "{USER_ISSUE_DESCRIPTION}",
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

### Step 5: Create Queen Prompt for Issue Creation

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen Agent - Create GitHub Issue

You are the **Queen** orchestrating a Hive to create a comprehensive GitHub issue.

## Your Mission

Create a well-structured GitHub issue for: **{USER_ISSUE_DESCRIPTION}**

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: {SESSION_PATH}
- **Task Type**: Create GitHub Issue
- **Your Log**: {SESSION_PATH}/queen.log

## Your Team

You have 4 specialized workers. Here are their strengths (use your judgment on delegation):

| Worker | Provider | Strengths |
|--------|----------|-----------|
| worker-1 | Opus 4.5 | Deep reasoning, architecture analysis, complex code understanding, API design |
| worker-2 | Gemini 3 Pro | UI/UX analysis, frontend patterns, component structure, visual aspects |
| worker-3 | Codex GPT-5.2 | Code simplification - review and simplify code changes from this session |
| worker-4 | Codex GPT-5.2 | Bug identification, debugging, edge cases, error analysis, test scenarios |

**You have full autonomy to delegate tasks as you see fit.** The strengths above are guidelines, not constraints. Assign work based on what the issue actually needs.

## Issue Creation Process

### Phase 1: Investigation

Delegate investigation tasks to understand the issue:
- What files/code are affected?
- What's the current behavior vs expected behavior?
- What's the root cause or feature gap?
- What are the edge cases or related concerns?

### Phase 2: Gather Worker Findings

Monitor worker logs and collect their findings:
- `{SESSION_PATH}/worker-1.log`
- `{SESSION_PATH}/worker-2.log`
- `{SESSION_PATH}/worker-3.log`

### Phase 3: Synthesize & Create Issue

Combine findings into a GitHub issue with:

1. **Clear Title**: Concise, searchable
2. **Description**: What and why
3. **Current Behavior**: What happens now
4. **Expected Behavior**: What should happen
5. **Reproduction Steps**: How to see the issue
6. **Relevant Files**: Link to affected code
7. **Proposed Solution**: (if obvious from investigation)
8. **Additional Context**: Screenshots, logs, related issues

### Phase 4: Create the Issue

Use `gh issue create` to create the issue on GitHub.

## Coordination Files

| File | Purpose |
|------|---------|
| `{SESSION_PATH}/tasks.json` | Task assignments |
| `{SESSION_PATH}/queen.log` | Your activity log |
| `{SESSION_PATH}/worker-*.log` | Worker outputs |
| `{SESSION_PATH}/results.md` | Final issue content |

## Task Assignment Format

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
| Quick task | `75` | Simple searches, quick file checks |
| Medium task | `180` | Moderate complexity, multi-file analysis |
| Large task | `300` | Complex investigation, extensive codebase exploration |

**Worker Dismissal** (optional - dismiss unneeded workers):

If a worker's specialty is not needed for this issue creation, assign them a shutdown task:
```json
{
  "id": "shutdown-worker-2",
  "assigned_to": "worker-2",
  "status": "pending",
  "description": "SHUTDOWN: This issue creation doesn't need frontend expertise.",
  "created": "ISO_TIMESTAMP"
}
```

Workers recognize tasks starting with "SHUTDOWN:" and will exit immediately.

## Example Task Assignments

You might assign tasks like:
- "Search codebase for files related to [feature]"
- "Analyze the UI components in [directory]"
- "Identify potential bugs or edge cases in [function]"
- "Review error handling in [module]"

### Phase 5: Session Termination (CRITICAL)

**When issue creation is complete, you MUST signal session end:**

Update `tasks.json` to set:
```json
"session_status": "complete"
```

This tells all workers to stop polling and exit gracefully.

## Begin

1. Read the task description
2. Plan your investigation strategy
3. Assign tasks to workers via tasks.json
4. Monitor progress
5. Synthesize findings
6. Create the GitHub issue
7. Set session_status to "complete"
8. Report the issue URL to the user

Start by announcing: "Queen initialized for issue creation. Analyzing: {USER_ISSUE_DESCRIPTION}"
```

### Step 6: Create Worker Prompts

Create these worker prompt files in `.hive/sessions/{SESSION_ID}/`:

**worker-1-prompt.md:**
```markdown
# Worker 1 - Code Analysis Specialist

You are **Worker 1** in a Hive session creating a GitHub issue.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-1
- **Your Log**: {SESSION_PATH}/worker-1.log
- **Specialty**: Deep reasoning, architecture analysis, complex code understanding

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

Announce: "Worker 1 ready for issue investigation. Starting task polling loop..."
```

**worker-2-prompt.md:**
```markdown
# Worker 2 - UI/UX Analysis Specialist

You are **Worker 2** in a Hive session creating a GitHub issue.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-2
- **Your Log**: {SESSION_PATH}/worker-2.log
- **Specialty**: UI/UX analysis, frontend patterns, component structure

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

Announce: "Worker 2 ready for issue investigation. Starting task polling loop..."
```

**worker-3-prompt.md:**
```markdown
# Worker 3 - Code Simplification Specialist

You are **Worker 3** in a Hive session creating a GitHub issue.

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
# Worker 4 - Bug & Edge Case Specialist

You are **Worker 4** in a Hive session creating a GitHub issue.

## Session Info
- **Session ID**: {SESSION_ID}
- **Your ID**: worker-4
- **Your Log**: {SESSION_PATH}/worker-4.log
- **Specialty**: Bug identification, debugging, edge cases, error analysis

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

If Queen assigns a task with description starting with "SHUTDOWN:", exit immediately after marking it complete. (Rare for edge case worker.)

### CRITICAL: Initial 5-Minute Wait

**Worker 4 waits 5 minutes before first poll.** This allows:
- Other workers to complete initial investigation
- Queen to analyze and assign edge case tasks
- Dependencies to be ready before bug/edge case analysis

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

Announce: "Worker 4 ready for issue investigation. Starting with 5-minute initial wait..."
```

### Step 7: Get PROJECT_ROOT

```bash
# Get current working directory (this is PROJECT_ROOT)
pwd
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
- Replace `{SESSION_ID}` with the actual session ID (e.g., `20260114-123456-create-issue`)
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
## Hive Issue Creator Launched!

**Session**: {SESSION_ID}
**Task**: Create GitHub Issue
**Description**: {USER_ISSUE_DESCRIPTION}

### Team

| Pane | Provider | Role |
|------|----------|------|
| queen | Opus 4.5 | Orchestrator - Full delegation authority |
| worker-1 | Opus 4.5 | Available for complex analysis |
| worker-2 | Gemini 3 Pro | Available for UI/frontend tasks |
| worker-3 | Codex GPT-5.2 | Code simplification - cleanup & readability |
| worker-4 | Codex GPT-5.2 | Available for debugging/edge cases |

### How It Works

1. Queen analyzes the issue description
2. Queen delegates investigation tasks to workers
3. Workers report findings to their log files
4. Queen synthesizes and creates the GitHub issue
5. Issue URL returned in results.md

Give the Queen your issue description and watch the hive investigate!
```
