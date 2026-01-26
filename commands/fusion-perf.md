---
description: F-Thread - Competing performance optimizations in separate worktrees, benchmark to pick winner
argument-hint: "<code-path-or-performance-issue>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Fusion Perf - True F-Thread Performance Optimization Arena

Launch 3-5 workers (based on variance level) in **separate git worktrees** to optimize the same code independently. A Judge Queen benchmarks all optimizations and picks the fastest.

## Thread Type: F-Thread (Fusion)

This is a TRUE fusion thread for performance optimization:
- **Divergent worktrees**: Each worker optimizes independently
- **Real artifacts**: Actual optimized code
- **Benchmark-driven**: Performance measured, not guessed
- **Best-of-N selection**: Fastest correct implementation wins

## Arguments

- `<code-path-or-performance-issue>`: Path to slow code or description of performance issue
- `--variance N`: Model diversity level (1-3, default: 1)
  - **Variance 1** (default): 3 workers (Opus, Gemini Pro, GPT-5.2)
  - **Variance 2**: 4 workers (+GLM 4.7 via OpenCode)

## Why F-Thread for Performance?

Different optimization strategies work better for different bottlenecks:
- Worker A: Algorithm optimization (better Big-O)
- Worker B: Memory optimization (fewer allocations)
- Worker C: Parallelization (concurrent execution)

Benchmark all three to find what actually helps.

## Workflow

### Step 1-4: Prerequisites, Parse, Variables, Directories

(Same pattern as fusion-algorithm.md with appropriate substitutions)

**Variables** (in Step 3):
```
GEMINI_MODEL = "gemini-3-pro-preview"  # Performance optimization = code generation, use Pro
```

### Step 5: Create Git Worktrees

```bash
# Worker A - Algorithm optimization
git worktree add "{WORKTREE_ROOT}/impl-a" -b fusion/{SESSION_ID}/impl-a

# Worker B - Memory optimization
git worktree add "{WORKTREE_ROOT}/impl-b" -b fusion/{SESSION_ID}/impl-b

# Worker C - Parallelization optimization
git worktree add "{WORKTREE_ROOT}/impl-c" -b fusion/{SESSION_ID}/impl-c
```

### Step 6: Create tasks.json

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "F-Thread (Fusion)",
  "task_type": "fusion-perf",
  "optimization": {
    "target": "{PERF_TARGET}",
    "slug": "{PERF_SLUG}",
    "baseline_time": null
  },
  "base_branch": "{BASE_BRANCH}",
  "worktrees": {
    "impl-a": {
      "path": "{WORKTREE_ROOT}/impl-a",
      "branch": "fusion/{SESSION_ID}/impl-a",
      "worker": "worker-a",
      "provider": "claude-opus",
      "strategy": "algorithm-optimization",
      "status": "pending",
      "benchmark_result": null
    },
    "impl-b": {
      "path": "{WORKTREE_ROOT}/impl-b",
      "branch": "fusion/{SESSION_ID}/impl-b",
      "worker": "worker-b",
      "provider": "gemini-3-pro",
      "strategy": "memory-optimization",
      "status": "pending",
      "benchmark_result": null
    },
    "impl-c": {
      "path": "{WORKTREE_ROOT}/impl-c",
      "branch": "fusion/{SESSION_ID}/impl-c",
      "worker": "worker-c",
      "provider": "codex-gpt-5.2",
      "strategy": "parallelization",
      "status": "pending",
      "benchmark_result": null
    }
  },
  "evaluation": {
    "status": "pending",
    "criteria": ["execution_time", "memory_usage", "correctness", "maintainability", "scalability"],
    "winner": null
  }
}
```

### Step 7: Create Judge Queen Prompt

```markdown
# Judge Queen - Performance Optimization Evaluator

You are the **Judge Queen** for an F-Thread performance optimization session.

## Your Mission

Three workers are optimizing the same code with different strategies. Your job is to:
1. Establish baseline performance
2. Monitor their progress
3. Benchmark all three optimizations
4. Pick the winner based on MEASURED performance

## Optimization Target

**{PERF_TARGET}**

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Thread Type**: F-Thread (Fusion) - Competing optimizations

## Optimization Strategies

| Worker | Strategy | Approach |
|--------|----------|----------|
| worker-a | Algorithm | Better Big-O, smarter data structures |
| worker-b | Memory | Fewer allocations, pooling, caching |
| worker-c | Parallelization | Concurrent execution, workers, SIMD |

## Benchmarking Protocol

### Phase 1: Establish Baseline

Before workers start, measure current performance:

