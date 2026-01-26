---
description: F-Thread - Competing data model designs in separate worktrees, evaluate trade-offs and pick best
argument-hint: "<domain-or-feature-description>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Fusion Data Model - True F-Thread Schema Design Arena

Launch 3-5 workers (based on variance level) in **separate git worktrees** to design the same data model independently. A Judge Queen evaluates trade-offs and helps pick the best schema for your use case.

## Thread Type: F-Thread (Fusion)

This is a TRUE fusion thread for data modeling:
- **Divergent worktrees**: Each worker designs a unique schema
- **Real artifacts**: Actual migrations, types, and queries
- **Trade-off analysis**: Query patterns, scalability, complexity
- **Best-of-N selection**: Right model for YOUR use case wins

## Arguments

- `<domain-or-feature-description>`: What to model (e.g., "e-commerce orders", "social media posts", "multi-tenant SaaS")
- `--variance N`: Model diversity level (1-3, default: 1)
  - **Variance 1** (default): 3 workers (Opus, Gemini Pro, GPT-5.2)
  - **Variance 2**: 4 workers (+GLM 4.7 via OpenCode)

## Why F-Thread for Data Models?

Data model decisions are **expensive to change** later. Different philosophies produce wildly different schemas:

| Philosophy | Optimize For | Trade-off |
|------------|--------------|-----------|
| Normalized | Data integrity, flexibility | More joins, complex queries |
| Denormalized | Read performance, simplicity | Data duplication, update anomalies |
| Event-sourced | Audit trail, temporal queries | Complexity, storage, learning curve |

See all three before you commit.

## Workflow

### Step 1-4: Prerequisites, Parse, Variables, Directories

(Same pattern as fusion-algorithm.md with appropriate substitutions)

**Variables** (in Step 3):
```
GEMINI_MODEL = "gemini-3-pro-preview"  # Data model design = schema generation, use Pro
```

### Step 5: Create Git Worktrees

```bash
# Worker A - Normalized/Relational design
git worktree add "{WORKTREE_ROOT}/impl-a" -b fusion/{SESSION_ID}/impl-a

# Worker B - Denormalized/Document design
git worktree add "{WORKTREE_ROOT}/impl-b" -b fusion/{SESSION_ID}/impl-b

# Worker C - Event-sourced/CQRS design
git worktree add "{WORKTREE_ROOT}/impl-c" -b fusion/{SESSION_ID}/impl-c
```

### Step 6: Create tasks.json

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "F-Thread (Fusion)",
  "task_type": "fusion-datamodel",
  "domain": {
    "description": "{DOMAIN_DESC}",
    "slug": "{DOMAIN_SLUG}"
  },
  "base_branch": "{BASE_BRANCH}",
  "worktrees": {
    "impl-a": {
      "path": "{WORKTREE_ROOT}/impl-a",
      "branch": "fusion/{SESSION_ID}/impl-a",
      "worker": "worker-a",
      "provider": "claude-opus",
      "philosophy": "normalized-relational",
      "status": "pending"
    },
    "impl-b": {
      "path": "{WORKTREE_ROOT}/impl-b",
      "branch": "fusion/{SESSION_ID}/impl-b",
      "worker": "worker-b",
      "provider": "gemini-3-pro",
      "philosophy": "denormalized-document",
      "status": "pending"
    },
    "impl-c": {
      "path": "{WORKTREE_ROOT}/impl-c",
      "branch": "fusion/{SESSION_ID}/impl-c",
      "worker": "worker-c",
      "provider": "codex-gpt-5.2",
      "philosophy": "event-sourced-cqrs",
      "status": "pending"
    }
  },
  "evaluation": {
    "status": "pending",
    "criteria": ["query_complexity", "write_performance", "read_performance", "flexibility", "data_integrity"],
    "winner": null
  }
}
```

### Step 7: Create Judge Queen Prompt

```markdown
# Judge Queen - Data Model Fusion Evaluator

You are the **Judge Queen** for an F-Thread data model design session.

## Your Mission

Three workers are designing data models for the same domain with different philosophies. Your job is to:
1. Monitor their progress
2. Evaluate trade-offs for the user's specific needs
3. Help the user pick the right model

## Domain to Model

**{DOMAIN_DESC}**

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Thread Type**: F-Thread (Fusion) - Competing data philosophies

## Data Model Philosophies

| Worker | Philosophy | Best When |
|--------|------------|-----------|
| worker-a | Normalized/Relational | Complex queries, data integrity critical, schema may evolve |
| worker-b | Denormalized/Document | Read-heavy, predictable access patterns, scale horizontally |
| worker-c | Event-sourced/CQRS | Audit requirements, temporal queries, complex domains |

## Evaluation Framework

### Query Pattern Analysis

