---
description: Launch visible multi-agent system using mprocs with queen + workers coordination
argument-hint: "{session-name}" [worker-count]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob]
---

# Hive - Multi-Agent Orchestration

Launch multiple Claude Code agents in visible terminal panes using mprocs.

## Arguments

- `{session-name}`: Name for this session (required, kebab-case)
- `[worker-count]`: Number of workers (optional, default: 4, max: 5)

## Workflow

### Step 1: Check mprocs Installation

```bash
mprocs --version
```

If command fails, output:
```
mprocs is not installed. Install it first:

Windows (Scoop): scoop install mprocs
npm (any OS):    npm install -g mprocs
Cargo:           cargo install mprocs

Then run /hive again.
```
STOP if mprocs not installed.

### Step 2: Parse Arguments

Extract:
- `SESSION_NAME`: First argument (convert spaces to hyphens, lowercase)
- `WORKER_COUNT`: Second argument or default to 3 (clamp 1-4)

### Step 3: Classify Task & Select Gemini Model

**Before launching, analyze the user's request to determine the Gemini model:**

| Task Type | Keywords/Indicators | Model |
|-----------|---------------------|-------|
| **Research/Investigation** | search, find, explore, investigate, analyze, understand, review, audit, scan | `gemini-3-flash-preview` |
| **Code Generation** | implement, build, create, write, fix, refactor, add feature, update, modify | `gemini-3-pro-preview` |

**Set the variable:**
```
GEMINI_MODEL = "gemini-3-flash-preview"  # Default for research
            OR "gemini-3-pro-preview"    # If code generation needed
```

**Decision logic:**
- If the session name or user context suggests **exploration, search, or analysis** → Flash (faster, cheaper)
- If the session name or user context suggests **implementation or code changes** → Pro (better reasoning)
- When in doubt, ask the user: "Should Gemini focus on research (flash) or code generation (pro)?"

### Step 0: Lightweight Codebase Pre-Scan (Before mprocs)

**Purpose**: Use 4 lightweight OpenCode agents via Bash to scan the codebase and identify relevant files BEFORE launching the full hive.

**Why This Matters**:
- Token-efficient: Fast, cheap OpenCode models for initial reconnaissance
- Context: Queen and workers get a pre-populated file list
- Model diversity: 4 different perspectives on the codebase (enables tie-breaker logic)
- No mprocs overhead: Simple bash calls that complete before orchestration begins

#### Step 0a: Spawn 4 Pre-Scan Agents in Parallel

Use the Task tool to spawn 4 agents simultaneously. Each agent uses Bash to call OpenCode CLI:

**Agent 1 - Architecture Scanner (OpenCode BigPickle):**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle "Scan this codebase for: {TASK_DESCRIPTION}. Identify: 1) Main architecture patterns, 2) Key modules and their relationships, 3) Critical files for this task. Return file paths with brief descriptions."
```

**Agent 2 - Code Organization Scanner (OpenCode GLM 4.7):**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Analyze this codebase for: {TASK_DESCRIPTION}. Focus on: 1) Code organization patterns, 2) High coupling files, 3) Configuration and environment files. Return file paths with observations."
```

**Agent 3 - Entry Points Scanner (OpenCode Grok Code):**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "Scout this codebase for: {TASK_DESCRIPTION}. Identify: 1) Entry points and main flows, 2) Test files, 3) Package definitions. Return file paths with notes."
```

**Timeout**: 3 minutes per agent (180000ms)

#### Step 0b: Collect Pre-Scan Results

After all 4 agents complete:
1. Deduplicate file paths
2. Merge overlapping findings
3. Rank by consensus (files found by multiple agents = higher priority)
4. **If 2-2 tie on file relevance**: Claude (orchestrator) reviews evidence and decides
5. Store results in `.hive/sessions/{SESSION_ID}/prescan-results.md`

**Pre-Scan Results File Format:**
```markdown
# Pre-Scan Results for: {SESSION_NAME}

## Task Context
{TASK_DESCRIPTION}

## Key Files Identified

### Entry Points & Core Logic
- {file_path} - {description} (found by: {agent_list})
- {file_path} - {description}

### Configuration Files
- {file_path} - {description}

### Architecture & Patterns
- {file_path} - {description}

### Test Files
- {file_path} - {description}

## Consensus
- **4/4 agree**: High confidence files
- **3/4 agree**: Medium confidence files
- **2-2 tie**: Claude tie-breaker applied

