---
description: Resolve a GitHub issue using multi-agent Hive coordination
argument-hint: "<issue-number-or-url>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task, TodoWrite]
---

# Resolve Hive Issue - Spawn-on-Demand GitHub Issue Resolution

Launch a spawn-on-demand hive with sequential workers, reviewers, resolver, and tester to resolve a GitHub issue.

## Thread Type: B-Thread (Big/Meta) + L-Thread (Long Duration)

- **Spawn-on-demand**: Only Queen starts, workers spawned as needed
- **Sequential workers**: Each reads previous logs, builds on their work
- **Structured logging**: Decisions, rationale, approach passed downstream
- **Review + Resolve**: Reviewers find issues, Resolver addresses them
- **Clean exit**: PR with difficulties documented (no infinite loops)

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  MAIN CLAUDE (runs /resolve-hive-issue)                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ 1. Fetch issue details                                         │  │
│  │ 2. Validate concerns (4 OpenCode agents per concern)           │  │
│  │ 3. Write task files for workers                                │  │
│  │ 4. Launch mprocs (Queen only)                                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    QUEEN (Opus 4.5) - Orchestrator                  │
│                                                                     │
│   Phase 1: Sequential Workers (each reads previous logs)            │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐        │
│   │Worker-1 │ → │Worker-2 │ → │Worker-3 │ → │Worker-4 │          │
│   │ Opus    │    │ Gemini  │    │  GLM    │    │ Codex   │          │
│   │Backend  │    │Frontend │    │Cohertic │    │Simplify │          │
│   └─────────┘    └─────────┘    └─────────┘    └─────────┘        │
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
- `ISSUE_CONCERNS` - Key concerns/tasks from the issue body

### Step 3: Generate Session Variables

```bash
TIMESTAMP=$(powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'")
PROJECT_ROOT_WINDOWS=$(powershell -NoProfile -Command "(Get-Location).Path")
MPROCS_PORT=$((4000 + ${TIMESTAMP: -4}))
SESSION_ID="${TIMESTAMP}-resolve-issue-${ISSUE_NUMBER}"
BASE_BRANCH=$(git branch --show-current)
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

---

## PHASE 0: Multi-Agent Validation (4 OpenCode agents per concern)

### Step 5: Spawn Validation Agents in Parallel

**For EVERY concern in the issue, spawn exactly 4 OpenCode agents.**

Launch ALL agents in PARALLEL using a SINGLE message with multiple Task tool calls.

**Agent 1 - OpenCode BigPickle (Deep Analysis):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase verification scout using OpenCode BigPickle.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle \"Search codebase for evidence related to: {CONCERN}. Find files that address this concern and existing implementations.\"

Report back:
- Files found that address this concern
- Existing implementations
- Evidence for whether implementation is needed

Verdict: VALID (needs work) or MISTAKEN (already implemented)"
)
```

**Agent 2 - OpenCode GLM 4.7 (Pattern Recognition):**
```
Task(
  subagent_type="general-purpose",
  prompt="... same pattern with glm-4.7-free ..."
)
```

**Agent 3 - OpenCode Grok Code (Quick Search):**
```
Task(
  subagent_type="general-purpose",
  prompt="... same pattern with grok-code ..."
)
```

### Step 6: Categorize Concerns Using Agent Results

**Consensus logic:**
- 3/3 agents agree "needs work" → VALID (high confidence)
- 2/3 agents agree "needs work" → VALID (medium confidence)
- 3/3 agents found existing solution → MISTAKEN (high confidence)
- 2/3 agents found existing solution → MISTAKEN (medium confidence)
- **Tie** → Claude (orchestrator) reviews all evidence and makes final call

Store list of **VALID concerns** for the workers to resolve.

If no VALID concerns, report that issue is already addressed and STOP.

### Step 6b: Learning Scout Agent (GLM 4.7) - BEFORE WORKERS

**Purpose**: Extract relevant learnings from past sessions and project DNA to guide this session's workers.

**Spawn Learning Scout (Task agent):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a Learning Scout using OpenCode GLM 4.7.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free \"You are a Learning Scout. Extract relevant learnings for resolving GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

TASK CONTEXT: {LIST_OF_VALIDATED_CONCERNS}