For each model, evaluate these common operations:

```sql
-- 1. Single entity fetch
-- How hard is it to get one complete record?

-- 2. List with filters
-- How hard is it to list/search with multiple filters?

-- 3. Aggregations
-- How hard is it to compute counts, sums, averages?

-- 4. Related data
-- How hard is it to get an entity with its relationships?

-- 5. Updates
-- How hard is it to update data consistently?

-- 6. Historical queries (if applicable)
-- Can you query "what was the state at time X"?
```

### Trade-off Matrix

| Criteria | Normalized | Denormalized | Event-Sourced |
|----------|------------|--------------|---------------|
| Write simplicity | Medium | Easy | Complex |
| Read simplicity | Complex (joins) | Easy | Medium (projections) |
| Data integrity | Excellent | Manual | Excellent |
| Schema flexibility | High | Low | High |
| Horizontal scale | Hard | Easy | Medium |
| Audit trail | Manual | Manual | Built-in |
| Storage efficiency | High | Low | Medium |

## Generate Comparison Report

Write to `.hive/sessions/{SESSION_ID}/evaluation.md`:

```markdown
# Data Model Fusion Evaluation

## Domain: {DOMAIN_DESC}

## Schema Comparison

### Model A: Normalized/Relational

**Tables**: [list]
**Relationships**: [list]
**Indexes**: [list]

```sql
-- Key schema DDL
```

### Model B: Denormalized/Document

**Collections/Tables**: [list]
**Embedded Documents**: [list]
**Indexes**: [list]

```sql
-- Key schema DDL or document structure
```

### Model C: Event-Sourced/CQRS

**Event Types**: [list]
**Projections**: [list]
**Read Models**: [list]

```sql
-- Event schema and projection queries
```

## Query Comparison

### Query 1: [Common operation]

**Normalized (A)**:
```sql
SELECT ... FROM ... JOIN ... WHERE ...
```
Complexity: X joins, Y conditions

**Denormalized (B)**:
```sql
SELECT ... FROM ... WHERE ...
```
Complexity: Single table, embedded data

**Event-Sourced (C)**:
```sql
SELECT ... FROM read_model WHERE ...
```
Complexity: Pre-computed projection

### Query 2: [Another common operation]
[Same format]

## Trade-off Analysis

| Factor | Model A | Model B | Model C |
|--------|---------|---------|---------|
| Query complexity | X/10 | X/10 | X/10 |
| Write performance | X/10 | X/10 | X/10 |
| Read performance | X/10 | X/10 | X/10 |
| Flexibility | X/10 | X/10 | X/10 |
| Data integrity | X/10 | X/10 | X/10 |
| **Total** | **X/50** | **X/50** | **X/50** |

## Recommendation Matrix

| If Your Priority Is... | Choose |
|------------------------|--------|
| Data integrity & complex reporting | Model A (Normalized) |
| Read performance & simple queries | Model B (Denormalized) |
| Audit trail & temporal queries | Model C (Event-Sourced) |

## Final Recommendation

**For {DOMAIN_DESC}**, I recommend: **{MODEL}**

### Reasoning
[Why this model fits the domain best]

### Migration Path
[How to evolve if needs change]

### Warnings
[Potential issues to watch for]
```

## Questions to Ask User

Before declaring a winner, ask:
1. What's your read:write ratio?
2. Do you need audit/history?
3. How complex are your queries?
4. What's your scale target?
5. What's your team's familiarity with each approach?
```

### Step 8: Create Worker Prompts

**Worker A** (Normalized/Relational):
```markdown
# Worker A - Normalized/Relational Data Model

## Your Mission
Design a data model for **{DOMAIN_DESC}** using normalized relational design.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-a
- **Branch**: fusion/{SESSION_ID}/impl-a

## Design Philosophy: Normalized/Relational

Core principles:
- **3rd Normal Form (3NF)** minimum
- **Single source of truth** for each fact
- **Foreign keys** for relationships
- **No data duplication**
- **Referential integrity** enforced

## Design Process

1. **Identify entities** - What are the core nouns?
2. **Define attributes** - What properties does each have?
3. **Establish relationships** - How do entities relate?
4. **Normalize** - Eliminate redundancy
5. **Add indexes** - Optimize common queries
6. **Write migrations** - Implement the schema

## Deliverables

### Required Files

1. **Schema file** (e.g., `schema.prisma`, `schema.sql`, `migrations/`)
   - All tables with columns and types
   - Primary keys and foreign keys
   - Indexes for common queries
   - Constraints (unique, not null, check)

2. **Entity diagram** (`docs/erd.md`)
   - ASCII or mermaid diagram of relationships

3. **Type definitions** (`types/models.ts`)
   - TypeScript interfaces for each entity

