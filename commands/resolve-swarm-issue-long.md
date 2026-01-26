---
description: Long-horizon swarm resolution with sequential Planners (1-2 at a time), up to 10 Planners for complex multi-domain issues
argument-hint: "<issue-numbers>" [--by-issue | --by-domain]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
---

# Resolve Swarm Issue Long - Sequential Multi-Planner Orchestration

Launch a **long-horizon swarm** where the Queen deploys Planners **sequentially** (1-2 at a time), allowing adaptive domain decomposition. Supports **one or more GitHub issues** in a single branch.

## Architecture

```
Queen (Opus 4.5) → Planners A-J (Opus 4.5) → Workers (mixed models)
                        ↓
              SEQUENTIAL WAVES (1-2 Planners per wave)
              Max 10 Planners total
```

## Arguments

- `<issue-numbers>`: One or more issue numbers/URLs (space or comma separated)
  - Single: `42`
  - Multiple: `42 43 44` or `42,43,44`
- `[--by-issue]`: Scaffold waves by issue (Wave 1 = Issue 1, Wave 2 = Issue 2, etc.)
- `[--by-domain]`: Pool all concerns, scaffold waves by domain dependency

---

## Step 1: Check Prerequisites

```bash
mprocs --version
gh --version
git rev-parse --is-inside-work-tree
```

## Step 2: Parse and Fetch All Issues

Parse issue numbers, then fetch each:

```bash
for issue in {ISSUE_NUMBERS}; do
  gh issue view $issue --json title,body,labels,state,comments
done
```

Store per-issue: `ISSUES[N].number`, `.title`, `.body`, `.labels`, `.concerns`

## Step 3: Generate Session Variables

```bash
TIMESTAMP=$(powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'")
PROJECT_ROOT_WINDOWS=$(powershell -NoProfile -Command "(Get-Location).Path")
MPROCS_PORT=$((4000 + ${TIMESTAMP: -4}))
ISSUE_COUNT={length of ISSUE_NUMBERS}
if [ $ISSUE_COUNT -eq 1 ]; then
  SESSION_ID="${TIMESTAMP}-resolve-swarm-long-${ISSUE_NUMBERS[0]}"
  BRANCH_NAME="issue/${ISSUE_NUMBERS[0]}-{slug}"
else
  SESSION_ID="${TIMESTAMP}-resolve-swarm-long-multi-${ISSUE_NUMBERS[0]}"
  BRANCH_NAME="issue/multi-${ISSUE_NUMBERS[0]}-{slug}"
fi
BASE_BRANCH=$(git branch --show-current)
```

## Step 4: Create Session Directory

```bash
mkdir -p ".swarm/sessions/{SESSION_ID}/docs"
mkdir -p ".swarm/sessions/{SESSION_ID}/phases"
mkdir -p ".swarm/sessions/{SESSION_ID}/state"
mkdir -p ".swarm/sessions/{SESSION_ID}/logs"

# Pre-create ALL possible Planner directories (A through J)
for letter in a b c d e f g h i j; do
  mkdir -p ".swarm/sessions/{SESSION_ID}/tasks/planner-$letter"
done
```

## Step 5: Copy Templates + Generate Config

Copy from `~/.claude/swarm-templates/` to session folder:

**To root session folder:**
- Generate `config.json` from `config-template.json` (replace all placeholders)

**To `docs/`:**
- model-selection.md
- spawn-templates.md
- log-protocol.md
- **roles.md**
- **declaration-protocol.md** (MANDATORY - all agents must follow)
- **planner-cross-reference.md** (for later Planners)

**To `phases/`:** phase-1 through phase-6

**To `state/`:**
- Create `planner-status.md` (Queen updates this as Planners complete)

**CRITICAL FILES (agents MUST read these first):**
1. `config.json` - **AUTHORITATIVE** model assignments. DO NOT IMPROVISE.
2. `docs/roles.md` - Strict hierarchy
3. `docs/declaration-protocol.md` - Declare before execute

---

## PHASE 0: Concern Validation

Same as `/resolve-swarm-issue`:
- Spawn 3 agents per concern
- Consensus logic
- Store validated concerns
- Learning Scout → `state/session-guidelines.md`

