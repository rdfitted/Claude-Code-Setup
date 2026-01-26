---
description: F-Thread - Competing API designs in separate worktrees, evaluate ergonomics and pick best
argument-hint: "<api-description>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Fusion API - True F-Thread API Design Arena

Launch 3-5 workers (based on variance level) in **separate git worktrees** to design the same API independently. A Judge Queen evaluates ergonomics, consistency, and developer experience.

## Thread Type: F-Thread (Fusion)

This is a TRUE fusion thread for API design:
- **Divergent worktrees**: Each worker designs a unique API surface
- **Real artifacts**: Actual working API with types and implementation
- **DX comparison**: Evaluate how each API feels to use
- **Best-of-N selection**: Most ergonomic API wins

## Arguments

- `<api-description>`: What API to design (e.g., "authentication service", "file upload handler", "notification system")
- `--variance N`: Model diversity level (1-3, default: 1)
  - **Variance 1** (default): 3 workers (Sonnet, Gemini Pro, GPT-5.2)
  - **Variance 2**: 4 workers (+GLM 4.7 via OpenCode)

## Why F-Thread for API Design?

API design is highly subjective. Different philosophies produce different ergonomics:
- Worker A: REST-ful, resource-oriented
- Worker B: Functional, composable
- Worker C: Object-oriented, fluent/chainable

See all three before committing to one.

## Workflow

### Step 1-4: Prerequisites, Parse, Variables, Directories

(Same pattern as fusion-algorithm.md with appropriate substitutions)

**Variables** (in Step 3):
```
GEMINI_MODEL = "gemini-3-pro-preview"  # API design = code generation, use Pro
```

### Step 5: Create Git Worktrees

```bash
# Worker A - RESTful/Resource-oriented design
git worktree add "{WORKTREE_ROOT}/impl-a" -b fusion/{SESSION_ID}/impl-a

# Worker B - Functional/Composable design
git worktree add "{WORKTREE_ROOT}/impl-b" -b fusion/{SESSION_ID}/impl-b

# Worker C - Object-oriented/Fluent design
git worktree add "{WORKTREE_ROOT}/impl-c" -b fusion/{SESSION_ID}/impl-c
```

### Step 6: Create tasks.json

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "F-Thread (Fusion)",
  "task_type": "fusion-api",
  "api": {
    "description": "{API_DESC}",
    "slug": "{API_SLUG}"
  },
  "base_branch": "{BASE_BRANCH}",
  "worktrees": {
    "impl-a": {
      "path": "{WORKTREE_ROOT}/impl-a",
      "branch": "fusion/{SESSION_ID}/impl-a",
      "worker": "worker-a",
      "provider": "claude-sonnet",
      "design_philosophy": "restful-resource",
      "status": "pending"
    },
    "impl-b": {
      "path": "{WORKTREE_ROOT}/impl-b",
      "branch": "fusion/{SESSION_ID}/impl-b",
      "worker": "worker-b",
      "provider": "gemini-3-pro",
      "design_philosophy": "functional-composable",
      "status": "pending"
    },
    "impl-c": {
      "path": "{WORKTREE_ROOT}/impl-c",
      "branch": "fusion/{SESSION_ID}/impl-c",
      "worker": "worker-c",
      "provider": "codex-gpt-5.2",
      "design_philosophy": "oop-fluent",
      "status": "pending"
    }
  },
  "evaluation": {
    "status": "pending",
    "criteria": ["discoverability", "type_safety", "consistency", "documentation", "error_handling"],
    "winner": null
  }
}
```

### Step 7: Create Judge Queen Prompt

```markdown
# Judge Queen - API Design Fusion Evaluator

You are the **Judge Queen** for an F-Thread API design session.

## Your Mission

Three workers are designing the same API with different philosophies. Your job is to:
1. Monitor their progress
2. Evaluate the developer experience of each
3. Pick the most ergonomic design

## API to Design

**{API_DESC}**

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Thread Type**: F-Thread (Fusion) - Competing API designs

## Design Philosophies

| Worker | Philosophy | Style |
|--------|------------|-------|
| worker-a | RESTful/Resource | `users.get(id)`, `posts.create(data)` |
| worker-b | Functional/Composable | `pipe(fetch, validate, transform)` |
| worker-c | OOP/Fluent | `client.users().withId(id).posts().limit(10).fetch()` |

