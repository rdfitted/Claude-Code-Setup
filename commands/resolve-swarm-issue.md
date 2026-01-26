---
description: Resolve GitHub issue(s) using hierarchical Swarm with Planners orchestrating domain-specific mini-hives
argument-hint: "<issue-numbers>" [--by-issue | --by-domain]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
---

# Resolve Swarm Issue - Hierarchical Multi-Agent GitHub Issue Resolution

Launch a hierarchical swarm to resolve **one or more GitHub issues** in a single branch. Supports two planning modes:
- **By Issue**: Each Planner owns one issue (better focus, cleaner commits)
- **By Domain**: Pool concerns from all issues, assign by domain (better for overlapping work)

## Architecture

```
Queen (Opus 4.5) → Planners (Opus 4.5) → Workers (mixed models)
                        ↓
              All Planners run in PARALLEL
```

## Arguments

- `<issue-numbers>`: One or more issue numbers/URLs (space or comma separated)
  - Single: `42`
  - Multiple: `42 43 44` or `42,43,44`
  - URLs: `https://github.com/owner/repo/issues/42`
- `[--by-issue]`: One Planner per issue (default if issues are distinct)
- `[--by-domain]`: Pool concerns, assign Planners by domain (default if issues overlap)

---

## Step 1: Check Prerequisites

```bash
mprocs --version
gh --version
git rev-parse --is-inside-work-tree
```

If any fails, tell user what's missing - STOP.

## Step 2: Parse Issue Numbers

Extract all issue numbers from arguments:
- `42 43 44` → `[42, 43, 44]`
- `42,43,44` → `[42, 43, 44]`
- URLs → extract number from path

Store as `ISSUE_NUMBERS` array.

## Step 3: Fetch All Issue Details

For EACH issue, fetch details:

```bash
for issue in {ISSUE_NUMBERS}; do
  gh issue view $issue --json title,body,labels,state,comments
done
```

Store per-issue:
- `ISSUES[N].number`
- `ISSUES[N].title`
- `ISSUES[N].body`
- `ISSUES[N].labels`
- `ISSUES[N].concerns`

## Step 4: Generate Session Variables

```bash
TIMESTAMP=$(powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd-HHmmss'")
PROJECT_ROOT_WINDOWS=$(powershell -NoProfile -Command "(Get-Location).Path")
MPROCS_PORT=$((4000 + ${TIMESTAMP: -4}))
ISSUE_COUNT={length of ISSUE_NUMBERS}
# For branch name, use first issue or "multi" prefix
if [ $ISSUE_COUNT -eq 1 ]; then
  SESSION_ID="${TIMESTAMP}-resolve-swarm-${ISSUE_NUMBERS[0]}"
  BRANCH_NAME="issue/${ISSUE_NUMBERS[0]}-{slug}"
else
  SESSION_ID="${TIMESTAMP}-resolve-swarm-multi-${ISSUE_NUMBERS[0]}"
  BRANCH_NAME="issue/multi-${ISSUE_NUMBERS[0]}-{slug}"
fi
BASE_BRANCH=$(git branch --show-current)
```

## Step 5: Create Session Directory

```bash
mkdir -p ".swarm/sessions/{SESSION_ID}/docs"
mkdir -p ".swarm/sessions/{SESSION_ID}/phases"
mkdir -p ".swarm/sessions/{SESSION_ID}/state"
mkdir -p ".swarm/sessions/{SESSION_ID}/logs"

# Create Planner directories based on mode
# --by-issue: one per issue (planner-a = issue 1, planner-b = issue 2, etc.)
# --by-domain: based on domain analysis
for letter in a b c d; do
  mkdir -p ".swarm/sessions/{SESSION_ID}/tasks/planner-$letter"
done
```

## Step 6: Copy Templates + Generate Config

Copy from `~/.claude/swarm-templates/` to session folder, replacing placeholders:

**To root session folder:**
- Generate `config.json` from `config-template.json` (replace all placeholders)

**To `docs/`:**
- model-selection.md
- spawn-templates.md
- log-protocol.md
- **roles.md**
- **declaration-protocol.md** (MANDATORY - all agents must follow)
- **planner-cross-reference.md** (for context sharing between Planners)

