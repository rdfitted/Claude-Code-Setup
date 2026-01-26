---
description: F-Thread - Competing refactoring approaches in separate worktrees, judge picks safest/cleanest
argument-hint: "<file-or-module-to-refactor>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Fusion Refactor - True F-Thread Refactoring Arena

Launch 3-5 workers (based on variance level) in **separate git worktrees** to refactor the same code independently. A Judge Queen evaluates all approaches and picks the safest/cleanest.

## Thread Type: F-Thread (Fusion)

This is a TRUE fusion thread for high-risk refactoring:
- **Divergent worktrees**: Each worker refactors in isolated branch
- **Real artifacts**: Actual refactored code, not just plans
- **Comparative analysis**: Judge validates tests, reviews changes
- **Best-of-N selection**: Safest, cleanest approach wins

## Arguments

- `<file-or-module-to-refactor>`: Path to file/module or description of what to refactor
- `--variance N`: Model diversity level (1-3, default: 1)
  - **Variance 1** (default): 3 workers (Opus, Gemini Pro, GPT-5.2)
  - **Variance 2**: 4 workers (+GLM 4.7 via OpenCode)

## Workflow

### Step 1: Check Prerequisites

```bash
git --version
mprocs --version
git rev-parse --is-inside-work-tree
```

If not a git repo or mprocs not installed, STOP.

### Step 2: Parse Input & Identify Target

Extract:
- `REFACTOR_TARGET`: What to refactor
- `REFACTOR_SLUG`: Kebab-case version for branches

Read the target file(s) to understand current state.

### Step 3: Generate Session Variables

```bash
powershell -Command "Get-Date -Format 'yyyyMMdd-HHmmss'"
git branch --show-current
pwd
```

```
TIMESTAMP = result of Get-Date
SESSION_ID = {TIMESTAMP}-fusion-refactor
BASE_BRANCH = current branch
PROJECT_ROOT = current working directory
WORKTREE_ROOT = {PROJECT_ROOT}/../.fusion-worktrees/{SESSION_ID}
GEMINI_MODEL = "gemini-3-pro-preview"  # Refactoring = code generation, use Pro
VARIANCE = parsed from --variance argument (default: 1, max: 3)
```

### Step 4: Create Directories

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
mkdir -p "{WORKTREE_ROOT}"
```

### Step 5: Create Git Worktrees

Create isolated worktrees based on variance level:

```bash
# Always create (Variance 1+):
# Worker A - Conservative incremental refactoring
git worktree add "{WORKTREE_ROOT}/impl-a" -b fusion/{SESSION_ID}/impl-a

# Worker B - Aggressive pattern-based refactoring
git worktree add "{WORKTREE_ROOT}/impl-b" -b fusion/{SESSION_ID}/impl-b

# Worker C - Complete rewrite approach
git worktree add "{WORKTREE_ROOT}/impl-c" -b fusion/{SESSION_ID}/impl-c

# If VARIANCE >= 2:
# Worker D - Defensive/Safety-first refactoring (GLM 4.7)
git worktree add "{WORKTREE_ROOT}/impl-d" -b fusion/{SESSION_ID}/impl-d

```

### Step 6: Create tasks.json

Write to `.hive/sessions/{SESSION_ID}/tasks.json`:

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "F-Thread (Fusion)",
  "task_type": "fusion-refactor",
  "variance": {VARIANCE},
  "refactor": {
    "target": "{REFACTOR_TARGET}",
    "slug": "{REFACTOR_SLUG}"
  },
  "base_branch": "{BASE_BRANCH}",
  "worktrees": {
    "impl-a": {
      "path": "{WORKTREE_ROOT}/impl-a",
      "branch": "fusion/{SESSION_ID}/impl-a",
      "worker": "worker-a",
      "provider": "claude-opus",
      "approach": "conservative-incremental",
      "status": "pending"
    },
    "impl-b": {
      "path": "{WORKTREE_ROOT}/impl-b",
      "branch": "fusion/{SESSION_ID}/impl-b",
      "worker": "worker-b",
      "provider": "gemini-3-pro",
      "approach": "aggressive-patterns",
      "status": "pending"
    },
    "impl-c": {
      "path": "{WORKTREE_ROOT}/impl-c",
      "branch": "fusion/{SESSION_ID}/impl-c",
      "worker": "worker-c",
      "provider": "codex-gpt-5.2",
      "approach": "complete-rewrite",
      "status": "pending"
    }
    // If VARIANCE >= 2, add:
    ,"impl-d": {
      "path": "{WORKTREE_ROOT}/impl-d",
      "branch": "fusion/{SESSION_ID}/impl-d",
      "worker": "worker-d",
      "provider": "opencode-glm-4.7",
      "approach": "defensive-safety",
      "status": "pending"
    }
  },
  "evaluation": {
    "status": "pending",
    "criteria": ["tests_pass", "breaking_changes", "code_reduction", "readability", "risk_level"],
    "winner": null
  }
}
```

