---
description: F-Thread - Competing algorithm implementations in separate worktrees, judge picks best
argument-hint: "<algorithm-description>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Fusion Algorithm - True F-Thread Implementation Arena

Launch 3-5 workers (based on variance level) in **separate git worktrees** to implement the same algorithm independently. A Judge Queen evaluates all implementations and picks the winner.

## Thread Type: F-Thread (Fusion)

This is a TRUE fusion thread:
- **Divergent worktrees**: Each worker implements in isolated branch
- **Real artifacts**: Actual runnable code, not just plans
- **Comparative analysis**: Judge runs tests, benchmarks, reviews code
- **Best-of-N selection**: Winner selected or best elements merged

## Arguments

- `<algorithm-description>`: What algorithm to implement (e.g., "LRU cache", "rate limiter", "pagination helper")
- `--variance N`: Model diversity level (1-3, default: 1)
  - **Variance 1** (default): 3 workers (Sonnet, Gemini Pro, GPT-5.2)
  - **Variance 2**: 4 workers (+GLM 4.7 via OpenCode)

## Workflow

### Step 1: Check Prerequisites

```bash
git --version
mprocs --version
```

Verify we're in a git repository:
```bash
git rev-parse --is-inside-work-tree
```

If not a git repo or mprocs not installed, tell user and STOP.

### Step 2: Parse Input

Extract from user input:
- `ALGORITHM_DESC`: The algorithm to implement
- `ALGORITHM_SLUG`: Kebab-case version for branch names

### Step 3: Generate Session Variables

```bash
# Get timestamp
powershell -Command "Get-Date -Format 'yyyyMMdd-HHmmss'"

# Get current branch (base for worktrees)
git branch --show-current

# Get current working directory in Windows format
powershell -NoProfile -Command "(Get-Location).Path"
```

Set variables:
```
TIMESTAMP = result of Get-Date command
SESSION_ID = {TIMESTAMP}-fusion-algorithm
BASE_BRANCH = current branch name
PROJECT_ROOT_WINDOWS = PowerShell path (e.g., D:\Code Projects\MyProject)
WORKTREE_ROOT = {PROJECT_ROOT_WINDOWS}\..\..\.fusion-worktrees\{SESSION_ID}
GEMINI_MODEL = "gemini-3-pro-preview"  # Algorithm implementation = code generation, use Pro
VARIANCE = parsed from --variance argument (default: 1, max: 3)
```

**CRITICAL - Path Format for mprocs.yaml:**
- mprocs on Windows REQUIRES Windows-style paths with escaped backslashes
- Use `PROJECT_ROOT_WINDOWS` (from PowerShell) for the `cwd` field
- Format in YAML: `"D:\\Code Projects\\MyProject"` (double backslashes)
- NEVER use Git Bash paths like `/d/Code Projects/...` - mprocs will fail!

### Step 4: Create Session Directory

```bash
mkdir -p ".hive/sessions/{SESSION_ID}"
mkdir -p "{WORKTREE_ROOT}"
```

### Step 5: Create Git Worktrees

Create isolated worktrees based on variance level:

```bash
# Always create (Variance 1+):
# Worker A (Sonnet - clean/elegant approach)
git worktree add "{WORKTREE_ROOT}/impl-a" -b fusion/{SESSION_ID}/impl-a

# Worker B (Gemini - creative/alternative approach)
git worktree add "{WORKTREE_ROOT}/impl-b" -b fusion/{SESSION_ID}/impl-b

# Worker C (GPT - performance-focused approach)
git worktree add "{WORKTREE_ROOT}/impl-c" -b fusion/{SESSION_ID}/impl-c

# If VARIANCE >= 2:
# Worker D (GLM 4.7 - robust/thorough approach)
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
  "task_type": "fusion-algorithm",
  "variance": {VARIANCE},
  "algorithm": {
    "description": "{ALGORITHM_DESC}",
    "slug": "{ALGORITHM_SLUG}"
  },
  "base_branch": "{BASE_BRANCH}",
  "worktrees": {
    "impl-a": {
      "path": "{WORKTREE_ROOT}/impl-a",
      "branch": "fusion/{SESSION_ID}/impl-a",
      "worker": "worker-a",
      "provider": "claude-sonnet",
      "approach": "clean-elegant",
      "status": "pending"
    },
    "impl-b": {
      "path": "{WORKTREE_ROOT}/impl-b",
      "branch": "fusion/{SESSION_ID}/impl-b",
      "worker": "worker-b",
      "provider": "gemini-3-pro",
      "approach": "creative-alternative",
      "status": "pending"
    },
    "impl-c": {
      "path": "{WORKTREE_ROOT}/impl-c",
      "branch": "fusion/{SESSION_ID}/impl-c",
      "worker": "worker-c",
      "provider": "codex-gpt-5.2",
      "approach": "performance-focused",
      "status": "pending"
    }
    // If VARIANCE >= 2, add:
    ,"impl-d": {
      "path": "{WORKTREE_ROOT}/impl-d",
      "branch": "fusion/{SESSION_ID}/impl-d",
      "worker": "worker-d",
      "provider": "opencode-glm-4.7",
      "approach": "robust-thorough",
      "status": "pending"
    }
  },
  "evaluation": {
    "status": "pending",
    "criteria": ["tests_pass", "performance", "readability", "correctness", "edge_cases"],
    "winner": null,
    "scores": {}
  }
}
```

### Step 7: Create Judge Queen Prompt

Write to `.hive/sessions/{SESSION_ID}/queen-prompt.md`:

```markdown
# Judge Queen - Algorithm Fusion Evaluator

You are the **Judge Queen** for an F-Thread algorithm fusion session.

## Your Mission

Three workers are implementing the same algorithm in **separate git worktrees**. Your job is to:
1. Monitor their progress
2. Evaluate all three implementations when complete
3. Pick the winner (or recommend merging best elements)

## Algorithm to Implement

**{ALGORITHM_DESC}**

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Your Log**: .hive/sessions/{SESSION_ID}/queen.log
- **Thread Type**: F-Thread (Fusion) - True competing implementations

## Worktrees (Isolated Implementations)

**Variance Level**: {VARIANCE}

| Worker | Worktree | Branch | Approach | Variance |
|--------|----------|--------|----------|----------|
| worker-a | {WORKTREE_ROOT}/impl-a | fusion/{SESSION_ID}/impl-a | Clean/Elegant (Sonnet) | 1+ |
| worker-b | {WORKTREE_ROOT}/impl-b | fusion/{SESSION_ID}/impl-b | Creative/Alternative (Gemini) | 1+ |
| worker-c | {WORKTREE_ROOT}/impl-c | fusion/{SESSION_ID}/impl-c | Performance-Focused (GPT) | 1+ |
| worker-d | {WORKTREE_ROOT}/impl-d | fusion/{SESSION_ID}/impl-d | Robust/Thorough (GLM 4.7) | 2+ |

## Protocol

### Phase 1: Wait for Implementations

Monitor `tasks.json` and worker logs until all three workers report completion.

Log progress:
```markdown
---
[TIMESTAMP] MONITORING
---
- impl-a: {status}
- impl-b: {status}
- impl-c: {status}
---
```

### Phase 2: Evaluate Each Implementation

When all workers complete, evaluate each worktree:

**For each implementation:**

1. **Check tests pass**
   ```bash
   cd {WORKTREE_PATH}
   npm test  # or appropriate test command
   ```

2. **Run benchmarks** (if applicable)
   ```bash
   cd {WORKTREE_PATH}
   npm run bench  # or create simple benchmark
   ```

3. **Code review**
   - Read the implementation
   - Check for edge cases
   - Assess readability and maintainability
   - Look for bugs or issues

4. **Score on criteria** (1-10 each):
   - Tests pass: Do all tests pass?
   - Performance: How efficient is it?
   - Readability: How clear is the code?
   - Correctness: Does it handle all cases?
   - Edge cases: Are edge cases covered?

### Phase 3: Generate Comparison Report

Write to `.hive/sessions/{SESSION_ID}/evaluation.md`:

```markdown
# Algorithm Fusion Evaluation

