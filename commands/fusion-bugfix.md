---
description: F-Thread - Competing bug fix strategies in separate worktrees, judge picks most robust
argument-hint: "<bug-description-or-issue>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Fusion Bugfix - True F-Thread Bug Investigation Arena

Launch 3-5 workers (based on variance level) in **separate git worktrees** to investigate and fix the same bug independently. A Judge Queen evaluates which fix is most robust.

## Thread Type: F-Thread (Fusion)

This is a TRUE fusion thread for bug fixing:
- **Divergent worktrees**: Each worker investigates/fixes independently
- **Real artifacts**: Actual working fixes with tests
- **Root cause analysis**: Different theories tested
- **Best-of-N selection**: Most robust fix wins

## Arguments

- `<bug-description-or-issue>`: Bug description, error message, or GitHub issue number
- `--variance N`: Model diversity level (1-3, default: 1)
  - **Variance 1** (default): 3 workers (Opus, Gemini Pro, GPT-5.2)
  - **Variance 2**: 4 workers (+GLM 4.7 via OpenCode)

## Why F-Thread for Bugs?

When root cause is unclear, multiple approaches find the truth faster:
- Worker A: Assumes it's a logic error
- Worker B: Assumes it's a data/state issue
- Worker C: Assumes it's a race condition/async issue

One of them will find the real cause.

## Workflow

### Step 1-4: Prerequisites, Parse, Variables, Directories

(Same pattern as fusion-algorithm.md with appropriate substitutions)

**Variables** (in Step 3):
```
GEMINI_MODEL = "gemini-3-pro-preview"  # Bug investigation = code analysis, use Pro
```

### Step 5: Create Git Worktrees

```bash
# Worker A - Logic/Algorithm hypothesis
git worktree add "{WORKTREE_ROOT}/impl-a" -b fusion/{SESSION_ID}/impl-a

# Worker B - Data/State hypothesis
git worktree add "{WORKTREE_ROOT}/impl-b" -b fusion/{SESSION_ID}/impl-b

# Worker C - Async/Race condition hypothesis
git worktree add "{WORKTREE_ROOT}/impl-c" -b fusion/{SESSION_ID}/impl-c
```

### Step 6: Create tasks.json

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "F-Thread (Fusion)",
  "task_type": "fusion-bugfix",
  "bug": {
    "description": "{BUG_DESC}",
    "reproduction_steps": "",
    "error_message": ""
  },
  "base_branch": "{BASE_BRANCH}",
  "worktrees": {
    "impl-a": {
      "path": "{WORKTREE_ROOT}/impl-a",
      "branch": "fusion/{SESSION_ID}/impl-a",
      "worker": "worker-a",
      "provider": "claude-opus",
      "hypothesis": "logic-algorithm",
      "status": "pending"
    },
    "impl-b": {
      "path": "{WORKTREE_ROOT}/impl-b",
      "branch": "fusion/{SESSION_ID}/impl-b",
      "worker": "worker-b",
      "provider": "gemini-3-pro",
      "hypothesis": "data-state",
      "status": "pending"
    },
    "impl-c": {
      "path": "{WORKTREE_ROOT}/impl-c",
      "branch": "fusion/{SESSION_ID}/impl-c",
      "worker": "worker-c",
      "provider": "codex-gpt-5.2",
      "hypothesis": "async-race",
      "status": "pending"
    }
  },
  "evaluation": {
    "status": "pending",
    "criteria": ["fixes_bug", "root_cause_found", "regression_tests", "no_side_effects", "minimal_change"],
    "winner": null
  }
}
```

### Step 7: Create Judge Queen Prompt

```markdown
# Judge Queen - Bugfix Fusion Evaluator

You are the **Judge Queen** for an F-Thread bug investigation session.

## Your Mission

Three workers are investigating the same bug with different hypotheses. Your job is to:
1. Monitor their progress
2. Evaluate which fix actually solves the root cause
3. Pick the most robust, minimal fix

## Bug to Fix

**{BUG_DESC}**

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Thread Type**: F-Thread (Fusion) - Competing bug hypotheses

## Investigation Hypotheses

| Worker | Hypothesis | What They're Looking For |
|--------|------------|-------------------------|
| worker-a | Logic/Algorithm | Off-by-one, wrong condition, bad math |
| worker-b | Data/State | Invalid state, null values, stale data |
| worker-c | Async/Race | Timing issues, missing awaits, race conditions |