## Evaluation Criteria

1. **Discoverability**: Can you guess the API without docs?
2. **Type Safety**: Are types helpful and accurate?
3. **Consistency**: Does the API follow consistent patterns?
4. **Documentation**: Are docs/comments helpful?
5. **Error Handling**: Are errors clear and actionable?

## DX Evaluation Method

For each API, write the same 3 usage scenarios:

```typescript
// Scenario 1: Basic CRUD
// How do you create, read, update, delete?

// Scenario 2: Complex query
// How do you filter, sort, paginate?

// Scenario 3: Error handling
// How do you catch and handle errors?
```

Rate how each feels to write.

## Generate Comparison Report

Write to `.hive/sessions/{SESSION_ID}/evaluation.md`:

```markdown
# API Design Fusion Evaluation

## API: {API_DESC}

## Side-by-Side Usage Comparison

### Scenario 1: Basic CRUD

**RESTful (A)**:
```typescript
// Code example
```

**Functional (B)**:
```typescript
// Code example
```

**Fluent (C)**:
```typescript
// Code example
```

### Scenario 2: Complex Query

[Same format]

### Scenario 3: Error Handling

[Same format]

## Evaluation Matrix

| Criteria | API A (REST) | API B (Functional) | API C (Fluent) |
|----------|--------------|-------------------|----------------|
| Discoverability | X/10 | X/10 | X/10 |
| Type Safety | X/10 | X/10 | X/10 |
| Consistency | X/10 | X/10 | X/10 |
| Documentation | X/10 | X/10 | X/10 |
| Error Handling | X/10 | X/10 | X/10 |
| **Total** | **X/50** | **X/50** | **X/50** |

## Recommendation

**Winner**: {API_STYLE}

### Why This Design Wins
[Explanation focusing on DX]

### When to Use Each

| Style | Best For |
|-------|----------|
| RESTful | CRUD-heavy apps, REST API clients |
| Functional | Data pipelines, transformation-heavy |
| Fluent | Complex queries, builder patterns |
```

## Present Options

After evaluation, present to user:
"All three API designs are complete. Here's how they compare:

A (RESTful): Best for [use case]
B (Functional): Best for [use case]
C (Fluent): Best for [use case]

Which feels right for your project?"
```

### Step 8: Create Worker Prompts

**Worker A** (RESTful/Resource-oriented):
```markdown
# Worker A - RESTful/Resource-Oriented API Design

## Your Mission
Design **{API_DESC}** using a RESTful, resource-oriented approach.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-a
- **Branch**: fusion/{SESSION_ID}/impl-a

## Design Philosophy: RESTful/Resource

Core principles:
- Resources are nouns (users, posts, comments)
- Methods are verbs (get, create, update, delete)
- Nested resources show relationships
- Consistent patterns across all resources

## API Structure Pattern

```typescript
// Resource pattern
interface Resource<T> {
  get(id: string): Promise<T>;
  list(options?: ListOptions): Promise<T[]>;
  create(data: CreateInput<T>): Promise<T>;
  update(id: string, data: UpdateInput<T>): Promise<T>;
  delete(id: string): Promise<void>;
}

// Usage
const user = await api.users.get('123');
const posts = await api.users('123').posts.list({ limit: 10 });
```

## Deliverables

1. Type definitions for all resources
2. Implementation with consistent patterns
3. Example usage file showing common operations
4. README documenting the API surface

## Begin

Announce: "Worker A designing RESTful/resource-oriented API for {API_DESC}"
```

**Worker B** (Functional/Composable):
```markdown
# Worker B - Functional/Composable API Design

## Your Mission
Design **{API_DESC}** using a functional, composable approach.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-b
- **Branch**: fusion/{SESSION_ID}/impl-b

## Design Philosophy: Functional/Composable

Core principles:
- Pure functions with no side effects
- Composable operations via pipe/flow
- Data transformations as functions
- Explicit over implicit

## API Structure Pattern

```typescript
// Composable functions
const getUser = (id: string) => fetch(`/users/${id}`);
const validateUser = (user: User) => { /* validate */ };
const transformUser = (user: User) => { /* transform */ };

// Composed pipeline
const fetchUser = pipe(
  getUser,
  validateResponse,
  parseJSON,
  validateUser,
  transformUser
);

// Usage
const user = await fetchUser('123');
```