## Algorithm: {ALGORITHM_DESC}

## Comparison Matrix

**Variance {VARIANCE}**: {3|4|5} implementations to evaluate

| Criteria | Impl A (Sonnet) | Impl B (Gemini) | Impl C (GPT) | Impl D (GLM 4.7)* |
|----------|-----------------|-----------------|--------------|-------------------|---------------------|
| Tests Pass | X/Y | X/Y | X/Y | X/Y | X/Y |
| Performance | Xms | Xms | Xms | Xms | Xms |
| Readability | X/10 | X/10 | X/10 | X/10 | X/10 |
| Correctness | X/10 | X/10 | X/10 | X/10 | X/10 |
| Edge Cases | X/10 | X/10 | X/10 | X/10 | X/10 |
| **Total** | **X/50** | **X/50** | **X/50** | **X/50** | **X/50** |

*Variance 2+ only | **Variance 3 only

## Implementation Summaries

### Implementation A (Sonnet - Clean/Elegant)
[Code summary and notable patterns]

### Implementation B (Gemini - Creative/Alternative)
[Code summary and notable patterns]

### Implementation C (GPT - Performance-Focused)
[Code summary and notable patterns]

### Implementation D (GLM 4.7 - Robust/Thorough) [Variance 2+]
[Code summary and notable patterns]

## Winner

**{WINNER}** with score {SCORE}/50

## Reasoning
[Why this implementation won]

## Recommendation
- [ ] Merge winner to {BASE_BRANCH}
- [ ] Cherry-pick specific elements from other implementations
- [ ] Request user review before merging
```

### Phase 4: Update tasks.json

Set evaluation status to complete, record winner.

### Phase 5: Cleanup Options

Present to user:
1. Merge winner branch to {BASE_BRANCH}
2. Keep all branches for review
3. Clean up worktrees and branches

## Coordination Files

| File | Purpose |
|------|---------|
| `.hive/sessions/{SESSION_ID}/tasks.json` | Session state |
| `.hive/sessions/{SESSION_ID}/queen.log` | Your activity log |
| `.hive/sessions/{SESSION_ID}/worker-*.log` | Worker outputs |
| `.hive/sessions/{SESSION_ID}/evaluation.md` | Final comparison |

## Begin

Start by announcing: "Judge Queen initialized for algorithm fusion. Monitoring three implementations of: {ALGORITHM_DESC}"
```

### Step 8: Create Worker Prompts

**Worker A Prompt** (`.hive/sessions/{SESSION_ID}/worker-a-prompt.md`):

```markdown
# Worker A - Clean/Elegant Implementation

You are **Worker A** implementing an algorithm in your own isolated worktree.

## Your Mission

Implement **{ALGORITHM_DESC}** with a focus on:
- Clean, readable code
- Elegant design patterns
- Clear abstractions
- Well-documented interfaces

## Your Worktree

- **Path**: {WORKTREE_ROOT}/impl-a
- **Branch**: fusion/{SESSION_ID}/impl-a
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-a.log

**IMPORTANT**: All your code changes go in YOUR worktree only. Do not modify the main project.

## Protocol

1. **Navigate to your worktree**
   ```bash
   cd "{WORKTREE_ROOT}/impl-a"
   ```

2. **Implement the algorithm**
   - Create necessary files
   - Write clean, well-documented code
   - Add unit tests
   - Ensure tests pass

3. **Log your progress** to worker-a.log

4. **Commit your work**
   ```bash
   git add .
   git commit -m "impl-a: {ALGORITHM_SLUG} - clean/elegant approach"
   ```

5. **Signal completion** by updating tasks.json

## Your Approach: Clean/Elegant

Focus on:
- Readable variable names
- Single responsibility principle
- Clear function signatures
- Comprehensive documentation
- Standard design patterns

Do NOT optimize prematurely. Clarity over cleverness.

## Begin

Announce: "Worker A starting clean/elegant implementation of {ALGORITHM_DESC}"
```