```bash
# Run baseline benchmark on original code
cd {PROJECT_ROOT}
# Run benchmark command appropriate for the code
# Record: execution time, memory usage, iterations/second
```

Document baseline in `.hive/sessions/{SESSION_ID}/baseline.md`

### Phase 2: Monitor Workers

Watch for completion. Each worker should:
- Include a benchmark in their implementation
- Not break existing tests
- Document their optimization approach

### Phase 3: Benchmark All Implementations

For each worktree:

```bash
cd {WORKTREE_PATH}

# 1. Run correctness tests
npm test  # or equivalent

# 2. Run performance benchmark
# Options:
# - npm run bench
# - hyperfine 'node script.js'
# - time command
# - Built-in benchmark

# 3. Measure memory
# - process.memoryUsage()
# - /usr/bin/time -v
# - heaptrack
```

Run each benchmark **multiple times** for accuracy.

### Phase 4: Generate Comparison Report

Write to `.hive/sessions/{SESSION_ID}/benchmark-results.md`:

```markdown
# Performance Optimization Benchmark Results

## Target: {PERF_TARGET}

## Test Environment
- Platform: {OS/Version}
- Node/Runtime: {Version}
- CPU: {Info}
- Memory: {Info}

## Baseline Performance
- Execution time: {X}ms
- Memory usage: {X}MB
- Ops/second: {X}

## Optimization Results

| Metric | Baseline | Algo (A) | Memory (B) | Parallel (C) |
|--------|----------|----------|------------|--------------|
| Exec time | {X}ms | {X}ms ({X}%) | {X}ms ({X}%) | {X}ms ({X}%) |
| Memory | {X}MB | {X}MB | {X}MB | {X}MB |
| Ops/sec | {X} | {X} | {X} | {X} |
| Tests pass | - | Yes/No | Yes/No | Yes/No |

## Speedup Summary

| Optimization | Speedup | Memory Impact |
|--------------|---------|---------------|
| Algorithm (A) | {X}x faster | {+/-X}% |
| Memory (B) | {X}x faster | {+/-X}% |
| Parallel (C) | {X}x faster | {+/-X}% |

## Winner

**{STRATEGY}** with **{X}x speedup**

### Why This Wins
[Analysis of why this optimization was most effective]

### Implementation Notes
[Key techniques used in winning implementation]

### Trade-offs
[What was sacrificed for performance: readability, memory, etc.]
```

## Critical Rules

1. **Correctness first**: A fast wrong answer is worthless
2. **Measure, don't guess**: Actual benchmarks, not intuition
3. **Multiple runs**: Account for variance
4. **Same test data**: All implementations benchmark same inputs
```

### Step 8: Create Worker Prompts

**Worker A** (Algorithm Optimization):
```markdown
# Worker A - Algorithm Optimization

## Your Mission
Optimize **{PERF_TARGET}** by improving the algorithm.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-a
- **Branch**: fusion/{SESSION_ID}/impl-a

## Your Strategy: Algorithm Optimization

Focus on:
- Better time complexity (O(n) -> O(log n))
- Smarter data structures (array -> hash map)
- Algorithmic techniques (memoization, dynamic programming)
- Reducing unnecessary iterations
- Early exits and short circuits

## Do NOT:
- Sacrifice correctness for speed
- Use parallelization (that's Worker C's job)
- Focus on memory (that's Worker B's job)

## Deliverables

1. Optimized implementation
2. Benchmark showing improvement
3. Big-O analysis: before vs after
4. Document algorithm changes in worker-a.log

## Benchmark Template

```javascript
// benchmark.js
const { performance } = require('perf_hooks');

const iterations = 1000;
const start = performance.now();

for (let i = 0; i < iterations; i++) {
  // Run optimized code
}

const end = performance.now();
console.log(`Time: ${(end - start) / iterations}ms per iteration`);
```

## Begin

Announce: "Worker A optimizing {PERF_TARGET} via algorithm improvements"
```

**Worker B** (Memory Optimization):
```markdown
# Worker B - Memory Optimization

## Your Mission
Optimize **{PERF_TARGET}** by reducing memory pressure.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-b
- **Branch**: fusion/{SESSION_ID}/impl-b

## Your Strategy: Memory Optimization

Focus on:
- Object pooling
- Pre-allocation
- Reducing garbage collection pressure
- Caching/memoization
- Streaming vs loading all in memory
- Buffer reuse
- Avoiding intermediate arrays

## Do NOT:
- Sacrifice correctness for speed
- Change the algorithm significantly (that's Worker A's job)
- Use parallelization (that's Worker C's job)

## Deliverables