## Deliverables

1. Composable function library
2. Pipe/flow utilities
3. Example compositions for common operations
4. README documenting composability patterns

## Begin

Announce: "Worker B designing functional/composable API for {API_DESC}"
```

**Worker C** (OOP/Fluent):
```markdown
# Worker C - Object-Oriented/Fluent API Design

## Your Mission
Design **{API_DESC}** using an object-oriented, fluent/chainable approach.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-c
- **Branch**: fusion/{SESSION_ID}/impl-c

## Design Philosophy: OOP/Fluent

Core principles:
- Method chaining for readable queries
- Builder pattern for complex operations
- Encapsulated state management
- Discoverable via IDE autocomplete

## API Structure Pattern

```typescript
// Fluent builder pattern
class UserQuery {
  withId(id: string): this;
  withEmail(email: string): this;
  include(relation: string): this;
  limit(n: number): this;
  offset(n: number): this;
  orderBy(field: string, dir?: 'asc' | 'desc'): this;
  fetch(): Promise<User[]>;
}

// Usage
const users = await client
  .users()
  .where('active', true)
  .include('posts')
  .orderBy('createdAt', 'desc')
  .limit(10)
  .fetch();
```

## Deliverables

1. Fluent builder classes
2. Chainable method implementations
3. Example queries for common operations
4. README documenting the fluent interface

## Begin

Announce: "Worker C designing OOP/fluent API for {API_DESC}"
```

### Output Status

```markdown
## Fusion API Arena Launched!

**Thread Type**: F-Thread (True Fusion)
**Session**: {SESSION_ID}
**API**: {API_DESC}

### Competing Design Philosophies

| Worker | Philosophy | Example Style |
|--------|------------|---------------|
| Worker A | RESTful/Resource | `api.users.get(id)` |
| Worker B | Functional/Composable | `pipe(fetch, validate, transform)(id)` |
| Worker C | OOP/Fluent | `client.users().withId(id).fetch()` |

### What Gets Evaluated

- How easy is it to discover the API?
- How safe are the types?
- How consistent is the design?
- How are errors communicated?

### Why Three Philosophies?

API design is subjective. What feels "right" depends on:
- Your team's background (FP vs OOP)
- Your use cases (CRUD vs pipelines vs queries)
- Your tooling (IDE support, type inference)

See all three, then decide!

Watch three API philosophies take shape!
```

### Step 9: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# mprocs configuration for Fusion API session: {SESSION_ID}
# Gemini CLI: using latest installed version
procs:
  judge-queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the JUDGE QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "judge-queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      FUSION_TYPE: "api"

  worker-a-sonnet:
    cmd: ["claude", "--model", "sonnet", "--dangerously-skip-permissions", "You are WORKER A. Read .hive/sessions/{SESSION_ID}/worker-a-prompt.md"]
    cwd: "{WORKTREE_ROOT}/impl-a"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "a"
      FUSION_APPROACH: "restful-resource"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-b-gemini:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER B. Read .hive/sessions/{SESSION_ID}/worker-b-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-b"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "b"
      FUSION_APPROACH: "functional-composable"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-c-gpt:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER C. Read .hive/sessions/{SESSION_ID}/worker-c-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-c"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "c"
      FUSION_APPROACH: "oop-fluent"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 5 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

**Note**: Set `GEMINI_MODEL = "gemini-3-pro-preview"` for API design (code generation benefits from Pro model).

### Variance Workers (Optional)

**If VARIANCE >= 2, add Worker D (GLM 4.7 - Declarative/DSL approach):**

```yaml
  worker-d-glm:
    cmd: ["powershell", "-NoProfile", "-Command", "cd '{WORKTREE_ROOT}/impl-d'; $env:OPENCODE_YOLO='true'; opencode run --format default -m opencode/glm-4.7-free 'You are WORKER D. Design the API using a declarative/DSL approach. Focus on configuration over code, schema-driven design, and GraphQL-like patterns.'"]
    cwd: "{WORKTREE_ROOT}/impl-d"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "d"
      FUSION_APPROACH: "declarative-dsl"
```

Create additional worktrees for variance workers:
```bash
# If VARIANCE >= 2:
git worktree add "{WORKTREE_ROOT}/impl-d" -b fusion/{SESSION_ID}/impl-d
```