---
Scanned by: 3 OpenCode agents (BigPickle, GLM 4.7, Grok Code)
Duration: ~{elapsed_time}
```

#### Step 0c: Pass Results to Queen

The Queen prompt (Step 6) references `.hive/sessions/{SESSION_ID}/prescan-results.md`. Ensure the file is created before launching mprocs.

#### Step 0d: Learning Scout Agent (GLM 4.7) - BEFORE WORKERS

**Purpose**: Extract relevant learnings from past sessions and project DNA to guide this session's workers.

**Why This Matters**:
- Compound engineering: Build on past learnings, don't repeat mistakes
- Project consistency: Apply established patterns and conventions
- Context injection: Every worker gets relevant historical insights

**Spawn Learning Scout (Task agent):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a Learning Scout using OpenCode GLM 4.7.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free \"You are a Learning Scout. Your job is to extract relevant learnings for this task.

TASK: {TASK_DESCRIPTION}

1. Read .ai-docs/learnings.jsonl (if exists) - extract entries with keywords matching this task
2. Read .ai-docs/project-dna.md (if exists) - extract relevant principles and patterns
3. Read .ai-docs/bug-patterns.md (if exists) - extract bug fix patterns that might apply
4. Read CLAUDE.md (if exists) - extract coding standards and project instructions

OUTPUT FORMAT (write to stdout):
---SESSION-GUIDELINES-START---
## Relevant Past Learnings
- [learning 1 from similar past tasks]
- [learning 2]

## Project DNA Principles
- [principle 1 relevant to this task]
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

#### Step 0e: Codify Session Guidelines

After Learning Scout completes:
1. Extract the output between `---SESSION-GUIDELINES-START---` and `---SESSION-GUIDELINES-END---`
2. Write to `.hive/sessions/{SESSION_ID}/session-guidelines.md`:

```markdown
# Session Guidelines for: {SESSION_NAME}

## Task
{TASK_DESCRIPTION}

{LEARNING_SCOUT_OUTPUT}

## Codified Guidelines (Queen's Directives)

Based on the above learnings and project DNA, ALL workers in this session MUST:

1. {GUIDELINE_1}
2. {GUIDELINE_2}
3. {GUIDELINE_3}

---
Generated by: Learning Scout (GLM 4.7) + Main Claude
```

**IMPORTANT**: Main Claude reviews the Learning Scout output and adds/refines guidelines based on:
- The specific task requirements
- Any obvious gaps in the suggested guidelines
- Project-specific patterns noticed during pre-scan

### Step 4: Generate Session Variables

**Run as a single block:**
```bash
TIMESTAMP=$(powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'")
PROJECT_ROOT_WINDOWS=$(powershell -NoProfile -Command "(Get-Location).Path")
MPROCS_PORT=$((4000 + ${TIMESTAMP: -4}))
SESSION_ID="${TIMESTAMP}-${SESSION_NAME}"
```

**Variables:**
```
TIMESTAMP = e.g., 20260120-143052
SESSION_ID = {TIMESTAMP}-{SESSION_NAME}
PROJECT_ROOT_WINDOWS = Windows-style path from PowerShell (e.g., D:\Code Projects\MyProject)
MPROCS_PORT = 4000 + last 4 digits (e.g., 143052 → 3052 → port 7052)
```

**Port range:** 4000-9959 (unique per session, no conflicts)

**CRITICAL - Path Format for mprocs.yaml:**
- mprocs on Windows REQUIRES Windows-style paths with escaped backslashes
- Use `PROJECT_ROOT_WINDOWS` (from PowerShell) for the `cwd` field
- Format in YAML: `"D:\\Code Projects\\MyProject"` (double backslashes)
- NEVER use Git Bash paths like `/d/Code Projects/...` - mprocs will fail!

### Step 5: Create Session Directory

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
```

### Step 6: Generate tasks.json

Write to `.hive/sessions/{SESSION_ID}/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "session_status": "active",
  "queen_status": "initializing",
  "task_description": "",
  "workers": {WORKER_COUNT},
  "tasks": [],
  "synthesis": {
    "status": "pending",
    "result_file": "results.md"
  }
}
```

**Note**: `session_status` starts as "active". Queen sets it to "complete" when all work is done to signal workers to exit.

### Step 7: Generate Queen Prompt (Spawn-on-Demand)

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen Agent - Spawn-on-Demand Hive

You are the **Queen** orchestrating a spawn-on-demand hive.

**Task files have already been written by Main Claude.** Your job is to spawn workers at the right time and monitor their progress.

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/queen.log
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}