**To `phases/`:** phase-1 through phase-6

**To `state/`:**
- Create `planner-status.md` (Queen updates this as Planners complete)

**CRITICAL FILES (agents MUST read these first):**
1. `config.json` - **AUTHORITATIVE** model assignments. DO NOT IMPROVISE.
2. `docs/roles.md` - Strict hierarchy
3. `docs/declaration-protocol.md` - Declare before execute

---

## PHASE 0: Concern Validation (Per Issue)

### Step 7: Spawn Validation Agents (3 per concern, per issue)

For EACH issue, for EACH concern, spawn 3 agents in parallel via Task tool.

**Scaffold validation by issue** - this keeps focus and makes results traceable:

**BigPickle:**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle "Search codebase for: {CONCERN}. Verdict: VALID (needs work) or MISTAKEN (already done)"
```

**GLM 4.7:**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Search codebase for: {CONCERN}. Verdict: VALID or MISTAKEN"
```

**Grok Code:**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "Search codebase for: {CONCERN}. Verdict: VALID or MISTAKEN"
```

### Step 8: Consensus (Per Issue)

For each issue:
- 3/3 agree "needs work" → VALID (high confidence)
- 2/3 agree "needs work" → VALID (medium confidence)
- 3/3 found solution → MISTAKEN
- 2/3 found solution → MISTAKEN
- Tie → Main Claude decides

Store validated concerns **grouped by issue**:
```
ISSUES[0].valid_concerns = [...]
ISSUES[1].valid_concerns = [...]
```

If ALL issues have no VALID concerns, report already addressed - STOP.

### Step 9: Learning Scout

```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Extract learnings from .ai-docs/ for issue #{ISSUE_NUMBER}: {ISSUE_TITLE}. Validated concerns: {LIST}. Output: ---SESSION-GUIDELINES-START--- ... ---SESSION-GUIDELINES-END---"
```

Write to `state/session-guidelines.md`

---

## PHASE 0.5: Planning Mode Decision + Domain Decomposition

### Step 10: Decide Planning Mode

**Analyze the issues and decide:**

| Condition | Mode | Rationale |
|-----------|------|-----------|
| Issues are distinct (different areas) | `--by-issue` | 1 Planner per issue, focused work |
| Issues overlap (same files/domains) | `--by-domain` | Pool concerns, avoid conflicts |
| User specified flag | Use that flag | User knows best |
| Single issue | `--by-domain` | Original behavior |

**Default heuristic**: If issues share >30% of likely files → `--by-domain`

### Step 11: Assign Planners

**Mode: --by-issue** (One Planner per Issue)

Write to `state/responsibility-matrix.md`:

```markdown
## Swarm Responsibility Matrix (By Issue)

### Issues
| # | Title | Valid Concerns |
|---|-------|----------------|
| {ISSUE_1} | {TITLE_1} | {COUNT} |
| {ISSUE_2} | {TITLE_2} | {COUNT} |

---

### Planner A - Issue #{ISSUE_1}
**Issue**: #{ISSUE_1} - {TITLE_1}
**Concerns**:
- {All validated concerns from issue 1}

### Planner B - Issue #{ISSUE_2}
**Issue**: #{ISSUE_2} - {TITLE_2}
**Concerns**:
- {All validated concerns from issue 2}

{...one Planner per issue, max 4...}

### Cross-Issue Concerns
{concerns that span multiple issues - Queen monitors}
```

**Mode: --by-domain** (Pool concerns, assign by domain)

Write to `state/responsibility-matrix.md`:

```markdown
## Swarm Responsibility Matrix (By Domain)

### Issues Being Resolved
| # | Title | Valid Concerns |
|---|-------|----------------|
| {ISSUE_1} | {TITLE_1} | {COUNT} |
| {ISSUE_2} | {TITLE_2} | {COUNT} |

### All Validated Concerns (Pooled)
{LIST_ALL_CONCERNS_WITH_SOURCE_ISSUE}

---