4. **Example queries** (`docs/queries.md`)
   - Common CRUD operations
   - Complex queries with joins
   - Aggregation examples

### Schema Template

```sql
-- Example normalized schema
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE order_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
  product_id UUID REFERENCES products(id),
  quantity INTEGER NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL
);

-- Indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
```

## Normalization Checklist

- [ ] 1NF: No repeating groups, atomic values
- [ ] 2NF: No partial dependencies
- [ ] 3NF: No transitive dependencies
- [ ] Foreign keys for all relationships
- [ ] Indexes on foreign keys and query filters

## Begin

Announce: "Worker A designing normalized/relational model for {DOMAIN_DESC}"
```

**Worker B** (Denormalized/Document):
```markdown
# Worker B - Denormalized/Document Data Model

## Your Mission
Design a data model for **{DOMAIN_DESC}** using denormalized document design.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-b
- **Branch**: fusion/{SESSION_ID}/impl-b

## Design Philosophy: Denormalized/Document

Core principles:
- **Embed related data** where accessed together
- **Optimize for read patterns** not write
- **Accept duplication** for performance
- **Document = complete unit** for most queries
- **Horizontal scalability** friendly

## Design Process

1. **Identify access patterns** - How will data be queried?
2. **Design documents** - What's fetched together lives together
3. **Choose embedding vs referencing** - Balance duplication vs joins
4. **Plan for updates** - How to keep duplicates in sync
5. **Add indexes** - Support query patterns

## Deliverables

### Required Files

1. **Schema/Collection design** (`schema/collections.ts`)
   - Document structures with embedded data
   - Reference patterns where needed

2. **Document examples** (`docs/document-examples.md`)
   - Sample documents showing structure

3. **Type definitions** (`types/models.ts`)
   - TypeScript interfaces

4. **Example queries** (`docs/queries.md`)
   - Common operations
   - How embedding simplifies reads

### Document Design Template

```typescript
// Example denormalized document
interface Order {
  _id: ObjectId;
  orderNumber: string;
  status: 'pending' | 'shipped' | 'delivered';
  createdAt: Date;

  // Embedded customer (denormalized)
  customer: {
    id: string;
    name: string;
    email: string;
    // Snapshot at order time
  };

  // Embedded items (no separate collection)
  items: Array<{
    productId: string;
    productName: string;  // Denormalized
    sku: string;          // Denormalized
    quantity: number;
    unitPrice: number;
    subtotal: number;     // Pre-computed
  }>;

  // Pre-computed aggregates
  totals: {
    subtotal: number;
    tax: number;
    shipping: number;
    total: number;
  };

  // Embedded shipping (no join needed)
  shipping: {
    address: Address;
    method: string;
    trackingNumber?: string;
  };
}
```

## Embedding Decision Matrix

| Relationship | Embed When | Reference When |
|--------------|------------|----------------|
| 1:1 | Almost always | Rarely accessed |
| 1:Few | Usually | Large/volatile data |
| 1:Many | If bounded | Unbounded growth |
| Many:Many | Embed IDs | Need bidirectional |

## Duplication Strategy

Document which fields are duplicated and how to sync:
- Customer name in orders → Update on customer change? Or snapshot?
- Product name in items → Snapshot at order time (immutable)

## Begin

Announce: "Worker B designing denormalized/document model for {DOMAIN_DESC}"
```

**Worker C** (Event-Sourced/CQRS):
```markdown
# Worker C - Event-Sourced/CQRS Data Model

## Your Mission
Design a data model for **{DOMAIN_DESC}** using event sourcing and CQRS.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-c
- **Branch**: fusion/{SESSION_ID}/impl-c

## Design Philosophy: Event-Sourced/CQRS

Core principles:
- **Events are the source of truth** (not current state)
- **State is derived** from replaying events
- **Commands** mutate (write side)
- **Queries** read from **projections** (read side)
- **Full audit trail** built-in
- **Temporal queries** possible

## Design Process

1. **Identify aggregates** - Consistency boundaries
2. **Define events** - What facts occur?
3. **Design commands** - What actions are allowed?
4. **Build projections** - Read models for queries
5. **Plan event handlers** - How projections update

## Deliverables

### Required Files

1. **Event definitions** (`events/`)
   - All domain events with schemas

2. **Command handlers** (`commands/`)
   - Validation and event emission

3. **Projections** (`projections/`)
   - Read models built from events

4. **Type definitions** (`types/`)
   - Events, commands, read models

5. **Example flows** (`docs/flows.md`)
   - Command → Events → Projection updates

### Event Design Template