## Your Team

| Worker | Model | CLI | Specialty |
|--------|-------|-----|-----------|
| worker-1 | Opus 4.5 | **Cursor CLI** | Backend, architecture, APIs |
| worker-2 | Gemini 3 Pro | Gemini | UI, frontend, styling |
| worker-3 | Grok Code | OpenCode | Backend/frontend coherence |
| worker-4 | Codex GPT-5.2 | Codex | Code simplification |
| reviewer-bigpickle | BigPickle | OpenCode | Edge cases, deep analysis |
| reviewer-grok | Grok Code | OpenCode | Quick observations |
| resolver | Opus 4.5 | **Cursor CLI** | Fix reviewer findings |
| tester-1 | Codex GPT-5.2 | Codex | Testing, bug fixing |
| code-quality | Opus 4.5 | **Cursor CLI** | PR comment resolution |

## Spawn Commands

**IMPORTANT**: Use forward slashes in paths. Escape inner quotes with backslash.

### Worker 1 - Backend/Architecture (Cursor CLI - Opus 4.5)

**Step 1: Write spawn .bat file**
```powershell
Set-Content -Path ".hive/sessions/{SESSION_ID}/spawn-worker1.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.hive/sessions/{SESSION_ID}/worker-1-task.md and execute.\\\"\", \"name\": \"worker-1\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

**Step 2: Execute**
```bash
.hive/sessions/{SESSION_ID}/spawn-worker1.bat
```

### Worker 2 - UI/Frontend (Gemini)

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "gemini -m gemini-3-pro-preview -y -i \"Read .hive/sessions/{SESSION_ID}/worker-2-task.md and execute.\"", "name": "worker-2"}'
```

**Gemini Fallback**: If Gemini fails with quota/rate limit error, retry with flash model:
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "gemini -m gemini-3-flash-preview -y -i \"Read .hive/sessions/{SESSION_ID}/worker-2-task.md and execute.\"", "name": "worker-2"}'
```

### Worker 3 - Coherence (OpenCode Grok Code)

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read .hive/sessions/{SESSION_ID}/worker-3-task.md and execute.\"", "name": "worker-3", "env": {"OPENCODE_YOLO": "true"}}'
```

### Worker 4 - Code Simplification (Codex GPT-5.2)

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .hive/sessions/{SESSION_ID}/worker-4-task.md and execute.\"", "name": "worker-4"}'
```

### Reviewer - BigPickle (OpenCode)

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read .hive/sessions/{SESSION_ID}/reviewer-bigpickle-task.md and execute.\"", "name": "reviewer-bigpickle", "env": {"OPENCODE_YOLO": "true"}}'
```

### Reviewer - Grok (OpenCode)

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read .hive/sessions/{SESSION_ID}/reviewer-grok-task.md and execute.\"", "name": "reviewer-grok", "env": {"OPENCODE_YOLO": "true"}}'
```

### Resolver (Cursor CLI - Opus 4.5)

**Step 1: Write spawn .bat file**
```powershell
Set-Content -Path ".hive/sessions/{SESSION_ID}/spawn-resolver.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.hive/sessions/{SESSION_ID}/resolver-task.md and execute.\\\"\", \"name\": \"resolver\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

**Step 2: Execute**
```bash
.hive/sessions/{SESSION_ID}/spawn-resolver.bat
```

### Tester (Codex GPT-5.2)

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .hive/sessions/{SESSION_ID}/tester-task.md and execute.\"", "name": "tester-1"}'
```

## Process Management

```bash
# Remove a process
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "remove-proc", "proc": "worker-name"}'