1. Read .ai-docs/learnings.jsonl (if exists) - extract entries with keywords matching this issue
2. Read .ai-docs/project-dna.md (if exists) - extract relevant principles and patterns
3. Read .ai-docs/bug-patterns.md (if exists) - extract bug fix patterns that might apply
4. Read CLAUDE.md (if exists) - extract coding standards and project instructions

OUTPUT FORMAT (write to stdout):
---SESSION-GUIDELINES-START---
## Relevant Past Learnings
- [learning 1 from similar past tasks]
- [learning 2]

## Project DNA Principles
- [principle 1 relevant to this issue]
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
# Session Guidelines for Issue #{ISSUE_NUMBER}

## Issue
{ISSUE_TITLE}

## Validated Concerns
{LIST_OF_VALIDATED_CONCERNS}

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

## PHASE 1: Resolution Hive (mprocs - Spawn-on-Demand)

### Step 7: Create tasks.json

Write to `.hive/sessions/{SESSION_ID}/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "B-Thread (Resolve Issue)",
  "github_issue": {
    "number": "{ISSUE_NUMBER}",
    "title": "{ISSUE_TITLE}",
    "labels": "{ISSUE_LABELS}"
  },
  "validated_concerns": ["{LIST_OF_VALID_CONCERNS}"],
  "base_branch": "{BASE_BRANCH}",
  "feature_branch": "issue/{ISSUE_NUMBER}-{slug}",
  "workflow": "sequential-with-logging",
  "phases": {
    "workers": ["worker-1", "worker-2", "worker-3", "worker-4"],
    "reviewers": ["reviewer-bigpickle", "reviewer-grok"],
    "resolver": "resolver",
    "tester": "tester"
  }
}
```

### Step 8: Write Worker Task Files

**CRITICAL: Each worker logs decisions/rationale for downstream workers.**

**worker-1-task.md (Backend/Architecture - Opus):**
```markdown
# Worker 1 Task - Backend/Architecture

## Issue
Resolving GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/worker-1.log

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines throughout your work.**

## Validated Concerns to Address

{LIST_OF_VALIDATED_CONCERNS}

## Your Specialty
Backend logic, architecture, APIs, complex algorithms, data models.

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
[14:30:01] WORKER-1: STARTED - Analyzing issue concerns
[14:30:15] WORKER-1: DECISION: Create new API endpoint for user preferences
[14:30:15] WORKER-1: RATIONALE: Issue requires persistent user settings, REST endpoint is most appropriate
[14:30:45] WORKER-1: APPROACH: Using repository pattern, separate service layer for business logic
[14:31:20] WORKER-1: FILE_CHANGED: src/api/preferences.ts - Created preferences endpoint
[14:35:00] WORKER-1: COMPLETED
```

## Instructions

1. Log STARTED
2. Analyze the validated concerns
3. Log your APPROACH and key DECISIONS with RATIONALE
4. Implement backend/architecture changes
5. Log each FILE_CHANGED
6. Log COMPLETED when done
7. **DO NOT commit or push** - Queen handles git

## Begin
Execute your task now.
```

**worker-2-task.md (UI/Frontend - Gemini):**
```markdown
# Worker 2 Task - UI/Frontend

## Issue
Resolving GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/worker-2.log

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines throughout your work.**

## CRITICAL: Read Worker-1's Log First

Before starting, understand what Worker-1 did:
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
```

Pay attention to:
- Their APPROACH and ideology
- Their DECISIONS and RATIONALE
- Files they changed (avoid conflicts, build on their work)
- API endpoints or data structures they created

## Validated Concerns

{LIST_OF_VALIDATED_CONCERNS}

## Your Specialty
UI components, frontend logic, styling, user experience.

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
5. Implement UI/frontend changes
6. Log each FILE_CHANGED
7. Log COMPLETED when done
8. **DO NOT commit or push** - Queen handles git

## Begin
Read Worker-1's log, then execute your task.
```