### Planner A - {DOMAIN_A}
**Domain**: {e.g., "Backend API and Database"}
**Concerns Assigned**:
- {Concern from issue #1}
- {Concern from issue #2}

### Planner B - {DOMAIN_B}
**Domain**: {e.g., "Frontend UI"}
**Concerns Assigned**:
- {Concern from issue #1}

### Cross-Cutting Concerns
{list}
```

### Step 12: File Scouts (2 per domain/issue)

Spawn GLM + Grok scouts per domain/issue → merge results.

Write to `state/file-ownership.md`

### Step 13: Write Context

Write to `state/context.md`:

```markdown
# Issue Context

## Issues Being Resolved
| # | Title | Labels | Valid Concerns |
|---|-------|--------|----------------|
| {ISSUE_1} | {TITLE_1} | {LABELS_1} | {COUNT} |
| {ISSUE_2} | {TITLE_2} | {LABELS_2} | {COUNT} |

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
- Mode: {--by-issue | --by-domain}
- Planners: {PLANNER_COUNT}
- Resolves: #{ISSUE_1}, #{ISSUE_2}, ...
```

---

## PHASE 1: Swarm Setup

### Step 14: Generate Queen Prompt (THIN but with INLINE spawn commands)

Write to `.swarm/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Queen - Issues {ISSUE_LIST}

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
- **READ config.json FIRST** - it defines all model assignments
- **DECLARE before EVERY spawn** (see declaration-protocol.md)
- Spawn **PLANNERS** (A through D) to handle domains/issues
- Write Planner prompt files before spawning
- Monitor Planner progress via logs
- Run integration cycle AFTER all Planners complete
- Commit and create PR

### YOU MUST NOT:
- ❌ **NEVER improvise model assignments** - use config.json
- ❌ **NEVER ask "what's the correct syntax?"** - it's in config.json
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
- **Planners**: {PLANNER_COUNT}
- **Branch**: {BRANCH_NAME}
- **Base**: {BASE_BRANCH}
- **Mode**: {--by-issue | --by-domain}
- **Resolves**: #{ISSUE_1}, #{ISSUE_2}, ...

## Read for Context (ABSOLUTE PATHS) - IN THIS ORDER

**CRITICAL - READ THESE FIRST (AUTHORITATIVE):**
1. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/config.json` - **AUTHORITATIVE MODEL CONFIG. DO NOT IMPROVISE.**
2. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/declaration-protocol.md` - **MANDATORY: Declare before every spawn**
3. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/roles.md` - Role hierarchy

**Context files:**
4. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/context.md` - All issues
5. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/responsibility-matrix.md` - Planner assignments
6. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/file-ownership.md` - File boundaries
7. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/session-guidelines.md` - Learnings
8. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/planner-status.md` - Track completions
9. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/planner-cross-reference.md` - Context sharing
10. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/log-protocol.md` - How to log

## Log Protocol
Log to queen.log:
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: {MESSAGE}\""
```

Log to coordination.log for Planner communication:
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

---

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

### Spawn Planner C (if needed)
```
DECLARATION: I will spawn Planner C using Claude CLI with model Opus.
Command: mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-c-prompt.md and execute.\"", "name": "planner-c", "cwd": "{PROJECT_ROOT}"}'
```

### Spawn Planner D (if needed)
```
DECLARATION: I will spawn Planner D using Claude CLI with model Opus.
Command: mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read {PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/planner-d-prompt.md and execute.\"", "name": "planner-d", "cwd": "{PROJECT_ROOT}"}'
```

---

## PHASE 4+ SPAWN COMMANDS (Integration Team - After All Planners)

**ONLY use these AFTER all Planners have signaled PLANNER_COMPLETE.**

### Spawn Integration Reviewer
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
1. Read `state/responsibility-matrix.md` for domain assignments
2. Write `planner-{X}-prompt.md` files for each Planner (NOT worker tasks)
3. **USE BASH TOOL** to execute TIER 1 SPAWN COMMANDS above
4. Log progress to queen.log

### Phase 2: Monitor Planners
- Watch `logs/planner-*.log` for PLANNER_COMPLETE
- Use `logs/coordination.log` to communicate with Planners
- Wait until ALL Planners signal PLANNER_COMPLETE

### Phase 3: Integration Review
- See `phases/phase-4-integration.md` for review cycle
- Use PHASE 4+ SPAWN COMMANDS for integration team

### Phase 4: Commit and PR
- See `phases/phase-5-commit.md`
- Commit message format:
```
fix: resolve issues #{ISSUE_1}, #{ISSUE_2}

{summary}

Resolves #{ISSUE_1}
Resolves #{ISSUE_2}

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

### Phase 5: Code Quality Loop (MANDATORY)

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
| Run integration cycle | ✅ YES | ❌ NO | ❌ NO |
| Commit code | ✅ YES | ❌ NO | ❌ NO |
| Push PR | ✅ YES | ❌ NO | ❌ NO |

## Begin
1. Log STARTED to queen.log
2. Create branch: `git checkout -b {BRANCH_NAME}`
3. Read context files (especially `docs/roles.md`)
4. Write **Planner prompts** (NOT worker tasks)
5. Spawn **Planners** (NOT workers)
```

### Step 15: Generate Planner Prompts (THIN with absolute paths + inlined spawn commands)

For each Planner, write to `.swarm/sessions/{SESSION_ID}/planner-{X}-prompt.md`:

**Mode: --by-issue** (Planner owns one issue)

```markdown
# Planner {X} - Issue #{ISSUE_N}

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
- Break your issue into **Worker tasks BY ROLE** (not by feature)
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
- ❌ **NEVER work outside your assigned issue** - respect file ownership
- ❌ **NEVER implement code yourself** - delegate to Workers
- ❌ **NEVER signal PLANNER_COMPLETE until review cycle done**

If a concern is outside your issue, log it to coordination.log for Queen.

---

## Session
- **ID**: {SESSION_ID}
- **Project Root**: {PROJECT_ROOT}
- **Log**: logs/planner-{X}.log (relative from project root)
- **Tasks**: tasks/planner-{X}/ (relative from project root)
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}
- **Your Issue**: #{ISSUE_N} - {ISSUE_TITLE}

## Read for Context (ABSOLUTE PATHS) - IN THIS ORDER

**CRITICAL - READ THESE FIRST (AUTHORITATIVE):**
1. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/config.json` - **AUTHORITATIVE MODEL CONFIG. USE EXACT MODELS. DO NOT IMPROVISE.**
2. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/declaration-protocol.md` - **MANDATORY: Declare before every spawn**
3. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/roles.md` - Role hierarchy

**Cross-Reference (read completed Planners' summaries):**
4. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/planner-status.md` - Check which Planners are done
5. If others COMPLETED, read their `tasks/planner-{X}/summary.md` to inherit patterns

**Context files:**
6. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/context.md` - Find YOUR issue
7. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/responsibility-matrix.md` - Your assignment
8. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/file-ownership.md` - Your files
9. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/session-guidelines.md` - Learnings
10. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/log-protocol.md` - How to log

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

Before executing ANY spawn command, declare:

```
DECLARATION: I will spawn Worker {N}{X} using {CLI} with model {MODEL}.
Role: {ROLE} - {SPECIALTY}
Command: [paste exact command]
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

### Phase 1: Break Issue into Tasks
1. Read config.json FIRST - verify you understand model assignments
2. Read completed Planner summaries (if any exist) to inherit patterns
3. Break issue #{ISSUE_N} into 2-4 worker tasks **BY ROLE not by feature**:
   - Worker 1 = ALL backend Python work
   - Worker 2 = ALL frontend TypeScript/React work
   - Worker 3 = Coherence/consistency checks
   - Worker 4 = Cleanup/simplification
4. Write task files to `tasks/planner-{X}/` (use relative paths)

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

1. **DECLARE** before each spawn (see declaration-protocol.md)
2. Spawn workers SEQUENTIALLY (wait for dependencies)
3. **USE BASH TOOL** to execute SPAWN COMMANDS above
4. **WAIT** appropriate time before checking logs (see table)
5. Monitor worker logs - poll every 60s for Gemini/Codex

### Phase 3: Review Cycle
1. Wait for ALL workers to show COMPLETED (be patient with Codex)
2. Declare + Spawn Reviewer
3. Declare + Spawn Tester
4. Address any issues found

### Phase 4: Write Summary (MANDATORY)

**Before signaling PLANNER_COMPLETE, write a summary for other Planners.**

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

## Patterns Established
- Pattern 1: How we handle X

## Discoveries for Other Planners
- Gotcha 1: Watch out for X
```

### Phase 5: Signal Completion
1. Log PLANNER_COMPLETE to planner-{X}.log
2. Log [STATUS] PLANNER_COMPLETE to coordination.log
4. Log PLANNER_COMPLETE to coordination.log

## Focus
You own Issue #{ISSUE_N}. All work addresses that issue's concerns.

## Begin
1. Log STARTED to planner-{X}.log
2. Read context files
3. Execute Phase 1
```

**Mode: --by-domain** (Planner owns a domain across issues)

```markdown
# Planner {X} - {DOMAIN}

---

## ⚠️ ROLE BOUNDARIES - READ THIS FIRST ⚠️

You are a **PLANNER** - middle-tier orchestrator in a 3-tier hierarchy:

```
TIER 1: QUEEN           → Spawned you, monitors your progress
TIER 2: PLANNER (you)   → Spawn Workers, Reviewers, Testers
TIER 3: WORKERS         → Execute implementation tasks
```

### YOU MUST:
- Break your domain into **Worker tasks** (2-4 tasks)
- Write task files to `tasks/planner-{X}/`
- Spawn **Workers** to execute those tasks
- Spawn **Reviewer** and **Tester** after Workers complete
- Signal **PLANNER_COMPLETE** to Queen when done

### YOU MUST NOT:
- ❌ **NEVER spawn other Planners** - only Queen does that
- ❌ **NEVER work outside your assigned domain** - respect file ownership
- ❌ **NEVER implement code yourself** - delegate to Workers
- ❌ **NEVER signal PLANNER_COMPLETE until review cycle done**

If a concern is outside your domain, log it to coordination.log for Queen.

---

## Session
- **ID**: {SESSION_ID}
- **Project Root**: {PROJECT_ROOT}
- **Log**: logs/planner-{X}.log
- **Tasks**: tasks/planner-{X}/
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}

## Read for Context (ABSOLUTE PATHS)
1. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/roles.md` - **READ FIRST: Role hierarchy**
2. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/context.md`
3. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/responsibility-matrix.md` - Your domain
4. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/file-ownership.md` - Your files
5. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/state/session-guidelines.md`
6. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/docs/log-protocol.md`

## Log Protocol
```bash
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/planner-{X}.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] PLANNER-{X}: {MESSAGE}\""
```

---

## TIER 2 SPAWN COMMANDS (Workers, Reviewer, Tester)

**These are your spawn commands. Execute via Bash tool.**

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

### Reviewer {X}
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
2. Break domain into 2-4 worker tasks
3. Write task files to `tasks/planner-{X}/` (relative paths)

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
2. Spawn Reviewer + Tester
3. Address issues
4. Log PLANNER_COMPLETE

## Begin
1. Log STARTED
2. Read context files
3. Execute Phase 1
```