---

## PHASE 0.5: Initial Domain Decomposition (Wave 1 Only)

### Step 6: Decide Wave Strategy

**Mode: --by-issue** (One issue per wave)
- Wave 1: Issue #1 (foundational)
- Wave 2: Issue #2 (builds on Wave 1)
- etc.
- Good for related but sequential issues

**Mode: --by-domain** (Pool concerns, waves by dependency)
- Wave 1: Foundational domains (core, backend)
- Wave 2: Dependent domains (frontend, integration)
- etc.
- Good for overlapping issues

### Step 7: Assign Wave 1

**Only plan Wave 1** - Queen plans future waves adaptively.

Write to `state/responsibility-matrix.md`:

```markdown
## Swarm Responsibility Matrix (Long-Horizon)

### Issues Being Resolved
| # | Title | Valid Concerns |
|---|-------|----------------|
| {ISSUE_1} | {TITLE_1} | {COUNT} |
| {ISSUE_2} | {TITLE_2} | {COUNT} |

### Mode: {--by-issue | --by-domain}

### All Validated Concerns (Total: {COUNT})
{LIST_ALL_CONCERNS_WITH_SOURCE_ISSUE}

---

## Wave 1 (Initial)

**Mode: --by-issue**
### Planner A - Issue #{ISSUE_1}
**Issue**: #{ISSUE_1} - {TITLE_1}
**Concerns**: {all concerns from issue 1}
**Why first**: {foundational issue}

**Mode: --by-domain**
### Planner A - {DOMAIN_A}
**Domain**: {foundational domain}
**Concerns**: {from issues #1, #2, ...}
**Why first**: {rationale}

### Planner B (if 2 in Wave 1)
...

---

## Future Waves (Queen Decides)

### Remaining Issues/Concerns
{LIST_NOT_ASSIGNED}

### Suggested Wave Plan
- Wave 2: {issue/domain}
- Wave 3: {issue/domain}
- etc.
```

### Step 7: File Scouts (Wave 1 only)

Spawn scouts for Wave 1 domains → `state/file-ownership.md`

### Step 8: Initialize Wave Status

Write to `state/wave-status.md`:

```markdown
# Wave Status - Issue #{ISSUE_NUMBER}

**Mode**: Long-Horizon Sequential
**Max Planners**: 10

## Progress
- Total Concerns: {COUNT}
- Concerns Resolved: 0
- Planners Deployed: 0/10
- Waves Completed: 0

---

## Wave 1
- **Planners**: A, B
- **Status**: PENDING
- **Concerns**: {count}
```

### Step 9: Write Issue Context

Write to `state/context.md` (include long-horizon details):

```markdown
# Issue Context (Long-Horizon)

## Issues Being Resolved
| # | Title | Labels | Valid Concerns |
|---|-------|--------|----------------|
| {ISSUE_1} | {TITLE_1} | {LABELS_1} | {COUNT} |
| {ISSUE_2} | {TITLE_2} | {LABELS_2} | {COUNT} |

---

## Issue #{ISSUE_1}
**Title**: {TITLE_1}
**Body**:
{BODY_1}

**Validated Concerns**:
{LIST_1}

---

## Issue #{ISSUE_2}
**Title**: {TITLE_2}
**Body**:
{BODY_2}

**Validated Concerns**:
{LIST_2}

---

## Session
- ID: {SESSION_ID}
- Branch: {BRANCH_NAME}
- Base: {BASE_BRANCH}
- **Mode**: LONG-HORIZON (Sequential Waves)
- **Wave Strategy**: {--by-issue | --by-domain}
- **Max Planners**: 10
- **Resolves**: #{ISSUE_1}, #{ISSUE_2}, ...
```

---

## PHASE 1: Swarm Setup

### Step 10: Generate Queen Prompt (THIN with absolute paths + inlined spawn commands)