## Evaluation Criteria (MANDATORY ORDER)

1. **Fixes the Bug** (Required): Does it actually fix the reported issue?
2. **Root Cause Found**: Did they identify WHY it was broken?
3. **Regression Tests**: Did they add tests to prevent recurrence?
4. **No Side Effects**: Does the fix break anything else?
5. **Minimal Change**: Smallest correct fix wins

## Evaluation Process

For each worktree:

```bash
cd {WORKTREE_PATH}

# 1. Can we reproduce the bug on base?
git checkout {BASE_BRANCH}
# Run reproduction steps...

# 2. Is bug fixed on this branch?
git checkout fusion/{SESSION_ID}/impl-X
# Run reproduction steps...

# 3. Do all tests pass?
npm test

# 4. Check diff size
git diff {BASE_BRANCH}...HEAD --stat
```

## Generate Comparison Report

Write to `.hive/sessions/{SESSION_ID}/evaluation.md`:

```markdown
# Bugfix Fusion Evaluation

## Bug: {BUG_DESC}

## Root Cause Analysis

| Worker | Hypothesis | Root Cause Found? | Explanation |
|--------|------------|-------------------|-------------|
| A | Logic/Algorithm | Yes/No | [What they found] |
| B | Data/State | Yes/No | [What they found] |
| C | Async/Race | Yes/No | [What they found] |

## Fix Comparison

| Criteria | Fix A | Fix B | Fix C |
|----------|-------|-------|-------|
| Bug Fixed | Yes/No | Yes/No | Yes/No |
| Root Cause | Yes/No | Yes/No | Yes/No |
| Tests Added | X new | X new | X new |
| Tests Pass | X/Y | X/Y | X/Y |
| Lines Changed | +X/-Y | +X/-Y | +X/-Y |
| Side Effects | None/Some | None/Some | None/Some |

## Winning Fix

**{WINNER}**: {HYPOTHESIS}

### Why This Fix Wins
[Explanation of why this fix is best]

### Root Cause Summary
[One paragraph explaining the actual bug]

### Lessons Learned
[What to watch for in the future]
```

## Critical Rule

A fix that doesn't actually fix the bug gets score 0, regardless of how elegant it is.
```

### Step 8: Create Worker Prompts

**Worker A** (Logic/Algorithm Hypothesis):
```markdown
# Worker A - Logic/Algorithm Bug Hunter

## Your Mission
Investigate and fix **{BUG_DESC}** assuming it's a logic/algorithm error.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-a
- **Branch**: fusion/{SESSION_ID}/impl-a

## Your Hypothesis: Logic/Algorithm Error

Look for:
- Off-by-one errors
- Wrong comparison operators (< vs <=)
- Incorrect boolean logic
- Bad calculations
- Wrong loop bounds
- Missing edge case handling
- Incorrect sorting/ordering

## Investigation Protocol

1. **Reproduce the bug** - Confirm you can trigger it
2. **Add failing test** - Write a test that fails due to the bug
3. **Trace the logic** - Follow the code path
4. **Identify the error** - Find the exact line(s)
5. **Fix it** - Make minimal fix
6. **Verify** - Test passes, bug gone
7. **Check for similar issues** - Same pattern elsewhere?

## Deliverables

1. Failing test that demonstrates the bug
2. Minimal fix for the logic error
3. Document root cause in worker-a.log
4. Commit with message: "fix: {BUG_SLUG} - correct logic error in {location}"

## Begin

Announce: "Worker A investigating {BUG_DESC} - assuming logic/algorithm error"
```

**Worker B** (Data/State Hypothesis):
```markdown
# Worker B - Data/State Bug Hunter

## Your Mission
Investigate and fix **{BUG_DESC}** assuming it's a data/state issue.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-b
- **Branch**: fusion/{SESSION_ID}/impl-b

## Your Hypothesis: Data/State Issue

Look for:
- Null/undefined values
- Invalid state transitions
- Stale cached data
- Missing data validation
- Type coercion issues
- Uninitialized variables
- State mutation bugs

## Investigation Protocol

1. **Reproduce the bug** - Capture the state when it fails
2. **Add logging** - Log state at key points
3. **Trace the data** - Follow data flow
4. **Find invalid state** - Where does it go wrong?
5. **Fix it** - Add validation or correct state
6. **Add guards** - Prevent invalid state
7. **Write tests** - Test edge cases