### Step 16: Create Logs + tasks.json

```bash
type nul > ".swarm/sessions/{SESSION_ID}/logs/queen.log"
type nul > ".swarm/sessions/{SESSION_ID}/logs/coordination.log"
type nul > ".swarm/sessions/{SESSION_ID}/logs/planner-a.log"
type nul > ".swarm/sessions/{SESSION_ID}/logs/planner-b.log"
```

Write `state/tasks.json` with session metadata.

### Step 17: Generate mprocs.yaml

**IMPORTANT**: Use absolute paths for the Queen prompt so mprocs can find it regardless of working directory.

```yaml
server: 127.0.0.1:{MPROCS_PORT}

procs:
  queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "Read {PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\queen-prompt.md and execute."]
    cwd: "{PROJECT_ROOT_WINDOWS}"
    env:
      GITHUB_ISSUES: "{ISSUE_LIST}"

  coordination:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== ISSUES {ISSUE_LIST} COORDINATION ===' -ForegroundColor Green; Get-Content '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\logs\\coordination.log' -Tail 25 -ErrorAction SilentlyContinue; Start-Sleep 2 }"]
    cwd: "{PROJECT_ROOT_WINDOWS}"

  logs:
    cmd: ["powershell", "-NoProfile", "-Command", "while ($true) { cls; Write-Host '=== ISSUES {ISSUE_LIST} LOGS ===' -ForegroundColor Cyan; Get-Content '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\logs\\queen.log' -Tail 3 -ErrorAction SilentlyContinue; Get-ChildItem '{PROJECT_ROOT_WINDOWS}\\.swarm\\sessions\\{SESSION_ID}\\logs\\planner-*.log' | ForEach-Object { Write-Host $_.BaseName -ForegroundColor Yellow; Get-Content $_.FullName -Tail 2 -ErrorAction SilentlyContinue }; Start-Sleep 3 }"]
    cwd: "{PROJECT_ROOT_WINDOWS}"
```