Write to `.swarm/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen - Long-Horizon Issues {ISSUE_LIST}

---

## 🚨 CRITICAL: NO IMPROVISING, NO QUESTIONS 🚨

**READ config.json FIRST. Follow it EXACTLY. Do not ask "what's the correct syntax?" - the syntax is IN THE CONFIG.**

- If unsure about a model → READ config.json
- If unsure about a CLI command → READ config.json
- If unsure about spawn syntax → READ config.json and declaration-protocol.md

**NEVER improvise model assignments. NEVER ask clarifying questions about commands. The answers are in your context files.**

---

## ⚠️ ROLE BOUNDARIES ⚠️

You are the **QUEEN** - top-level orchestrator in a 3-tier hierarchy:

```
TIER 1: QUEEN (you)     → Spawns PLANNERS only
TIER 2: PLANNERS        → Spawn Workers, Reviewers, Testers
TIER 3: WORKERS         → Execute implementation tasks
```

### YOU MUST:
- Spawn **PLANNERS** (A through J) to handle domains/issues
- Write Planner prompt files before spawning
- Monitor Planner progress via logs
- Coordinate waves sequentially
- Run integration cycle AFTER all Planners complete
- Commit and create PR

### YOU MUST NOT:
- ❌ **NEVER spawn Workers directly** - that's the Planner's job
- ❌ **NEVER write worker task files** - Planners do that
- ❌ **NEVER execute implementation code** - Workers do that
- ❌ **NEVER bypass the hierarchy** - trust your Planners

If you find yourself wanting to spawn a Worker, STOP. Write a Planner prompt instead and let the Planner spawn Workers.

---

## Session
- **ID**: {SESSION_ID}
- **Project Root**: {PROJECT_ROOT}
- **Log**: logs/queen.log (relative from project root)
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}
- **Branch**: {BRANCH_NAME}
- **Base**: {BASE_BRANCH}
- **Mode**: LONG-HORIZON
- **Wave Strategy**: {--by-issue | --by-domain}
- **Max Planners**: 10 (A through J)
- **Resolves**: #{ISSUE_1}, #{ISSUE_2}, ...

## Read for Context (ABSOLUTE PATHS) - IN THIS ORDER

**CRITICAL - READ THESE FIRST (AUTHORITATIVE):**
1. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/config.json` - **AUTHORITATIVE MODEL CONFIG. DO NOT IMPROVISE.**
2. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/declaration-protocol.md` - **MANDATORY: Declare before every spawn**
3. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/roles.md` - Role hierarchy

**Context files:**
4. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/context.md`
5. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/responsibility-matrix.md`
6. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/file-ownership.md`
7. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/session-guidelines.md`
8. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/wave-status.md`
9. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/planner-status.md` - Track Planner completions
10. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/planner-cross-reference.md` - How to share context between Planners
11. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/log-protocol.md`

## Log Protocol
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: {MESSAGE}\""
```

Coordination:
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/coordination.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: [DIRECTIVE] {MESSAGE}\""
```

## Setup
```bash
git checkout -b {BRANCH_NAME}
```

---

## TIER 1 SPAWN COMMANDS (Planners Only)

**These are the ONLY spawn commands you execute during Phases 1-3.**

### ⚠️ DECLARATION REQUIRED BEFORE EVERY SPAWN

Before executing ANY spawn command, you MUST declare:

```
DECLARATION: I will spawn Planner {X} using Claude CLI with model Opus.
Command: [paste exact command]
```

Then execute. This catches drift BEFORE it wastes tokens.

### Spawn Planner A
```
DECLARATION: I will spawn Planner A using Claude CLI with model Opus.
Command: mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-a-prompt.md and execute.\"", "name": "planner-a", "cwd": "{PROJECT_ROOT}"}'
```

### Spawn Planner B
```
DECLARATION: I will spawn Planner B using Claude CLI with model Opus.
Command: mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-b-prompt.md and execute.\"", "name": "planner-b", "cwd": "{PROJECT_ROOT}"}'
```

### Spawn Planner C-J (as needed)
```
DECLARATION: I will spawn Planner {X} using Claude CLI with model Opus.
Command: mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-{X}-prompt.md and execute.\"", "name": "planner-{X}", "cwd": "{PROJECT_ROOT}"}'
```

---

## PHASE 4+ SPAWN COMMANDS (Integration Team - After All Waves)