**worker-3-task.md (Coherence - Grok Code):**
```markdown
# Worker 3 Task - Backend/Frontend Coherence

## Issue
Resolving GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/worker-3.log

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines throughout your work.**

## CRITICAL: Read Previous Workers' Logs First

```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-2.log"
```

Understand:
- Worker-1's backend approach and API contracts
- Worker-2's frontend approach and data expectations
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
3. Check for coherence issues:
   - API contracts match frontend expectations
   - Data types align
   - Error handling is consistent
4. Log any COHERENCE_FIX entries with RATIONALE
5. Make fixes, logging each FILE_CHANGED
6. Log COMPLETED when done
7. **DO NOT commit or push** - Queen handles git

## Begin
Read previous logs, then verify coherence.
```

**worker-4-task.md (Code Simplification - Codex GPT-5.2):**
```markdown
# Worker 4 Task - Code Simplification

## Issue
Resolving GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/worker-4.log

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**You MUST follow these guidelines - especially coding standards - during simplification.**

## CRITICAL: Read Previous Workers' Logs First

```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-2.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-3.log"
```

Understand:
- What files were modified by each worker
- The approach and decisions made
- Any coherence fixes from Worker-3

## Your Specialty: Code Simplification

Reference the code-simplifier skill principles:

### Principles
- **Preserve functionality**: Do not change what the code does
- **Apply project standards** from CLAUDE.md
- **Enhance clarity**: Reduce nesting, remove redundant code, improve naming, consolidate related logic, remove obvious comments, avoid nested ternaries
- **Maintain balance**: Avoid over-simplifying, overly clever solutions, merging too many concerns, or removing helpful abstractions
- **Focus scope**: Refine only recently modified code (files touched by workers 1-3)

### Workflow
1. Identify files modified by workers 1-3 (check FILE_CHANGED entries)
2. Review for simplification opportunities and standard alignment
3. Apply minimal, safe refactors and keep interfaces stable
4. Verify behavior is unchanged
5. Report only significant readability changes

## Structured Logging Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/worker-4.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] WORKER-4: message'"
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
2. **Read Worker-1, Worker-2, and Worker-3 logs completely**
3. Identify all FILE_CHANGED entries to know which files to simplify
4. Review each modified file for simplification opportunities
5. Apply minimal, safe refactors (do not change behavior!)
6. Log SIMPLIFIED or SKIPPED for each file
7. Log COMPLETED when done
8. **DO NOT commit or push** - Queen handles git

## Begin
Read previous logs, then simplify the modified code.
```

### Step 9: Write Reviewer Task Files

**reviewer-bigpickle-task.md:**
```markdown
# Reviewer Task - BigPickle (Deep Analysis)

## Issue
Reviewing GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Review File**: .hive/sessions/{SESSION_ID}/reviews/bigpickle.md

## Session Guidelines (Review Against These!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**Review code changes against these guidelines. Flag violations as findings.**

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
- Missing test coverage

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

1. Read all worker logs to understand decisions made
2. Review changed files (use `git diff`)
3. Look for issues the workers might have missed
4. Write findings to your review file
5. End with `COMPLETED`

## Begin
Execute your review now.
```

**reviewer-grok-task.md:**
```markdown
# Reviewer Task - Grok (Quick Observations)

## Issue
Reviewing GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Review File**: .hive/sessions/{SESSION_ID}/reviews/grok.md

## Session Guidelines (Review Against These!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**Quick-check code changes against these guidelines.**

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

## Instructions

1. Read worker logs
2. Quick review of changes
3. Write observations to your review file
4. End with `COMPLETED`

## Begin
Execute your review now.
```

### Step 10: Write Resolver Task File

**resolver-task.md:**
```markdown
# Resolver Task - Address All Reviewer Findings

## Issue
Resolving GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/resolver.log

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**Apply these guidelines when fixing issues.**

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
4. If skipping a finding, log SKIPPED with RATIONALE
5. Log COMPLETED when done
6. **DO NOT commit or push** - Queen handles git

## Begin
Read reviewer findings and resolve them.
```

### Step 11: Write Tester Task File

**tester-task.md:**
```markdown
# Tester Task - Run Tests and Fix Failures

## Issue
Testing GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/tester.log

## Session Guidelines (Test Against These!)

**READ THIS FIRST**: `.hive/sessions/{SESSION_ID}/session-guidelines.md`

{EMBEDDED_SESSION_GUIDELINES}

**Ensure tests validate adherence to these guidelines.**

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
4. Re-run tests until passing (max 3 attempts)
5. Log any DIFFICULTY entries for unresolved issues
6. Log COMPLETED
7. **DO NOT commit or push** - Queen handles git

## Begin
Run tests and fix failures.
```