### Step 7: Create Judge Queen Prompt

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Judge Queen - Refactoring Fusion Evaluator

You are the **Judge Queen** for an F-Thread refactoring fusion session.

## Your Mission

Three workers are refactoring the same code in **separate git worktrees** with different strategies. Your job is to:
1. Monitor their progress
2. Evaluate all three approaches when complete
3. Pick the SAFEST and cleanest approach

## Refactoring Target

**{REFACTOR_TARGET}**

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Base Branch**: {BASE_BRANCH}
- **Thread Type**: F-Thread (Fusion) - Competing refactoring strategies

## Worktrees (Isolated Approaches)

**Variance Level**: {VARIANCE}

| Worker | Worktree | Approach | Variance |
|--------|----------|----------|----------|
| worker-a | {WORKTREE_ROOT}/impl-a | Conservative/Incremental (Opus) | 1+ |
| worker-b | {WORKTREE_ROOT}/impl-b | Aggressive/Pattern-based (Gemini) | 1+ |
| worker-c | {WORKTREE_ROOT}/impl-c | Complete Rewrite (GPT) | 1+ |
| worker-d | {WORKTREE_ROOT}/impl-d | Defensive/Safety-first (GLM 4.7) | 2+ |

## Evaluation Criteria (SAFETY FIRST)

When all workers complete, evaluate each on:

1. **Tests Pass** (Critical): All existing tests must pass
2. **Breaking Changes**: Any API/interface changes? Lower is better
3. **Code Reduction**: Lines removed/simplified
4. **Readability**: Is the result clearer?
5. **Risk Level**: How risky is this change to deploy?

### Risk Assessment Matrix

| Risk Factor | Low | Medium | High |
|-------------|-----|--------|------|
| Tests | All pass | Some skipped | Some fail |
| API changes | None | Deprecated | Breaking |
| Scope | Few files | Module | Cross-cutting |
| Reversibility | Easy rollback | Needs planning | Difficult |

## Evaluation Commands

For each worktree:

```bash
# Check tests
cd {WORKTREE_PATH}
npm test  # or project-specific test command

# Diff against base
git diff {BASE_BRANCH}...HEAD --stat

# Count changes
git diff {BASE_BRANCH}...HEAD --numstat
```

## Generate Comparison Report

Write to `.hive/sessions/{SESSION_ID}/evaluation.md`:

```markdown
# Refactoring Fusion Evaluation

## Target: {REFACTOR_TARGET}

## Safety Matrix

**Variance {VARIANCE}**: {3|4|5} approaches to evaluate

| Criteria | Impl A (Conservative) | Impl B (Aggressive) | Impl C (Rewrite) | Impl D (Defensive)* | Impl E (Cross-Paradigm)** |
|----------|----------------------|---------------------|------------------|---------------------|---------------------------|
| Tests Pass | X/Y | X/Y | X/Y | X/Y | X/Y |
| Breaking Changes | None/Some/Many | None/Some/Many | None/Some/Many | None/Some/Many | None/Some/Many |
| Files Changed | X | X | X | X | X |
| Lines +/- | +X/-Y | +X/-Y | +X/-Y | +X/-Y | +X/-Y |
| Risk Level | Low/Med/High | Low/Med/High | Low/Med/High | Low/Med/High | Low/Med/High |

*Variance 2+ only | **Variance 3 only

## Approach Summaries

### Approach A: Conservative/Incremental
[Description of changes, patterns used, trade-offs]

### Approach B: Aggressive/Pattern-based
[Description of changes, patterns used, trade-offs]

### Approach C: Complete Rewrite
[Description of changes, patterns used, trade-offs]

### Approach D: Defensive/Safety-first [Variance 2+]
[Description of changes, patterns used, trade-offs]

### Approach E: Cross-Paradigm Synthesis [Variance 3]
[Description of changes, patterns used, trade-offs]

## Recommendation

**Winner**: {APPROACH}

**Reasoning**: [Why this is the safest choice]

**Deployment Strategy**:
- [ ] Safe to merge directly
- [ ] Needs feature flag
- [ ] Requires staged rollout
- [ ] Needs more testing first
```