**ONLY use these AFTER all Planners have signaled PLANNER_COMPLETE.**

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/integration-reviewer-task.md and execute.\"", "name": "integration-reviewer", "cwd": "{PROJECT_ROOT}", "env": {"OPENCODE_YOLO": "true"}}'
```

---

## CRITICAL: Sequential Wave Execution

Unlike regular swarm, you deploy Planners in WAVES:

### Wave Loop
1. **Write** Planner prompts for this wave (1-2 Planners)
2. **USE BASH TOOL** to execute SPAWN COMMANDS above - copy-paste each command exactly
3. **Wait** for ALL wave Planners to show PLANNER_COMPLETE
4. **Review** wave results, update `state/wave-status.md`
5. **Plan next wave** - update `state/responsibility-matrix.md`
6. **File scouts** for new domains/issues
7. **Repeat** until all issues/concerns addressed OR 10 Planners deployed

### Wave Strategy

**--by-issue mode:**
| Wave | Planners | Content |
|------|----------|---------|
| 1 | A | Issue #1 (foundational) |
| 2 | B | Issue #2 (builds on #1) |
| 3 | C, D | Issues #3, #4 (independent) |

**--by-domain mode:**
| Wave | Planners | Content |
|------|----------|---------|
| 1 | A, B | Core + Backend (from all issues) |
| 2 | C | Frontend (depends on 1) |
| 3 | D | Testing (depends on 2) |

### Decision: Solo vs Pair

| Situation | Deploy |
|-----------|--------|
| Building on previous wave | 1 (solo) |
| Two independent issues/domains remain | 2 (pair) |
| Complex integration work | 1 (solo) |
| Final testing/cleanup | 1 (solo) |

### After All Waves
1. See `phases/phase-4-integration.md` - Integration review
2. See `phases/phase-5-commit.md` - Curate learnings, commit, PR
3. **Phase 6: Code Quality Loop (MANDATORY)**

### Phase 6: Code Quality Loop

**⚠️ DO NOT SKIP THIS PHASE ⚠️**

After PR is pushed, execute the code quality loop:

**Loop Parameters:**
- **Wait time per cycle**: 10 minutes
- **Maximum cycles**: 3
- **Code Quality Agent**: Cursor CLI (Opus 4.5)

**Loop Flow:**
1. Wait 10 minutes for external reviewers (Gemini, Codex, Code Rabbit)
2. Check for new comments: `gh api repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/comments --jq 'length'`
3. If no comments → END (success)
4. If comments → spawn code-quality-{N} agent (Cursor CLI):
   - Write task file from `tasks/code-quality-task-template.md`
   - Write spawn .bat: `spawn-code-quality-{N}.bat`
   - Execute .bat to spawn via mprocs
5. Wait for COMPLETED in code-quality-{N}.log
6. Agent commits/pushes fixes
7. If N < 3 → repeat from step 1
8. If N = 3 → END (max cycles)

**Code Quality Agent Spawn (.bat file):**
```batch
@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/code-quality-{N}-task.md and execute.\\\"\", \"name\": \"code-quality-{N}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

See `phases/phase-6-code-quality.md` for full details.

## Capabilities Matrix

| Action | Queen | Planner | Worker |
|--------|-------|---------|--------|
| Spawn Planners | ✅ YES | ❌ NO | ❌ NO |
| Spawn Workers | ❌ NO | ✅ YES | ❌ NO |
| Write Planner prompts | ✅ YES | ❌ NO | ❌ NO |
| Write Worker tasks | ❌ NO | ✅ YES | ❌ NO |
| Implement code | ❌ NO | ❌ NO | ✅ YES |
| Update wave-status.md | ✅ YES | ❌ NO | ❌ NO |
| Plan future waves | ✅ YES | ❌ NO | ❌ NO |
| Run integration cycle | ✅ YES | ❌ NO | ❌ NO |
| Commit code | ✅ YES | ❌ NO | ❌ NO |
| Push PR | ✅ YES | ❌ NO | ❌ NO |