# Restart a process
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "restart-proc", "proc": "worker-name"}'
```

## CLI-Specific Formats

| CLI | Format | Spawn Method |
|-----|--------|--------------|
| Cursor CLI | `--force "PROMPT"` | .bat file (required) |
| Gemini | `-m MODEL -y -i "PROMPT"` | Direct or .bat |
| OpenCode | `-m MODEL --prompt "PROMPT"` + `OPENCODE_YOLO=true` | Direct or .bat |
| Codex | `--dangerously-bypass-approvals-and-sandbox -m gpt-5.2 "PROMPT"` | Direct or .bat |

**Cursor CLI .bat pattern:**
```batch
@echo off
mprocs --server 127.0.0.1:{PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"PROMPT\\\"\", \"name\": \"agent-name\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

## Log Protocol

**APPEND-ONLY**: Use PowerShell explicitly for all commands.

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Message\""
```

**Check for COMPLETED in worker logs:**
```powershell
powershell -NoProfile -Command "Select-String -Path '.hive/sessions/{SESSION_ID}/worker-1.log' -Pattern 'COMPLETED'"
```

## Pre-Scan Results

Before this session started, agents scanned the codebase. Their findings are in:
`.hive/sessions/{SESSION_ID}/prescan-results.md`

## Session Guidelines (CRITICAL - READ FIRST!)

A Learning Scout has extracted relevant learnings and project DNA for this task:
`.hive/sessions/{SESSION_ID}/session-guidelines.md`

**BEFORE spawning ANY workers, you MUST:**
1. Read the session-guidelines.md file completely
2. Internalize the guidelines - they apply to ALL workers
3. These guidelines are already embedded in each worker's task file

## Orchestration Workflow

### Phase 0: Verify Session Guidelines

**FIRST THING**: Read and log that you've reviewed the session guidelines:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Reviewed session-guidelines.md - {number} guidelines codified\""
```

### Phase 1: Spawn Workers (Implementation)

**Parallel work (backend + frontend):**
1. Spawn worker-1 and worker-2 in parallel
2. Monitor logs for COMPLETED

**Sequential work (coherence after implementation):**
3. When worker-1 and worker-2 show COMPLETED, spawn worker-3
4. Monitor worker-3 log for COMPLETED

**Simplification (after coherence):**
5. When worker-3 shows COMPLETED, spawn worker-4
6. Monitor worker-4 log for COMPLETED

### Phase 2: Spawn Reviewers

When implementation is complete:
1. Spawn reviewer-bigpickle and reviewer-grok
2. Monitor review files for COMPLETED
3. Read their findings

### Phase 3: Spawn Resolver

After reviewers complete:
1. Spawn resolver (reads reviewer findings and fixes all issues)
2. Monitor resolver.log for COMPLETED
3. Resolver addresses ALL findings before testing

### Phase 4: Spawn Tester

After resolver completes:
1. Spawn tester-1 (verifies resolver's fixes)
2. Monitor tester-1.log for COMPLETED
3. If tester finds issues, may need to respawn resolver

### Phase 6: Curate Learnings (QUEEN REVIEWS LOGS FIRST!)

**BEFORE running curate-learnings, YOU (Queen) must:**

1. **Read ALL worker logs completely:**
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/worker-1.log"
Get-Content ".hive/sessions/{SESSION_ID}/worker-2.log"
Get-Content ".hive/sessions/{SESSION_ID}/worker-3.log"
Get-Content ".hive/sessions/{SESSION_ID}/worker-4.log"
Get-Content ".hive/sessions/{SESSION_ID}/resolver.log"
Get-Content ".hive/sessions/{SESSION_ID}/tester-1.log"
```

2. **Read ALL reviewer findings:**
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/reviews/bigpickle.md"
Get-Content ".hive/sessions/{SESSION_ID}/reviews/grok.md"
```

3. **Synthesize key insights** - What worked? What didn't? What patterns emerged?

4. **Log your synthesis:**
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: SESSION SYNTHESIS - {key insights}\""
```

5. **Curate learnings yourself** - Append to `.ai-docs/learnings.jsonl`:

**IMPORTANT**: `.gitignore` does NOT prevent file writes! It only prevents git from tracking files. You CAN and MUST write to `.ai-docs/learnings.jsonl` even if it's in `.gitignore`. The learnings are stored locally for future Claude sessions.

```powershell
# First ensure .ai-docs directory exists
New-Item -ItemType Directory -Force -Path ".ai-docs" | Out-Null

# Then append the learning
$learning = @{
    date = (Get-Date -Format "yyyy-MM-dd")
    session = "{SESSION_ID}"
    task = "{TASK_DESCRIPTION}"
    outcome = "success"
    keywords = @("{keyword1}", "{keyword2}")
    insight = "{YOUR_SYNTHESIS}"
    files_touched = @("{file1}", "{file2}")
} | ConvertTo-Json -Compress
Add-Content -Path ".ai-docs/learnings.jsonl" -Value $learning
```

If the directory doesn't exist, the above command creates it. Do NOT skip this step because of .gitignore!

### Phase 7: Commit & Push

**YOU are the ONLY agent who commits and pushes.**

After all work is complete:
```bash
git add -A
git commit -m "feat: {descriptive message}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push
```

### Phase 8: Code Quality Loop (Automated PR Comment Resolution)

**⚠️ MANDATORY - DO NOT SKIP THIS PHASE ⚠️**

You MUST execute Phase 6 after committing and pushing. Do not ask the user if they want to proceed - just do it.

**After commit/push, external reviewers (Gemini, Codex, Code Rabbit) will comment on the PR.**

This phase automates resolving those comments iteratively until the PR is clean.

#### Phase 8.1: Wait for External Reviews (10 minutes)

**⚠️ YOU MUST ACTUALLY WAIT - DO NOT SKIP ⚠️**

External reviewers (Gemini, Codex, Code Rabbit) need time to analyze the PR. You MUST execute the sleep command and wait the full 10 minutes before checking for comments.

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Waiting 10 minutes for external reviewers...\"; Start-Sleep -Seconds 600; Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Wait complete. Checking for comments...\""
```

**DO NOT proceed to Step 2 until this command completes (10 minutes).**

#### Phase 8.2: Check for New Comments

```bash
# Get PR number from the push
PR_NUMBER=$(gh pr list --head $(git branch --show-current) --json number -q '.[0].number')

# Check for new comments
NEW_COMMENTS=$(gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments --jq 'length')
```

**If NEW_COMMENTS = 0**: Log "No new comments. PR is ready for review." and END.

#### Phase 8.3: Write and Spawn Code Quality Agent (Opus)

**Phase 8.3a: Write iteration-specific task file**

Copy the template and fill in iteration details:
```powershell
# Read template and replace {N} with current iteration number
$template = Get-Content ".hive/sessions/{SESSION_ID}/code-quality-task-template.md" -Raw
$taskContent = $template -replace '\{N\}', '{N}' -replace '\{PR_NUMBER\}', '$PR_NUMBER'
Set-Content -Path ".hive/sessions/{SESSION_ID}/code-quality-{N}-task.md" -Value $taskContent
```

**Phase 8.3b: Create empty log file**
```powershell
New-Item -Path ".hive/sessions/{SESSION_ID}/code-quality-{N}.log" -ItemType File -Force
```

**Phase 8.3c: Spawn code-quality-{N} agent via MPROCS (Cursor CLI)**

**⚠️ YOU MUST USE MPROCS - NOT TASK TOOL ⚠️**

Do NOT use the Task tool to spawn subagents yourself. You MUST spawn a visible mprocs agent:

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

#### Phase 8.4: Monitor and Loop

1. Wait for `COMPLETED` in code-quality-{N}.log
2. Wait another 10 minutes for new reviews
3. Check for new comments
4. If new comments exist, spawn code-quality-{N+1}
5. Repeat until no new comments

**Loop termination conditions:**
- No new comments after 10-minute wait
- Maximum 5 iterations (to prevent infinite loops)

#### Phase 8.5: Log Completion

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Code Quality Loop complete. {N} iterations. PR is ready for human review.\""
```

## Error Handling

**If a worker seems stuck:**
1. Read their full log for clues
2. Remove the stuck worker: `remove-proc`
3. Spawn a replacement

**If Gemini fails with quota error:**
1. Remove worker-2
2. Respawn with flash model instead of pro

## Begin

Announce: "Queen initialized. Task files are ready. Spawning workers..."
```

### Step 8: Generate Worker Task Files (Spawn-on-Demand)

**Main Claude writes task files BEFORE launching mprocs.** Workers read their task file when spawned.

For each worker, write to `.hive/sessions/{SESSION_ID}/worker-{N}-task.md`:

**Worker 1 Task (Backend/Architecture):**
```markdown
# Worker 1 Task - Backend/Architecture

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-1.log
- **Specialty**: Backend, architecture, APIs, complex logic

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

These guidelines were extracted from:
- Past session learnings (`.ai-docs/learnings.jsonl`)
- Project DNA (`.ai-docs/project-dna.md`)
- Project coding standards

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines throughout your work.**

## Your Task

{WORKER_1_TASK_DESCRIPTION}

## Pre-Scan Results

Read `.hive/sessions/{SESSION_ID}/prescan-results.md` for relevant files.

## Log Protocol

**APPEND-ONLY** - Use PowerShell:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/worker-1.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] WORKER-1: Message\""
```

**Required entries:**
- STARTED - When you begin
- PROGRESS - Milestones
- COMPLETED - When finished (Queen monitors for this)

## Instructions

1. Log STARTED
2. Execute your task
3. Log COMPLETED when done
4. **DO NOT commit or push** - Queen handles git

## Begin

Execute your task now.
```

**Worker 2 Task (UI/Frontend):**
```markdown
# Worker 2 Task - UI/Frontend

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-2.log
- **Specialty**: UI, frontend, styling, user experience

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines throughout your work.**

## Your Task

{WORKER_2_TASK_DESCRIPTION}

## Log Protocol

**APPEND-ONLY**:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/worker-2.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] WORKER-2: Message\""
```

**Required entries:** STARTED, PROGRESS, COMPLETED

## Shell Command Rules (CRITICAL)

- **NEVER use chained commands** (`&&`, `||`, `;`)
- Run each shell command separately
- Example: Instead of `type file1 && type file2`, run `type file1` then `type file2` as separate commands
- This ensures YOLO mode works correctly for autonomous execution

## Instructions

1. Log STARTED
2. Execute your task
3. Log COMPLETED when done
4. **DO NOT commit or push** - Queen handles git

## Begin

Execute your task now.
```

**Worker 3 Task (Coherence):**
```markdown
# Worker 3 Task - Backend/Frontend Coherence

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-3.log
- **Specialty**: Backend/frontend coherence, integration, data flow

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines throughout your work.**

## Your Task

{WORKER_3_TASK_DESCRIPTION}

## Context

Read worker-1 and worker-2 logs to understand what was implemented:
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/worker-1.log" -Tail 20
Get-Content ".hive/sessions/{SESSION_ID}/worker-2.log" -Tail 20
```

## Log Protocol

**APPEND-ONLY**:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/worker-3.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] WORKER-3: Message\""
```

## Instructions

1. Log STARTED
2. Check coherence between backend and frontend changes
3. Log COMPLETED when done
4. **DO NOT commit or push** - Queen handles git

## Begin

Execute your task now.
```