**Worker B Prompt** (`.hive/sessions/{SESSION_ID}/worker-b-prompt.md`):

```markdown
# Worker B - Creative/Alternative Implementation

You are **Worker B** implementing an algorithm in your own isolated worktree.

## Your Mission

Implement **{ALGORITHM_DESC}** with a focus on:
- Creative solutions
- Alternative approaches
- Novel patterns
- Thinking outside the box

## Your Worktree

- **Path**: {WORKTREE_ROOT}/impl-b
- **Branch**: fusion/{SESSION_ID}/impl-b
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-b.log

**IMPORTANT**: All your code changes go in YOUR worktree only. Do not modify the main project.

## Protocol

1. **Navigate to your worktree**
   ```bash
   cd "{WORKTREE_ROOT}/impl-b"
   ```

2. **Implement the algorithm**
   - Try an unconventional approach
   - Experiment with different data structures
   - Add unit tests
   - Ensure tests pass

3. **Log your progress** to worker-b.log

4. **Commit your work**
   ```bash
   git add .
   git commit -m "impl-b: {ALGORITHM_SLUG} - creative/alternative approach"
   ```

5. **Signal completion** by updating tasks.json

## Your Approach: Creative/Alternative

Focus on:
- Different data structures than typical
- Functional vs imperative approaches
- Unconventional algorithms
- Novel abstractions
- What would a creative solution look like?

Be bold. Try something different.

## Begin

Announce: "Worker B starting creative/alternative implementation of {ALGORITHM_DESC}"
```

**Worker C Prompt** (`.hive/sessions/{SESSION_ID}/worker-c-prompt.md`):

```markdown
# Worker C - Performance-Focused Implementation

You are **Worker C** implementing an algorithm in your own isolated worktree.

## Your Mission

Implement **{ALGORITHM_DESC}** with a focus on:
- Maximum performance
- Memory efficiency
- Optimized algorithms
- Benchmark-driven development

## Your Worktree

- **Path**: {WORKTREE_ROOT}/impl-c
- **Branch**: fusion/{SESSION_ID}/impl-c
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-c.log

**IMPORTANT**: All your code changes go in YOUR worktree only. Do not modify the main project.

## Protocol

1. **Navigate to your worktree**
   ```bash
   cd "{WORKTREE_ROOT}/impl-c"
   ```

2. **Implement the algorithm**
   - Optimize for speed
   - Consider memory usage
   - Add unit tests AND benchmarks
   - Ensure tests pass

3. **Log your progress** to worker-c.log

4. **Commit your work**
   ```bash
   git add .
   git commit -m "impl-c: {ALGORITHM_SLUG} - performance-focused approach"
   ```

5. **Signal completion** by updating tasks.json

## Your Approach: Performance-Focused

Focus on:
- Big-O complexity optimization
- Cache-friendly data layouts
- Avoiding unnecessary allocations
- Profiling and benchmarking
- Low-level optimizations where appropriate

Speed matters. Measure everything.

## Begin

Announce: "Worker C starting performance-focused implementation of {ALGORITHM_DESC}"
```

**Worker D Prompt** (`.hive/sessions/{SESSION_ID}/worker-d-prompt.md`) - **Variance 2+ only**:

```markdown
# Worker D - Robust/Thorough Implementation

You are **Worker D** implementing an algorithm in your own isolated worktree.

## Your Mission

Implement **{ALGORITHM_DESC}** with a focus on:
- Robust error handling
- Thorough edge case coverage
- Defensive programming
- Production-ready resilience

## Your Worktree

- **Path**: {WORKTREE_ROOT}/impl-d
- **Branch**: fusion/{SESSION_ID}/impl-d
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-d.log

**IMPORTANT**: All your code changes go in YOUR worktree only. Do not modify the main project.

## Protocol

1. **Navigate to your worktree**
   ```bash
   cd "{WORKTREE_ROOT}/impl-d"
   ```

2. **Implement the algorithm**
   - Handle every edge case
   - Add comprehensive error handling
   - Write extensive tests
   - Ensure tests pass

3. **Log your progress** to worker-d.log

4. **Commit your work**
   ```bash
   git add .
   git commit -m "impl-d: {ALGORITHM_SLUG} - robust/thorough approach"
   ```

5. **Signal completion** by updating tasks.json

## Your Approach: Robust/Thorough

Focus on:
- Input validation
- Error recovery
- Null/undefined handling
- Boundary conditions
- Concurrent access safety
- Comprehensive test coverage

Production resilience over elegance.

## Begin

Announce: "Worker D starting robust/thorough implementation of {ALGORITHM_DESC}"
```

**Worker E Prompt** (`.hive/sessions/{SESSION_ID}/worker-e-prompt.md`) - **Variance 3 only**:

```markdown
# Worker E - Multi-Paradigm Implementation

You are **Worker E** implementing an algorithm in your own isolated worktree.

## Your Mission

Implement **{ALGORITHM_DESC}** with a focus on:
- Multi-paradigm approach
- Cross-language patterns
- Agentic design patterns
- Flexible architecture

## Your Worktree

- **Path**: {WORKTREE_ROOT}/impl-e
- **Branch**: fusion/{SESSION_ID}/impl-e
- **Your Log**: .hive/sessions/{SESSION_ID}/worker-e.log

**IMPORTANT**: All your code changes go in YOUR worktree only. Do not modify the main project.

## Protocol

1. **Navigate to your worktree**
   ```bash
   cd "{WORKTREE_ROOT}/impl-e"
   ```

2. **Implement the algorithm**
   - Draw from multiple paradigms
   - Consider patterns from different languages
   - Add unit tests
   - Ensure tests pass

3. **Log your progress** to worker-e.log

4. **Commit your work**
   ```bash
   git add .
   git commit -m "impl-e: {ALGORITHM_SLUG} - multi-paradigm approach"
   ```

5. **Signal completion** by updating tasks.json

## Your Approach: Multi-Paradigm

Focus on:
- Functional + OOP hybrid
- Patterns from Rust, Go, Python
- Composable abstractions
- Plugin/extension points
- Agentic tool patterns

Synthesize the best of all worlds.

## Begin

Announce: "Worker E starting multi-paradigm implementation of {ALGORITHM_DESC}"
```

### Step 9: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# mprocs configuration for Fusion Algorithm session: {SESSION_ID}
# Variance Level: {VARIANCE} ({3|4|5} workers)
procs:
  judge-queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the JUDGE QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "judge-queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      FUSION_TYPE: "algorithm"
      VARIANCE: "{VARIANCE}"

  # === Always included (Variance 1+) ===
  worker-a-sonnet:
    cmd: ["claude", "--model", "sonnet", "--dangerously-skip-permissions", "You are WORKER A. Read .hive/sessions/{SESSION_ID}/worker-a-prompt.md"]
    cwd: "{WORKTREE_ROOT}/impl-a"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "a"
      FUSION_APPROACH: "clean-elegant"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-b-gemini:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER B. Read .hive/sessions/{SESSION_ID}/worker-b-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-b"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "b"
      FUSION_APPROACH: "creative-alternative"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-c-gpt:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER C. Read .hive/sessions/{SESSION_ID}/worker-c-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-c"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "c"
      FUSION_APPROACH: "performance-focused"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  # === Variance 2+ only ===
  worker-d-glm:
    cmd: ["powershell", "-NoProfile", "-Command", "cd '{WORKTREE_ROOT}/impl-d'; $env:OPENCODE_YOLO='true'; opencode run --format default -m opencode/glm-4.7-free 'You are WORKER D. Read .hive/sessions/{SESSION_ID}/worker-d-prompt.md and implement the algorithm with a robust/thorough approach.'"]
    cwd: "{WORKTREE_ROOT}/impl-d"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "d"
      FUSION_APPROACH: "robust-thorough"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 5 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