## Begin
1. Log STARTED to queen.log
2. Create branch
3. Read context files
4. Write Wave 1 **Planner prompts** (NOT worker tasks)
5. Spawn Wave 1 **Planners** (NOT workers)
```

### Step 11: Generate Wave 1 Planner Prompts (THIN with absolute paths + inlined spawn commands)

Write to `.swarm/sessions/{SESSION_ID}/planner-{X}-prompt.md`:

```markdown
# Planner {X} - Wave {N} - {DOMAIN}

---

## 🚨 CRITICAL: NO IMPROVISING, NO QUESTIONS 🚨

**READ config.json FIRST. Follow it EXACTLY.**

- Worker 1 = Backend (Cursor/Opus) - ALL Python work
- Worker 2 = Frontend (Gemini) - ALL TypeScript/React work
- Worker 3 = Coherence (Grok) - Consistency checks
- Worker 4 = Simplify (Codex) - Cleanup

**DO NOT assign work by feature domain. Assign by ROLE. The config.json defines the models. USE THEM EXACTLY.**

---

## ⚠️ ROLE BOUNDARIES ⚠️

You are a **PLANNER** - middle-tier orchestrator in a 3-tier hierarchy:

```
TIER 1: QUEEN           → Spawned you, monitors your progress
TIER 2: PLANNER (you)   → Spawn Workers, Reviewers, Testers
TIER 3: WORKERS         → Execute implementation tasks
```

### YOU MUST:
- **READ config.json FIRST** - it defines all model assignments
- Break your domain/issue into **Worker tasks BY ROLE** (not by feature)
- Write task files to `tasks/planner-{X}/`
- **DECLARE before EVERY spawn** (see declaration-protocol.md)
- Spawn **Workers** to execute those tasks
- Spawn **Reviewer** and **Tester** after Workers complete
- **Write summary.md** before signaling complete
- Signal **PLANNER_COMPLETE** to Queen when done

### YOU MUST NOT:
- ❌ **NEVER improvise model assignments** - use config.json
- ❌ **NEVER ask "what's the correct syntax?"** - it's in config.json
- ❌ **NEVER spawn other Planners** - only Queen does that
- ❌ **NEVER work outside your assigned domain** - respect file ownership
- ❌ **NEVER implement code yourself** - delegate to Workers
- ❌ **NEVER signal PLANNER_COMPLETE until review cycle done**

If a concern is outside your domain, log it to coordination.log for Queen to assign to another Planner.

---

## Session
- **ID**: {SESSION_ID}
- **Project Root**: {PROJECT_ROOT}
- **Log**: logs/planner-{X}.log (relative from project root)
- **Tasks**: tasks/planner-{X}/
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}
- **Wave**: {N}

## Read for Context (ABSOLUTE PATHS) - IN THIS ORDER

**CRITICAL - READ THESE FIRST (AUTHORITATIVE):**
1. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/config.json` - **AUTHORITATIVE MODEL CONFIG. USE EXACT MODELS. DO NOT IMPROVISE.**
2. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/declaration-protocol.md` - **MANDATORY: Declare before every spawn**
3. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/roles.md` - Role hierarchy

**Cross-Reference (if later wave):**
4. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/planner-status.md` - Check completed Planners
5. If Planner A COMPLETED: `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-a/summary.md`
6. If Planner B COMPLETED: `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-b/summary.md`
(Read completed Planner summaries to inherit patterns and avoid re-exploration)

**Context files:**
7. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/context.md`
8. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/responsibility-matrix.md` - Your concerns
9. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/file-ownership.md` - Your files
10. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/session-guidelines.md`
11. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/log-protocol.md`

## Log Protocol
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/planner-{X}.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] PLANNER-{X}: {MESSAGE}\""
```