```typescript
// Domain Events
interface OrderCreated {
  type: 'OrderCreated';
  aggregateId: string;
  timestamp: Date;
  payload: {
    customerId: string;
    items: Array<{ productId: string; quantity: number; price: number }>;
  };
}

interface OrderItemAdded {
  type: 'OrderItemAdded';
  aggregateId: string;
  timestamp: Date;
  payload: {
    productId: string;
    quantity: number;
    price: number;
  };
}

interface OrderShipped {
  type: 'OrderShipped';
  aggregateId: string;
  timestamp: Date;
  payload: {
    trackingNumber: string;
    carrier: string;
  };
}

// Event Store Schema
CREATE TABLE events (
  id UUID PRIMARY KEY,
  aggregate_type VARCHAR(100) NOT NULL,
  aggregate_id UUID NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  payload JSONB NOT NULL,
  metadata JSONB,
  timestamp TIMESTAMP NOT NULL,
  version INTEGER NOT NULL,

  UNIQUE(aggregate_id, version)
);

// Read Model (Projection)
CREATE TABLE order_summary (
  id UUID PRIMARY KEY,
  customer_id UUID,
  status VARCHAR(50),
  item_count INTEGER,
  total_amount DECIMAL(10,2),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### CQRS Structure

```
Commands (Write)          Events              Projections (Read)
─────────────────         ──────              ──────────────────
CreateOrder      →   OrderCreated      →   order_summary
AddItem          →   OrderItemAdded    →   order_details
ShipOrder        →   OrderShipped      →   shipping_status
                                       →   customer_orders
                                       →   daily_sales_report
```

## Key Decisions to Document

1. **Aggregate boundaries** - What's the consistency unit?
2. **Event granularity** - Fine (ItemAdded) vs coarse (OrderUpdated)?
3. **Snapshot strategy** - When to snapshot for performance?
4. **Projection rebuild** - How to rebuild if logic changes?

## Begin

Announce: "Worker C designing event-sourced/CQRS model for {DOMAIN_DESC}"
```

### Step 9: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# mprocs configuration for Fusion Data Model session: {SESSION_ID}
# Gemini CLI: using latest installed version
procs:
  judge-queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the JUDGE QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "judge-queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      FUSION_TYPE: "datamodel"

  worker-a-opus:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are WORKER A. Read .hive/sessions/{SESSION_ID}/worker-a-prompt.md"]
    cwd: "{WORKTREE_ROOT}/impl-a"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "a"
      FUSION_APPROACH: "normalized-relational"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-b-gemini:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER B. Read .hive/sessions/{SESSION_ID}/worker-b-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-b"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "b"
      FUSION_APPROACH: "denormalized-document"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-c-gpt:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER C. Read .hive/sessions/{SESSION_ID}/worker-c-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-c"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "c"
      FUSION_APPROACH: "event-sourced-cqrs"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 5 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

### Variance Workers (Optional)

**If VARIANCE >= 2, add Worker D (GLM 4.7 - Graph/Network model):**

```yaml
  worker-d-glm:
    cmd: ["powershell", "-NoProfile", "-Command", "cd '{WORKTREE_ROOT}/impl-d'; $env:OPENCODE_YOLO='true'; opencode run --format default -m opencode/glm-4.7-free 'You are WORKER D. Design using a graph/network data model. Focus on Neo4j-style relationships, graph traversals, and connected data patterns.'"]
    cwd: "{WORKTREE_ROOT}/impl-d"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "d"
      FUSION_APPROACH: "graph-network"
```

Create additional worktrees for variance workers:
```bash
# If VARIANCE >= 2:
git worktree add "{WORKTREE_ROOT}/impl-d" -b fusion/{SESSION_ID}/impl-d
```

### Step 10-12: Create logs, launch mprocs, output status

(Same pattern as fusion-algorithm.md)

### Output Status

```markdown
## Fusion Data Model Arena Launched!

**Thread Type**: F-Thread (True Fusion)
**Session**: {SESSION_ID}
**Domain**: {DOMAIN_DESC}

### Competing Data Philosophies

| Worker | Philosophy | Optimizes For |
|--------|------------|---------------|
| Worker A | Normalized/Relational | Data integrity, complex queries |
| Worker B | Denormalized/Document | Read performance, simplicity |
| Worker C | Event-Sourced/CQRS | Audit trail, temporal queries |

### What You'll Get

Each worker produces:
- Complete schema/migrations
- Type definitions
- Example queries
- Trade-off documentation

### Why This Matters

Data model decisions are **expensive to change**:
- Normalized → Denormalized: Major migration
- Denormalized → Event-sourced: Rewrite
- Wrong choice → Technical debt for years

See all three approaches before you commit!

### Evaluation Criteria

1. Query complexity for your use cases
2. Write vs read performance balance
3. Schema flexibility for future changes
4. Data integrity requirements
5. Audit/compliance needs

Watch three data philosophies model the same domain!
```