**Worker 4 Task (Simplification):**
```markdown
# Worker 4 Task - Code Simplification

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-4.log
- **Specialty**: Code simplification, cleanup, readability

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines - especially coding standards - during simplification.**

## Your Task

{WORKER_4_TASK_DESCRIPTION}

## Context

Read other worker logs to see what was changed:
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/worker-1.log" -Tail 15
Get-Content ".hive/sessions/{SESSION_ID}/worker-2.log" -Tail 15
Get-Content ".hive/sessions/{SESSION_ID}/worker-3.log" -Tail 15
```

## Log Protocol

**APPEND-ONLY**:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/worker-4.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] WORKER-4: Message\""
```

## Instructions

1. Log STARTED
2. Simplify code that was modified
3. Log COMPLETED when done
4. **DO NOT commit or push** - Queen handles git

## Begin

Execute your task now.
```

**Reviewer BigPickle Task:**
```markdown
# Reviewer Task - BigPickle

## Session
- **Session ID**: {SESSION_ID}
- **Your Review File**: .hive/sessions/{SESSION_ID}/reviews/bigpickle.md
- **Specialty**: Edge cases, deep analysis

## Session Guidelines (Review Against These!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**Review code changes against these guidelines. Flag violations as findings.**

## Your Task

Review the code changes made by workers. Focus on edge cases and potential issues.

## Context

Read worker logs to see what was changed.

## Log Protocol

Write reviews to your file:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/reviews/bigpickle.md' -Value \"[$(Get-Date -Format 'HH:mm:ss')] REVIEW: Message\""
```