Coordination with Queen:
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/coordination.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] PLANNER-{X}: [STATUS] {MESSAGE}\""
```

---

## TIER 2 SPAWN COMMANDS (Workers, Reviewer, Tester)

**These are your spawn commands. Execute via Bash tool.**

### ⚠️ STANDARDIZED WORKER ROLES (from config.json - DO NOT MODIFY)

| Worker | Role | Model | CLI | Specialty |
|--------|------|-------|-----|-----------|
| Worker 1{X} | **Backend** | Opus 4.5 | Cursor | ALL Python/FastAPI/database work |
| Worker 2{X} | **Frontend** | Gemini 3 Pro | Gemini | ALL TypeScript/React work |
| Worker 3{X} | **Coherence** | Grok | OpenCode | Cross-cutting consistency checks |
| Worker 4{X} | **Simplify** | Codex/GPT-5.2 | Codex | Code cleanup, optimization |

**DO NOT assign work by feature domain. Assign by ROLE:**
- Backend = ALL Python code (models, schemas, CRUD, routes, migrations)
- Frontend = ALL TypeScript/React code (types, API client, components, hooks)
- Coherence = Verify backend/frontend consistency
- Simplify = Clean up after Workers 1-3

### ⚠️ DECLARATION REQUIRED BEFORE EVERY SPAWN

Before executing ANY spawn command, you MUST declare:

```
DECLARATION: I will spawn Worker {N}{X} using {CLI} with model {MODEL}.
Command: [paste exact command]
```

Example:
```
DECLARATION: I will spawn Worker 1A using Cursor CLI with model Opus 4.5.
Command: .swarm/sessions/{SESSION_ID}/tasks/planner-a/spawn-worker-1a.bat
```

---

### Worker 1{X} - Backend (Cursor CLI - Opus 4.5)

**Declaration:**
```
DECLARATION: I will spawn Worker 1{X} using Cursor CLI with model Opus 4.5.
Role: Backend - ALL Python/FastAPI/database work
```

**Step 1: Write spawn .bat file**
```powershell
Set-Content -Path ".swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-1{X}.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-1{X}-task.md and execute.\\\"\", \"name\": \"worker-1{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

**Step 2: Execute**
```bash
.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-worker-1{X}.bat
```

---

### Worker 2{X} - Frontend (Gemini 3 Pro)

**Declaration:**
```
DECLARATION: I will spawn Worker 2{X} using Gemini CLI with model gemini-3-pro-preview.
Role: Frontend - ALL TypeScript/React work
```

**Command:**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "gemini -m gemini-3-pro-preview -y -i \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-2{X}-task.md and execute.\"", "name": "worker-2{X}", "cwd": "{PROJECT_ROOT}"}'
```

---

### Worker 3{X} - Coherence (Grok)

**Declaration:**
```
DECLARATION: I will spawn Worker 3{X} using OpenCode CLI with model grok-code.
Role: Coherence - Cross-cutting consistency checks
```

**Command:**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-3{X}-task.md and execute.\"", "name": "worker-3{X}", "cwd": "{PROJECT_ROOT}", "env": {"OPENCODE_YOLO": "true"}}'
```

---

### Worker 4{X} - Simplify (Codex/GPT-5.2)

**Declaration:**
```
DECLARATION: I will spawn Worker 4{X} using Codex CLI with model gpt-5.2.
Role: Simplify - Code cleanup, optimization
```

**Command:**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/worker-4{X}-task.md and execute.\"", "name": "worker-4{X}", "cwd": "{PROJECT_ROOT}"}'
```

---

### Reviewer {X} (BigPickle)

**Declaration:**
```
DECLARATION: I will spawn Reviewer {X} using OpenCode CLI with model big-pickle.
Role: Deep code review, security analysis
```

**Command:**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/reviewer-{X}-task.md and execute.\"", "name": "reviewer-{X}", "cwd": "{PROJECT_ROOT}", "env": {"OPENCODE_YOLO": "true"}}'
```

---

### Tester {X} (Codex/GPT-5.2)

**Declaration:**
```
DECLARATION: I will spawn Tester {X} using Codex CLI with model gpt-5.2.
Role: Test execution, coverage verification
```

**Command:**
```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/tester-{X}-task.md and execute.\"", "name": "tester-{X}", "cwd": "{PROJECT_ROOT}"}'
```

---

## Execute Phases

### Phase 1: Break Domain into Tasks
1. Read context files above
2. Break your domain into 2-4 worker tasks
3. Write task files to `tasks/planner-{X}/` (use relative paths)

### Phase 2: Spawn Workers