1. Memory-optimized implementation
2. Benchmark showing improvement
3. Memory profile: before vs after
4. Document memory techniques in worker-b.log

## Memory Profiling

```javascript
// Profile memory
const before = process.memoryUsage();
// Run code
const after = process.memoryUsage();

console.log('Heap used:', (after.heapUsed - before.heapUsed) / 1024 / 1024, 'MB');
```

## Begin

Announce: "Worker B optimizing {PERF_TARGET} via memory improvements"
```

**Worker C** (Parallelization):
```markdown
# Worker C - Parallelization Optimization

## Your Mission
Optimize **{PERF_TARGET}** by adding parallelization.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-c
- **Branch**: fusion/{SESSION_ID}/impl-c

## Your Strategy: Parallelization

Focus on:
- Worker threads
- Promise.all for concurrent I/O
- Web Workers (if browser)
- Chunking work for parallel processing
- SIMD if applicable
- Avoiding contention and locks

## Do NOT:
- Sacrifice correctness for speed
- Introduce race conditions
- Over-parallelize (diminishing returns)

## Deliverables

1. Parallelized implementation
2. Benchmark showing improvement
3. Scalability analysis (1, 2, 4, 8 threads)
4. Document parallelization approach in worker-c.log

## Parallelization Patterns

```javascript
// Worker threads
const { Worker, isMainThread, workerData } = require('worker_threads');

// Promise.all for I/O
const results = await Promise.all(
  items.map(item => processItem(item))
);

// Chunking
function chunkArray(arr, size) {
  return Array.from({ length: Math.ceil(arr.length / size) },
    (_, i) => arr.slice(i * size, i * size + size));
}
```

## Begin

Announce: "Worker C optimizing {PERF_TARGET} via parallelization"
```

### Output Status

```markdown
## Fusion Perf Arena Launched!

**Thread Type**: F-Thread (True Fusion)
**Session**: {SESSION_ID}
**Target**: {PERF_TARGET}

### Competing Optimization Strategies

| Worker | Strategy | Technique |
|--------|----------|-----------|
| Worker A | Algorithm | Better Big-O, smarter structures |
| Worker B | Memory | Fewer allocations, pooling, caching |
| Worker C | Parallelization | Concurrent execution, workers |

### Benchmark Process

1. **Baseline**: Judge establishes current performance
2. **Optimize**: Workers implement their strategies
3. **Benchmark**: Judge measures all three
4. **Winner**: Fastest correct implementation wins

### Why Three Strategies?

Different bottlenecks need different solutions:
- **CPU-bound**: Algorithm optimization usually wins
- **Memory-bound**: Memory optimization helps
- **I/O-bound**: Parallelization shines

Let the benchmarks decide!

### Metrics Tracked

- Execution time (primary)
- Memory usage
- Ops/second
- Correctness (tests must pass)

Watch three optimization strategies compete on real benchmarks!
```

### Step 9: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# mprocs configuration for Fusion Perf session: {SESSION_ID}
# Gemini CLI: using latest installed version
procs:
  judge-queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the JUDGE QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "judge-queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      FUSION_TYPE: "perf"

  worker-a-opus:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are WORKER A. Read .hive/sessions/{SESSION_ID}/worker-a-prompt.md"]
    cwd: "{WORKTREE_ROOT}/impl-a"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "a"
      FUSION_APPROACH: "algorithm-optimization"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-b-gemini:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER B. Read .hive/sessions/{SESSION_ID}/worker-b-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-b"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "b"
      FUSION_APPROACH: "memory-optimization"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-c-gpt:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER C. Read .hive/sessions/{SESSION_ID}/worker-c-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-c"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "c"
      FUSION_APPROACH: "parallelization"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 5 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

### Variance Workers (Optional)

**If VARIANCE >= 2, add Worker D (GLM 4.7 - I/O optimization):**

```yaml
  worker-d-glm:
    cmd: ["powershell", "-NoProfile", "-Command", "cd '{WORKTREE_ROOT}/impl-d'; $env:OPENCODE_YOLO='true'; opencode run --format default -m opencode/glm-4.7-free 'You are WORKER D. Optimize via I/O improvements. Focus on batching, connection pooling, lazy loading, streaming, and reducing network round-trips.'"]
    cwd: "{WORKTREE_ROOT}/impl-d"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "d"
      FUSION_APPROACH: "io-optimization"
```

Create additional worktrees for variance workers:
```bash
# If VARIANCE >= 2:
git worktree add "{WORKTREE_ROOT}/impl-d" -b fusion/{SESSION_ID}/impl-d
```