## Instructions

1. Read worker logs and changed files
2. Write your review observations
3. Mark COMPLETED when done

## Begin

Execute your review now.
```

**Reviewer Grok Task:**
```markdown
# Reviewer Task - Grok

## Session
- **Session ID**: {SESSION_ID}
- **Your Review File**: .hive/sessions/{SESSION_ID}/reviews/grok.md
- **Specialty**: Quick observations, fast feedback

## Session Guidelines (Review Against These!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**Quick-check code changes against these guidelines.**

## Your Task

Quick review of code changes. Note any obvious issues.

## Log Protocol

Write to your file:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/reviews/grok.md' -Value \"[$(Get-Date -Format 'HH:mm:ss')] REVIEW: Message\""
```

## Instructions

1. Read worker logs and code changes
2. Write quick observations
3. Mark COMPLETED when done

## Begin

Execute your review now.
```

**Resolver Task:**
```markdown
# Resolver Task - Address All Reviewer Findings

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/resolver.log
- **Specialty**: Fix all issues found by reviewers

## Session Guidelines (Resolve According to These!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**All fixes must adhere to these guidelines.**

## Your Task

Address ALL findings from both reviewers before testing.

## Context

**Read reviewer findings:**
- `.hive/sessions/{SESSION_ID}/reviews/bigpickle.md`
- `.hive/sessions/{SESSION_ID}/reviews/grok.md`

**Read worker logs** to understand context of changes.

## Log Protocol

**APPEND-ONLY**:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive\sessions\{SESSION_ID}\resolver.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] RESOLVER: Message\""
```