**⏱️ TIMING EXPECTATIONS - BE PATIENT:**
| Worker | Model | Startup | Wait Before Checking |
|--------|-------|---------|---------------------|
| Worker 1{X} | Cursor/Opus | 30-60s | 2 min |
| Worker 2{X} | **Gemini** | **60-90s** | **3 min** |
| Worker 3{X} | Grok | 10s | 1 min |
| Worker 4{X} | **Codex** | **90-120s** | **5 min** |

**Gemini starts SLOW** - no activity for 2 minutes is NORMAL.
**Codex is SLOW THROUGHOUT** - not just startup. Log updates may be 2-3 min apart. This is deliberate, not stuck.

1. Spawn workers SEQUENTIALLY
2. **USE BASH TOOL** to execute SPAWN COMMANDS above
3. **WAIT** appropriate time before checking logs (see table)
4. Monitor worker logs - poll every 60s for Gemini/Codex

### Phase 3: Review Cycle
1. Wait for ALL workers to show COMPLETED (be patient with Codex)
2. Declare + Spawn Reviewer:
   ```
   DECLARATION: I will spawn Reviewer {X} using OpenCode CLI with model big-pickle.
   ```
3. Declare + Spawn Tester:
   ```
   DECLARATION: I will spawn Tester {X} using Codex CLI with model gpt-5.2.
   ```
4. Address any issues found

### Phase 4: Write Summary (MANDATORY)

**Before signaling PLANNER_COMPLETE, you MUST write a summary for future Planners.**

Write to `tasks/planner-{X}/summary.md`:

```markdown
# Planner {X} Summary

## Completed Tasks
- [x] Task 1: What was done
- [x] Task 2: What was done

## Files Created/Modified
| File | Action | Purpose |
|------|--------|---------|
| `path/to/file.py` | CREATED | What it does |
| `path/to/file.ts` | MODIFIED | What changed |

## Patterns Established
- Pattern 1: How we handle X in this codebase
- Pattern 2: Naming convention for Y

## API/Interface Contracts
- `POST /api/resource` - Request: {...}, Response: {...}
- `InterfaceName` - Key fields: {...}

## Discoveries for Future Planners
- Gotcha 1: Watch out for X
- Finding 1: The codebase does Y this way

## Files Needing Future Work
- `file.ts` - Why it needs more work
```

### Phase 5: Signal Completion
1. Log PLANNER_COMPLETE to planner-{X}.log
2. Log [STATUS] PLANNER_COMPLETE to coordination.log

## Begin
1. Log STARTED to planner-{X}.log
2. Read config.json FIRST - verify you understand the model assignments
3. Read completed Planner summaries (if any exist)
4. Read context files
5. Execute Phase 1
```

### Step 12: Create Logs

```bash
type nul > ".swarm/sessions/{SESSION_ID}/logs/queen.log"
type nul > ".swarm/sessions/{SESSION_ID}/logs/coordination.log"

# Pre-create ALL possible Planner logs
for letter in a b c d e f g h i j; do
  type nul > ".swarm/sessions/{SESSION_ID}/logs/planner-$letter.log"
done
```

### Step 13: Generate mprocs.yaml

**IMPORTANT**: Use absolute paths so mprocs can find files regardless of working directory.

```yaml
server: 127.0.0.1:{MPROCS_PORT}

procs:
  queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "Read {PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\queen-prompt.md and execute."]
    cwd: "{PROJECT_ROOT_WINDOWS}"
    env:
      GITHUB_ISSUES: "{ISSUE_LIST}"
      SWARM_MODE: "long-horizon"
      MAX_PLANNERS: "10"

  wave-status:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== WAVE STATUS ===' -ForegroundColor Magenta; Get-Content '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\state\\wave-status.md' -ErrorAction SilentlyContinue; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS}"

  coordination:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== COORDINATION ===' -ForegroundColor Green; Get-Content '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\logs\\coordination.log' -Tail 30 -ErrorAction SilentlyContinue; Start-Sleep 2 }"]
    cwd: "{PROJECT_ROOT_WINDOWS}"

  logs:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== ISSUES {ISSUE_LIST} LONG-HORIZON ===' -ForegroundColor Cyan; Get-Content '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\logs\\queen.log' -Tail 3 -ErrorAction SilentlyContinue; Get-ChildItem '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\logs\\planner-*.log' | ForEach-Object { $c = Get-Content $_.FullName -ErrorAction SilentlyContinue; if ($c) { Write-Host $_.BaseName -ForegroundColor Yellow; $c | Select-Object -Last 2 } }; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS}"