### Step 11b: Write Code Quality Task Template

**Write code-quality-task-template.md for Phase 7 agents:**

Write to `.hive/sessions/{SESSION_ID}/code-quality-task-template.md`:

```markdown
# Code Quality Task - Iteration {N}

## Issue
Resolving PR comments for GitHub issue #{ISSUE_NUMBER}: {ISSUE_TITLE}

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/code-quality-{N}.log
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
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/code-quality-{N}.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] CODE-QUALITY-{N}: message'"
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

### Step 12: Write Queen Prompt

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen Agent - Resolve Issue #{ISSUE_NUMBER}

You are the **Queen** orchestrating a spawn-on-demand hive to resolve this GitHub issue.

## Issue Details

**Issue #{ISSUE_NUMBER}**: {ISSUE_TITLE}

{ISSUE_BODY}

**Labels**: {ISSUE_LABELS}

## Validated Concerns (from Phase 0)

These concerns were verified by 4 agents each and confirmed as VALID:

{LIST_OF_VALIDATED_CONCERNS}

## Session Guidelines (CRITICAL - READ FIRST!)

A Learning Scout has extracted relevant learnings and project DNA for this issue:
`.hive/sessions/{SESSION_ID}/session-guidelines.md`

**BEFORE spawning ANY workers, you MUST:**
1. Read the session-guidelines.md file completely
2. Internalize the guidelines - they apply to ALL workers
3. These guidelines are already embedded in each worker's task file

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/logs/queen.log
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}
- **Feature Branch**: issue/{ISSUE_NUMBER}-{slug}
- **Base Branch**: {BASE_BRANCH}

## Workflow: Sequential Workers with Logging

**CRITICAL**: Workers run SEQUENTIALLY. Each reads the previous worker's log.

### Phase 0: Setup (DO THIS FIRST!)

**Phase 0.1: Create Feature Branch**
```bash
git checkout -b issue/{ISSUE_NUMBER}-{slug}
```

**Phase 0.2: Verify Session Guidelines**
Read and log that you've reviewed the session guidelines:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Reviewed session-guidelines.md - {number} guidelines codified\""
```

### Phase 1: Sequential Workers

**Phase 1.1: Spawn Worker-1 (Cursor CLI - Opus 4.5 - Backend/Architecture)**

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

**Phase 1.2: Spawn Worker-2 (Gemini - UI/Frontend)**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "gemini -m gemini-3-pro-preview -y -i \"Read .hive/sessions/{SESSION_ID}/worker-2-task.md and execute.\"", "name": "worker-2"}'
```

Wait for COMPLETED in worker-2.log.

**Gemini Fallback**: If Gemini fails with quota error, use flash:
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "gemini -m gemini-3-flash-preview -y -i \"Read .hive/sessions/{SESSION_ID}/worker-2-task.md and execute.\"", "name": "worker-2"}'
```

**Phase 1.3: Spawn Worker-3 (Grok - Coherence)**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read .hive/sessions/{SESSION_ID}/worker-3-task.md and execute.\"", "name": "worker-3", "env": {"OPENCODE_YOLO": "true"}}'
```

Wait for COMPLETED in worker-3.log.

**Phase 1.4: Spawn Worker-4 (Codex GPT-5.2 - Code Simplification)**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .hive/sessions/{SESSION_ID}/worker-4-task.md and execute.\"", "name": "worker-4"}'
```

Wait for COMPLETED in worker-4.log.

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

### Phase 5: Curate Learnings (QUEEN REVIEWS LOGS FIRST!)

**BEFORE running curate-learnings, YOU (Queen) must:**

1. **Read ALL worker logs completely:**
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-2.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-3.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/worker-4.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/resolver.log"
Get-Content ".hive/sessions/{SESSION_ID}/logs/tester.log"
```

2. **Read ALL reviewer findings:**
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/reviews/bigpickle.md"
Get-Content ".hive/sessions/{SESSION_ID}/reviews/grok.md"
```