## Instructions

1. Log STARTED
2. Read ALL reviewer findings from both BigPickle and Grok
3. For EACH finding:
   - Log which finding you're addressing
   - Make the fix
   - Log the fix completed
4. Log COMPLETED when ALL findings are addressed
5. **DO NOT commit or push** - Queen handles git

Execute your resolution now.
```

**Tester Task:**
```markdown
# Tester Task

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/tester-1.log
- **Specialty**: Testing, bug fixing, quality assurance

## Session Guidelines (Test Against These!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**Ensure tests validate adherence to these guidelines.**

## Your Task

Test the changes made by workers. Read reviewer findings first.

## Context

**Read reviewer findings:**
- `.hive/sessions/{SESSION_ID}/reviews/bigpickle.md`
- `.hive/sessions/{SESSION_ID}/reviews/grok.md`

**Read worker logs** to understand what was changed.

## Log Protocol

**APPEND-ONLY**:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/tester-1.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] TESTER-1: Message\""
```

## Instructions

1. Log STARTED
2. Read reviewer findings
3. Run tests and fix issues
4. Log COMPLETED when done
5. **DO NOT commit or push** - Queen handles git

## Begin

Execute your task now.
```

**Code Quality Task Template (for Phase 6):**

Write to `.hive/sessions/{SESSION_ID}/code-quality-task-template.md`:

```markdown
# Code Quality Task - Iteration {N}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/code-quality-{N}.log
- **PR Number**: {PR_NUMBER}
- **Iteration**: {N}

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**Apply these guidelines when fixing code review comments.**

## Your Task

Resolve ALL new PR comments from external reviewers (Gemini, Codex, Code Rabbit).

**⚠️ YOU MUST USE /resolveprcomments - DO NOT RESOLVE COMMENTS MANUALLY ⚠️**

The `/resolveprcomments` command provides:
- Multi-agent verification (4 OpenCode agents per comment)
- VALID vs MISTAKEN categorization with consensus logic
- Context scouts for learnings and code standards
- Code simplification via Codex GPT-5.2
- Automatic learning capture

### Execute This Command

```
/resolveprcomments
```

This will:
1. Fetch all new PR comments since last commit
2. Spawn 3 verification agents per comment (BigPickle, GLM 4.7, Grok Code)
3. Categorize each as VALID (needs fix) or MISTAKEN (already implemented)
4. Post replies to MISTAKEN comments with agent evidence
5. Spawn context scouts for each VALID comment (learnings + standards)
6. Implement fixes for VALID comments following project standards
7. Run Codex simplification on modified files
8. Capture learnings to .ai-docs/learnings.jsonl
9. Commit and push

## Structured Logging Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/code-quality-{N}.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] CODE-QUALITY-{N}: message'"
```

**Required log entries:**
- `STARTED`
- `RUNNING: /resolveprcomments`
- `COMMENTS_FOUND: {count}`
- `VALID: {count} | MISTAKEN: {count}`
- `COMMITTED: {commit_hash}`
- `COMPLETED`

## Instructions

1. Log STARTED
2. Log RUNNING: /resolveprcomments
3. Execute `/resolveprcomments` and let it handle everything
4. Log the results (COMMENTS_FOUND, VALID/MISTAKEN counts)
5. Log COMMITTED with the hash from the command output
6. Log COMPLETED

**DO NOT manually fetch or fix comments - use /resolveprcomments.**