```

### Step 14: Launch mprocs

```bash
powershell -Command "Start-Process powershell -WorkingDirectory '{PROJECT_ROOT_WINDOWS}' -ArgumentList '-NoExit', '-Command', 'mprocs --config .swarm/mprocs.yaml'"
```

### Step 15: Output Status

```markdown
## Long-Horizon Swarm Launched!

**Session**: {SESSION_ID}
**Issues**: #{ISSUE_1}, #{ISSUE_2}, ...
**Branch**: {BRANCH_NAME}
**Mode**: LONG-HORIZON (Sequential Waves)
**Wave Strategy**: {--by-issue | --by-domain}
**Max Planners**: 10

### Issues Being Resolved

| # | Title | Valid Concerns |
|---|-------|----------------|
| {ISSUE_1} | {TITLE_1} | {COUNT} |
| {ISSUE_2} | {TITLE_2} | {COUNT} |

### Wave 1 Assignment

**--by-issue mode:**
| Planner | Issue | Concerns |
|---------|-------|----------|
| A | #{ISSUE_1} | {COUNT} |

**--by-domain mode:**
| Planner | Domain | From Issues | Concerns |
|---------|--------|-------------|----------|
| A | {DOMAIN_A} | #1, #2 | {COUNT} |
| B | {DOMAIN_B} | #1 | {COUNT} |

### Future Waves
**Remaining Issues/Concerns**: {COUNT}
**Estimated Waves**: {MIN}-{MAX}

### Architecture
```
Queen (Opus) - Sequential Wave Orchestrator
│
├── Wave 1: Issue #1 or Domain A+B
├── Wave 2: Issue #2 or Domain C
├── ... up to 10 Planners total
│
├── Integration Cycle (after all waves)
│
└── Code Quality Loop (up to 3 x 10-minute cycles)
    └── code-quality-{N} agents (Cursor CLI + Opus 4.5)
```

### Workflow
1. Queen spawns Planners in waves (1-2 at a time, sequential)
2. Each Planner spawns Workers, Reviewers, Testers
3. Queen adapts domain assignments between waves
4. Integration review cycle (after all waves)
5. Queen commits, creates PR
6. **Code Quality Loop** (up to 3 x 10-minute cycles):
   - Wait 10 minutes for external reviewers
   - Spawn code-quality-{N} agent (Cursor CLI + Opus 4.5)
   - Agent resolves comments, commits, pushes
   - Repeat until no new comments or max 3 cycles

### Commit Will Include
```
Resolves #{ISSUE_1}
Resolves #{ISSUE_2}
```

Watch the swarm tackle issues #{ISSUE_1}, #{ISSUE_2} wave by wave!
```

---

## Usage

```bash
# Single issue
/resolve-swarm-issue-long 42

# Multiple issues - by-issue (1 issue per wave, sequential)
/resolve-swarm-issue-long 42 43 44 --by-issue

# Multiple issues - by-domain (pool concerns, waves by dependency)
/resolve-swarm-issue-long 42 43 44 --by-domain

# URLs work too
/resolve-swarm-issue-long https://github.com/owner/repo/issues/42 43 44
```

## When to Use

| Scenario | Command |
|----------|---------|
| 2-4 related issues, quick parallel | `/resolve-swarm-issue` |
| 5+ issues OR very complex single issue | `/resolve-swarm-issue-long` |
| Sequential dependent issues | `/resolve-swarm-issue-long --by-issue` |
| Overlapping issues, shared code | `/resolve-swarm-issue-long --by-domain` |
| Uncertain scope, need discovery | `/resolve-swarm-issue-long` |
| Many small issues in one PR | `/resolve-swarm-issue --by-issue` |