## Deliverables

1. Test demonstrating the data/state issue
2. Fix with appropriate validation
3. Document root cause in worker-b.log
4. Commit with message: "fix: {BUG_SLUG} - handle invalid state in {location}"

## Begin

Announce: "Worker B investigating {BUG_DESC} - assuming data/state issue"
```

**Worker C** (Async/Race Condition Hypothesis):
```markdown
# Worker C - Async/Race Condition Bug Hunter

## Your Mission
Investigate and fix **{BUG_DESC}** assuming it's a race condition or async issue.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-c
- **Branch**: fusion/{SESSION_ID}/impl-c

## Your Hypothesis: Async/Race Condition

Look for:
- Missing await keywords
- Unhandled promise rejections
- Race conditions between operations
- Stale closure captures
- Event handler timing issues
- Concurrent state modification
- Missing locks/mutexes

## Investigation Protocol

1. **Reproduce intermittently** - Race conditions are flaky
2. **Add timing logs** - Log timestamps
3. **Identify concurrent ops** - What runs in parallel?
4. **Find the race** - What order causes failure?
5. **Fix it** - Add proper synchronization
6. **Stress test** - Run many times quickly
7. **Write flaky-resistant tests** - Test the fix holds

## Deliverables

1. Test that can trigger the race (or explains why it's hard)
2. Fix with proper async handling
3. Document timing sequence in worker-c.log
4. Commit with message: "fix: {BUG_SLUG} - resolve race condition in {location}"

## Begin

Announce: "Worker C investigating {BUG_DESC} - assuming async/race condition"
```

### Output Status

```markdown
## Fusion Bugfix Arena Launched!

**Thread Type**: F-Thread (True Fusion)
**Session**: {SESSION_ID}
**Bug**: {BUG_DESC}

### Competing Hypotheses

| Worker | Hypothesis | Looking For |
|--------|------------|-------------|
| Worker A | Logic/Algorithm | Off-by-one, wrong conditions |
| Worker B | Data/State | Null values, invalid state |
| Worker C | Async/Race | Missing await, timing issues |

### Why This Works

When root cause is unclear, parallel investigation finds the truth faster.
- If it's logic: Worker A finds it first
- If it's state: Worker B finds it first
- If it's async: Worker C finds it first

All three might find symptoms, but only one finds the ROOT CAUSE.

### Evaluation Priority

1. Does the fix actually work?
2. Did they find the real root cause?
3. Did they add regression tests?
4. Is the fix minimal and safe?

Watch three bug hunting strategies compete!
```

### Step 9: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# mprocs configuration for Fusion Bugfix session: {SESSION_ID}
# Gemini CLI: using latest installed version
procs:
  judge-queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the JUDGE QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "judge-queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      FUSION_TYPE: "bugfix"

  worker-a-opus:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are WORKER A. Read .hive/sessions/{SESSION_ID}/worker-a-prompt.md"]
    cwd: "{WORKTREE_ROOT}/impl-a"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "a"
      FUSION_APPROACH: "logic-algorithm"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-b-gemini:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER B. Read .hive/sessions/{SESSION_ID}/worker-b-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-b"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "b"
      FUSION_APPROACH: "data-state"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-c-gpt:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER C. Read .hive/sessions/{SESSION_ID}/worker-c-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-c"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "c"
      FUSION_APPROACH: "async-race"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 5 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

### Variance Workers (Optional)

**If VARIANCE >= 2, add Worker D (GLM 4.7 - Environment/Config hypothesis):**

```yaml
  worker-d-glm:
    cmd: ["powershell", "-NoProfile", "-Command", "cd '{WORKTREE_ROOT}/impl-d'; $env:OPENCODE_YOLO='true'; opencode run --format default -m opencode/glm-4.7-free 'You are WORKER D. Investigate assuming it is an environment/config issue. Look for missing env vars, wrong config values, path issues, permissions, and deployment differences.'"]
    cwd: "{WORKTREE_ROOT}/impl-d"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "d"
      FUSION_APPROACH: "environment-config"
```

Create additional worktrees for variance workers:
```bash
# If VARIANCE >= 2:
git worktree add "{WORKTREE_ROOT}/impl-d" -b fusion/{SESSION_ID}/impl-d
```