3. **Synthesize key insights** - What worked? What didn't? What patterns emerged?

4. **Log your synthesis:**
```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: SESSION SYNTHESIS - {key insights}\""
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
    task = "Resolve issue #{ISSUE_NUMBER}"
    outcome = "success"
    keywords = @("{keyword1}", "{keyword2}")
    insight = "{YOUR_SYNTHESIS}"
    files_touched = @("{file1}", "{file2}")
} | ConvertTo-Json -Compress
Add-Content -Path ".ai-docs/learnings.jsonl" -Value $learning
```

If the directory doesn't exist, the above command creates it. Do NOT skip this step because of .gitignore!

### Phase 6: Commit, Push & Create PR

**Collect difficulties from tester log:**
```powershell
Select-String -Path ".hive/sessions/{SESSION_ID}/logs/tester.log" -Pattern "DIFFICULTY"
```

**Commit and push:**
```bash
git add -A
git commit -m "fix: resolve issue #{ISSUE_NUMBER}

{summary of changes}

Resolves #{ISSUE_NUMBER}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"

git push -u origin issue/{ISSUE_NUMBER}-{slug}
```

**Create PR with difficulties noted:**
```bash
gh pr create --base {BASE_BRANCH} --title "fix: {ISSUE_TITLE}" --body "$(cat <<'EOF'
## Summary
Resolves #{ISSUE_NUMBER}

{summary of what was implemented}

## Workers
- Worker-1 (Opus): Backend/architecture changes
- Worker-2 (Gemini): UI/frontend changes
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

### Phase 7: Code Quality Loop (Automated PR Comment Resolution)

**⚠️ MANDATORY - DO NOT SKIP THIS PHASE ⚠️**

You MUST execute Phase 7 after creating the PR. Do not ask the user if they want to proceed - just do it.

**After PR creation, external reviewers (Gemini, Codex, Code Rabbit) will comment on the PR.**

This phase automates resolving those comments iteratively until the PR is clean.

#### Phase 7.1: Wait for External Reviews (10 minutes)

**⚠️ YOU MUST ACTUALLY WAIT - DO NOT SKIP ⚠️**

External reviewers (Gemini, Codex, Code Rabbit) need time to analyze the PR. You MUST execute the sleep command and wait the full 10 minutes before checking for comments.

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Waiting 10 minutes for external reviewers...\"; Start-Sleep -Seconds 600; Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Wait complete. Checking for comments...\""
```

**DO NOT proceed to Step 2 until this command completes (10 minutes).**

#### Phase 7.2: Check for New Comments

```bash
# Get the PR number we just created
PR_NUMBER=$(gh pr list --head issue/{ISSUE_NUMBER}-{slug} --json number -q '.[0].number')

# Check for new comments
NEW_COMMENTS=$(gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments --jq 'length')
```

**If NEW_COMMENTS = 0**: Log "No new comments. PR is ready for human review." and END.

#### Phase 7.3: Write and Spawn Code Quality Agent (Opus)

**Phase 7.3a: Write iteration-specific task file**

Copy the template and fill in iteration details:
```powershell
# Read template and replace {N} with current iteration number
$template = Get-Content ".hive/sessions/{SESSION_ID}/code-quality-task-template.md" -Raw
$taskContent = $template -replace '\{N\}', '{N}' -replace '\{PR_NUMBER\}', '$PR_NUMBER'
Set-Content -Path ".hive/sessions/{SESSION_ID}/code-quality-{N}-task.md" -Value $taskContent
```

**Phase 7.3b: Create empty log file**
```powershell
New-Item -Path ".hive/sessions/{SESSION_ID}/logs/code-quality-{N}.log" -ItemType File -Force
```

**Phase 7.3c: Spawn code-quality-{N} agent via MPROCS (Cursor CLI)**

**⚠️ YOU MUST USE MPROCS - NOT TASK TOOL ⚠️**

Do NOT use the Task tool to spawn subagents yourself. You MUST spawn a visible mprocs agent:

Write spawn .bat file:
```powershell
Set-Content -Path ".hive/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.hive/sessions/{SESSION_ID}/code-quality-{N}-task.md and execute.\\\"\", \"name\": \"code-quality-{N}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

Execute:
```bash
.hive/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat
```

The code-quality agent will handle the PR comments. Your job is to SPAWN and MONITOR, not to do the work yourself.

#### Phase 7.4: Monitor and Loop

1. Wait for `COMPLETED` in code-quality-{N}.log
2. Wait another 10 minutes for new reviews
3. Check for new comments
4. If new comments exist, spawn code-quality-{N+1}
5. Repeat until no new comments

**Loop termination conditions:**
- No new comments after 10-minute wait
- Maximum 5 iterations (to prevent infinite loops)

#### Phase 7.5: Log Completion

```powershell
powershell -NoProfile -Command "Add-Content -Path '.hive/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Code Quality Loop complete. {N} iterations. PR is ready for human review.\""
```

## End of Queen Workflow

You have completed your mission when Phase 7 terminates (either no new comments or max iterations).
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
2. Respawn with flash model

## Begin

Announce: "Queen initialized for issue #{ISSUE_NUMBER}. Creating feature branch and starting Phase 1: Sequential workers..."
```

### Step 13: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# Spawn-on-Demand Hive - Issue Resolution
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
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== HIVE ISSUE RESOLUTION LOGS ===' -ForegroundColor Cyan; Get-ChildItem .hive/sessions/{SESSION_ID}/logs -Filter *.log -ErrorAction SilentlyContinue | ForEach-Object { Write-Host ('--- ' + $_.Name + ' ---') -ForegroundColor Yellow; Get-Content $_.FullName -Tail 5 -ErrorAction SilentlyContinue }; Write-Host '--- REVIEWS ---' -ForegroundColor Magenta; Get-ChildItem .hive/sessions/{SESSION_ID}/reviews -Filter *.md -ErrorAction SilentlyContinue | ForEach-Object { Write-Host $_.Name; Get-Content $_.FullName -Tail 3 -ErrorAction SilentlyContinue }; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

### Step 14: Create Log Files

```bash
cd "{PROJECT_ROOT}"
type nul > ".hive/sessions/{SESSION_ID}/logs/queen.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/worker-1.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/worker-2.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/worker-3.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/worker-4.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/resolver.log"
type nul > ".hive/sessions/{SESSION_ID}/logs/tester.log"
type nul > ".hive/sessions/{SESSION_ID}/reviews/bigpickle.md"
type nul > ".hive/sessions/{SESSION_ID}/reviews/grok.md"
```

### Step 15: Launch mprocs

```bash
powershell -Command "Start-Process powershell -WorkingDirectory '{PROJECT_ROOT_WINDOWS}' -ArgumentList '-NoExit', '-Command', 'mprocs --config .hive/mprocs.yaml'"
```

### Step 16: Output Status

```markdown
## Hive Issue Resolver Launched!

**Session**: {SESSION_ID}
**Issue**: #{ISSUE_NUMBER} - {ISSUE_TITLE}
**Branch**: issue/{ISSUE_NUMBER}-{slug}

### Phase 0: Validation Complete

| Concern | BigPickle | GLM 4.7 | Grok | Verdict |
|---------|-----------|---------|------|---------|---------|
{VALIDATION_RESULTS_TABLE}

**Validated Concerns**: {VALID_COUNT}

### Architecture: Spawn-on-Demand with Sequential Workers

```
Queen (Opus)
    │
    ├─► Worker-1 (Opus) ──► logs decisions + changes
    │       ↓ (sequential)
    ├─► Worker-2 (Gemini) ──► reads W1 logs, logs own
    │       ↓ (sequential)
    ├─► Worker-3 (Grok) ──► coherence check
    │       ↓ (sequential)
    ├─► Worker-4 (Codex) ──► code simplification
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
| `logs/worker-1.log` | Backend/architecture decisions |
| `logs/worker-2.log` | UI/frontend decisions |
| `logs/worker-3.log` | Coherence fixes |
| `logs/worker-4.log` | Code simplification |
| `logs/resolver.log` | How findings were addressed |
| `logs/tester.log` | Test results and difficulties |
| `reviews/*.md` | Reviewer findings |

Watch the issue get resolved!
```

## Usage

```bash
/resolve-hive-issue 42
/resolve-hive-issue https://github.com/owner/repo/issues/42
```