## Begin
Log STARTED, then run /resolveprcomments now.
```

### Step 9: Generate mprocs.yaml (Spawn-on-Demand)

**CRITICAL PATH FORMAT**: The `cwd` field MUST use Windows-style paths with escaped backslashes.
- Correct: `cwd: "D:\\Code Projects\\MyProject"`
- WRONG: `cwd: "/d/Code Projects/MyProject"` (Git Bash style - will fail!)

**Spawn-on-Demand Architecture**: Only Queen spawns at startup. Queen spawns workers dynamically using mprocs TCP server.

Write to `.hive/mprocs.yaml`:

```yaml
# Spawn-on-Demand Hive - Only Queen starts, workers spawned as needed
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

**Workers are spawned on-demand by Queen** using mprocs TCP commands (see Queen prompt for spawn commands).

### Step 10: Create Empty Log Files and Session Guidelines

```bash
cd "{PROJECT_ROOT}" && type nul > ".hive/sessions/{SESSION_ID}/queen.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-1.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-2.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-3.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-4.log" && type nul > ".hive/sessions/{SESSION_ID}/resolver.log" && type nul > ".hive/sessions/{SESSION_ID}/tester-1.log"
```

Add/remove worker log files based on WORKER_COUNT.

**Create session-guidelines.md** (populated by Step 0e):
```bash
# This file should already exist from Step 0e, but ensure it exists
type nul > ".hive/sessions/{SESSION_ID}/session-guidelines.md" 2>nul
```

**Also create reviews directory and reviewer files:**

```bash
mkdir -p ".hive/sessions/{SESSION_ID}/reviews"
touch ".hive/sessions/{SESSION_ID}/reviews/bigpickle.md"
touch ".hive/sessions/{SESSION_ID}/reviews/grok.md"
```

### Step 11: Launch mprocs in New Terminal

**MANDATORY**: Execute this command. Uses `-WorkingDirectory` with Windows path:

```bash
powershell -Command "Start-Process powershell -WorkingDirectory '{PROJECT_ROOT_WINDOWS}' -ArgumentList '-NoExit', '-Command', 'mprocs --config .hive/mprocs.yaml'"
```

This opens a new PowerShell window with mprocs running in the project directory.

### Step 12: Output Status

```markdown
## Hive Launched!

**Session ID**: {SESSION_ID}
**Workers**: {WORKER_COUNT}
**Path**: .hive/sessions/{SESSION_ID}/

### Team

| Pane | Model | CLI | Specialty |
|------|-------|-----|-----------|
| queen | Opus 4.5 | Claude Code | Orchestrator |
| worker-1 | Opus 4.5 | **Cursor CLI** | Backend & Architecture |
| worker-2 | Gemini 3 Pro | Gemini | UI & Frontend |
| worker-3 | Grok Code | OpenCode | Backend/Frontend Coherence |
| worker-4 | GPT-5.2 | Codex | Code Simplification |
| resolver | Opus 4.5 | **Cursor CLI** | Fix review findings |
| code-quality | Opus 4.5 | **Cursor CLI** | PR comment resolution |

### Code Reviewers (Non-Blocking)

| Pane | Provider | Role |
|------|----------|------|
| reviewer-bigpickle | OpenCode BigPickle | Independent Review |
| reviewer-grok | OpenCode Grok Code | Independent Review |

*Reviewers observe and write to `.hive/sessions/{SESSION_ID}/reviews/` - Queen MONITORS their output periodically.*

### Tester (Runs After Reviewers)

| Pane | Provider | Role |
|------|----------|------|
| tester-1 | Codex GPT-5.2 | Bug Fixing & Testing (incorporates reviewer findings) |

*Tester waits 5 minutes for reviewers to analyze code, then reads their findings and addresses issues.*

### mprocs opened in new window

Give Queen a task and watch the team work!

### Keyboard Shortcuts (in mprocs)

- `j/k`: Navigate panes
- `Enter`: Focus pane
- `q`: Quit
- `x`: Kill process
- `r`: Restart

### Session Files

- `session-guidelines.md` - Learnings + Project DNA guidelines for this session
- `prescan-results.md` - Pre-scan file identification
- `tasks.json` - Task queue
- `queen.log` / `worker-*.log` / `resolver.log` / `tester-1.log` - Agent logs
- `results.md` - Final output
- `reviews/` - Code reviewer outputs (bigpickle.md, grok.md)
```

## Example Usage

```bash
/hive "search-codebase"      # 4 workers + tester (default)
/hive "refactor-api" 4       # Full team: 4 workers + reviewers + tester
/hive "quick-task" 2         # 2 workers (backend + frontend only)
```