### Step 18: Launch mprocs

```bash
powershell -Command "Start-Process powershell -WorkingDirectory '{PROJECT_ROOT_WINDOWS}' -ArgumentList '-NoExit', '-Command', 'mprocs --config .swarm/mprocs.yaml'"
```

### Step 19: Output Status

```markdown
## Swarm Issue Resolver Launched!

**Session**: {SESSION_ID}
**Issues**: #{ISSUE_1}, #{ISSUE_2}, ...
**Branch**: {BRANCH_NAME}
**Mode**: {--by-issue | --by-domain}
**Planners**: {PLANNER_COUNT}

### Issues Being Resolved

| # | Title | Valid Concerns |
|---|-------|----------------|
| {ISSUE_1} | {TITLE_1} | {COUNT} |
| {ISSUE_2} | {TITLE_2} | {COUNT} |

### Planner Assignment

**Mode: --by-issue**
| Planner | Issue | Concerns |
|---------|-------|----------|
| A | #{ISSUE_1} | {COUNT} |
| B | #{ISSUE_2} | {COUNT} |

**Mode: --by-domain**
| Planner | Domain | Issues | Concerns |
|---------|--------|--------|----------|
| A | {DOMAIN_A} | #1, #2 | {COUNT} |
| B | {DOMAIN_B} | #1 | {COUNT} |

### Architecture
```
Queen (Opus) - Orchestration, Integration, PR
├── Planner A → Workers, Reviewer, Tester
├── Planner B → Workers, Reviewer, Tester
└── Code Quality Loop (up to 3 x 10-minute cycles)
    └── code-quality-{N} agents (Cursor CLI + Opus 4.5)