## Begin

Announce: "Judge Queen initialized for refactoring fusion. Monitoring three approaches to refactor: {REFACTOR_TARGET}"
```

### Step 8: Create Worker Prompts

**Worker A** (Conservative/Incremental):
```markdown
# Worker A - Conservative Incremental Refactoring

## Your Mission
Refactor **{REFACTOR_TARGET}** using CONSERVATIVE, incremental changes.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-a
- **Branch**: fusion/{SESSION_ID}/impl-a

## Your Approach: Conservative/Incremental

- Make the SMALLEST changes possible
- One logical change per commit
- Preserve all existing APIs
- Add deprecation warnings, don't remove
- If in doubt, don't change it
- Document every change

## Protocol

1. `cd "{WORKTREE_ROOT}/impl-a"`
2. Analyze the current code
3. Plan incremental improvements
4. Make small, safe changes
5. Run tests after EVERY change
6. Commit frequently with clear messages
7. Log progress to worker-a.log
8. Update tasks.json when complete
```

**Worker B** (Aggressive/Pattern-based):
```markdown
# Worker B - Aggressive Pattern-Based Refactoring

## Your Mission
Refactor **{REFACTOR_TARGET}** using modern patterns and best practices.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-b
- **Branch**: fusion/{SESSION_ID}/impl-b

## Your Approach: Aggressive/Pattern-based

- Apply known refactoring patterns
- Extract abstractions where beneficial
- Use modern language features
- Consolidate duplicated code
- Improve type safety
- Be willing to change interfaces

## Protocol

1. `cd "{WORKTREE_ROOT}/impl-b"`
2. Identify applicable patterns
3. Apply refactoring techniques
4. Update tests as needed
5. Ensure all tests pass
6. Commit with pattern names in messages
7. Log progress to worker-b.log
8. Update tasks.json when complete
```

**Worker C** (Complete Rewrite):
```markdown
# Worker C - Complete Rewrite Approach

## Your Mission
Refactor **{REFACTOR_TARGET}** by rewriting from scratch with the same behavior.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-c
- **Branch**: fusion/{SESSION_ID}/impl-c

## Your Approach: Complete Rewrite

- Start fresh with same requirements
- Design optimal architecture
- Write tests first (TDD)
- Implement from clean slate
- Match existing API exactly
- No legacy constraints

## Protocol

1. `cd "{WORKTREE_ROOT}/impl-c"`
2. Document existing behavior/API
3. Write tests for expected behavior
4. Implement from scratch
5. Ensure all tests pass
6. Compare behavior with original
7. Log progress to worker-c.log
8. Update tasks.json when complete
```

**Worker D** (Defensive/Safety-first) - **Variance 2+ only**:
```markdown
# Worker D - Defensive Safety-First Refactoring

## Your Mission
Refactor **{REFACTOR_TARGET}** with extreme focus on safety and defensive programming.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-d
- **Branch**: fusion/{SESSION_ID}/impl-d

## Your Approach: Defensive/Safety-first

- Add comprehensive error handling
- Validate all inputs thoroughly
- Add defensive null checks
- Preserve backwards compatibility
- Add migration paths
- Extensive logging for debugging

## Protocol

1. `cd "{WORKTREE_ROOT}/impl-d"`
2. Audit current code for safety gaps
3. Add error boundaries and handlers
4. Refactor with safety guards
5. Add regression tests
6. Ensure all tests pass
7. Log progress to worker-d.log
8. Update tasks.json when complete
```

**Worker E** (Cross-Paradigm Synthesis) - **Variance 3 only**:
```markdown
# Worker E - Cross-Paradigm Synthesis Refactoring