**Note**: Only include worker-d-glm if VARIANCE >= 2.

### Step 10: Create Empty Log Files

```bash
# Always create (Variance 1+):
cd "{PROJECT_ROOT}" && type nul > ".hive/sessions/{SESSION_ID}/queen.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-a.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-b.log" && type nul > ".hive/sessions/{SESSION_ID}/worker-c.log"

# If VARIANCE >= 2:
type nul > ".hive/sessions/{SESSION_ID}/worker-d.log"

# If VARIANCE >= 3:
type nul > ".hive/sessions/{SESSION_ID}/worker-e.log"
```

### Step 11: Launch mprocs

```bash
powershell -Command "Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd \"{PROJECT_ROOT}\"; mprocs --config .hive/mprocs.yaml'"
```

### Step 12: Output Status

```markdown
## Fusion Algorithm Arena Launched!

**Thread Type**: F-Thread (True Fusion)
**Session**: {SESSION_ID}
**Algorithm**: {ALGORITHM_DESC}
**Variance Level**: {VARIANCE} ({3|4|5} competing implementations)

### Isolated Worktrees

| Worker | Location | Branch | Approach | Variance |
|--------|----------|--------|----------|----------|
| Worker A | {WORKTREE_ROOT}/impl-a | fusion/{SESSION_ID}/impl-a | Clean/Elegant | 1+ |
| Worker B | {WORKTREE_ROOT}/impl-b | fusion/{SESSION_ID}/impl-b | Creative/Alternative | 1+ |
| Worker C | {WORKTREE_ROOT}/impl-c | fusion/{SESSION_ID}/impl-c | Performance-Focused | 1+ |
| Worker D | {WORKTREE_ROOT}/impl-d | fusion/{SESSION_ID}/impl-d | Robust/Thorough | 2+ |
| Worker E | {WORKTREE_ROOT}/impl-e | fusion/{SESSION_ID}/impl-e | Multi-Paradigm | 3 |

### Team

| Pane | Provider | Focus | Variance |
|------|----------|-------|----------|
| judge-queen | Opus 4.5 | Evaluates all implementations | 1+ |
| worker-a | Sonnet | Clean, readable, elegant code | 1+ |
| worker-b | Gemini 3 Pro | Creative, unconventional approach | 1+ |
| worker-c | GPT-5.2 | Performance-optimized code | 1+ |
| worker-d | GLM 4.7 (OpenCode) | Robust, production-ready code | 2+ |

### Fusion Flow

1. Workers implement independently in isolated worktrees
2. Each commits to their own branch
3. Judge Queen evaluates all {3|4|5} implementations
4. Comparison matrix generated
5. Winner selected or best elements merged

### Cleanup (when done)

```bash
# Remove worktrees (always)
git worktree remove "{WORKTREE_ROOT}/impl-a"
git worktree remove "{WORKTREE_ROOT}/impl-b"
git worktree remove "{WORKTREE_ROOT}/impl-c"

# If VARIANCE >= 2:
git worktree remove "{WORKTREE_ROOT}/impl-d"

# If VARIANCE >= 3:
git worktree remove "{WORKTREE_ROOT}/impl-e"

# Delete branches (if not merging)
git branch -D fusion/{SESSION_ID}/impl-a
git branch -D fusion/{SESSION_ID}/impl-b
git branch -D fusion/{SESSION_ID}/impl-c
git branch -D fusion/{SESSION_ID}/impl-d  # Variance 2+
git branch -D fusion/{SESSION_ID}/impl-e  # Variance 3
```

Watch {3|4|5} competing implementations battle it out!
```