```

### Key Files
- `state/context.md` - All issue details
- `state/responsibility-matrix.md` - Planner assignments
- `state/file-ownership.md` - File boundaries
- `logs/coordination.log` - Queen ↔ Planner communication

### Workflow
1. Queen spawns Planners (parallel)
2. Planners spawn Workers, Reviewers, Testers
3. Integration review cycle
4. Queen commits, creates PR
5. **Code Quality Loop** (up to 3 x 10-minute cycles):
   - Wait 10 minutes for external reviewers
   - Spawn code-quality-{N} agent (Cursor CLI + Opus 4.5)
   - Agent resolves comments, commits, pushes
   - Repeat until no new comments or max 3 cycles

### Commit Will Include
```
Resolves #{ISSUE_1}
Resolves #{ISSUE_2}
```

Watch the swarm resolve issues #{ISSUE_1}, #{ISSUE_2}!
```

---

## Usage

```bash
# Single issue
/resolve-swarm-issue 42

# Multiple issues (by-issue mode - 1 Planner per issue)
/resolve-swarm-issue 42 43 44 --by-issue

# Multiple issues (by-domain mode - pool concerns)
/resolve-swarm-issue 42 43 44 --by-domain

# URLs work too
/resolve-swarm-issue https://github.com/owner/repo/issues/42 43
```