## Your Mission
Refactor **{REFACTOR_TARGET}** by synthesizing best practices from multiple paradigms.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-e
- **Branch**: fusion/{SESSION_ID}/impl-e

## Your Approach: Cross-Paradigm Synthesis

- Blend functional and OOP patterns
- Use Rust-style ownership ideas
- Apply Go-style simplicity
- Consider reactive patterns
- Multi-language best practices

## Protocol

1. `cd "{WORKTREE_ROOT}/impl-e"`
2. Analyze paradigms applicable to the code
3. Design hybrid approach
4. Implement cross-paradigm solution
5. Ensure all tests pass
6. Document paradigm choices
7. Log progress to worker-e.log
8. Update tasks.json when complete
```

### Step 9: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# mprocs configuration for Fusion Refactor session: {SESSION_ID}
# Variance Level: {VARIANCE} ({3|4|5} workers)
procs:
  judge-queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the JUDGE QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "judge-queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      FUSION_TYPE: "refactor"
      VARIANCE: "{VARIANCE}"

  # === Always included (Variance 1+) ===
  worker-a-opus:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are WORKER A. Read .hive/sessions/{SESSION_ID}/worker-a-prompt.md"]
    cwd: "{WORKTREE_ROOT}/impl-a"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "a"
      FUSION_APPROACH: "conservative-incremental"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-b-gemini:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER B. Read .hive/sessions/{SESSION_ID}/worker-b-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-b"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "b"
      FUSION_APPROACH: "aggressive-patterns"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-c-gpt:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER C. Read .hive/sessions/{SESSION_ID}/worker-c-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-c"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "c"
      FUSION_APPROACH: "complete-rewrite"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  # === Variance 2+ only ===
  worker-d-glm:
    cmd: ["powershell", "-NoProfile", "-Command", "cd '{WORKTREE_ROOT}/impl-d'; $env:OPENCODE_YOLO='true'; opencode run --format default -m opencode/glm-4.7-free 'You are WORKER D. Read .hive/sessions/{SESSION_ID}/worker-d-prompt.md and refactor with a defensive/safety-first approach.'"]
    cwd: "{WORKTREE_ROOT}/impl-d"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "d"
      FUSION_APPROACH: "defensive-safety"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 5 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

**Note**: Only include worker-d-glm if VARIANCE >= 2.

### Step 10-12: Create logs, launch mprocs, output status

(Same pattern as fusion-algorithm.md)

### Output Status

```markdown
## Fusion Refactor Arena Launched!

**Thread Type**: F-Thread (True Fusion)
**Session**: {SESSION_ID}
**Target**: {REFACTOR_TARGET}
**Variance Level**: {VARIANCE} ({3|4|5} competing approaches)

### Competing Strategies

| Worker | Approach | Risk Level | Speed | Variance |
|--------|----------|------------|-------|----------|
| Worker A | Conservative/Incremental | Low | Slow | 1+ |
| Worker B | Aggressive/Patterns | Medium | Medium | 1+ |
| Worker C | Complete Rewrite | High | Variable | 1+ |
| Worker D | Defensive/Safety-first | Low | Medium | 2+ |
| Worker E | Cross-Paradigm Synthesis | Medium | Variable | 3 |

### Team

| Pane | Provider | Focus | Variance |
|------|----------|-------|----------|
| judge-queen | Opus 4.5 | Evaluates all approaches | 1+ |
| worker-a | Opus 4.5 | Conservative, safe changes | 1+ |
| worker-b | Gemini 3 Pro | Aggressive pattern refactoring | 1+ |
| worker-c | GPT-5.2 | Complete rewrite from scratch | 1+ |
| worker-d | GLM 4.7 (OpenCode) | Defensive, safety-first | 2+ |

### Safety Evaluation

The Judge Queen will evaluate based on:
1. **Tests passing** (mandatory)
2. **Breaking changes** (fewer is better)
3. **Risk level** (lower is better)
4. **Code improvement** (cleaner is better)

Best approach for production: Usually A, B, or D.
Most learning potential: Often C or E.

Watch {3|4|5} refactoring strategies compete!
```
