---
description: F-Thread - Competing architecture patterns in separate worktrees, evaluate trade-offs for your scale
argument-hint: "<system-or-feature-description>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Fusion Arch - True F-Thread Architecture Pattern Arena

Launch 3-5 workers (based on variance level) in **separate git worktrees** to architect the same system with different patterns. A Judge Queen evaluates trade-offs for your specific scale and needs.

## Thread Type: F-Thread (Fusion)

This is a TRUE fusion thread for architecture decisions:
- **Divergent worktrees**: Each worker designs a different architecture
- **Real artifacts**: Actual project structure, configs, and code
- **Trade-off analysis**: Evaluate for YOUR scale and team
- **Best-of-N selection**: Right architecture for YOUR context wins

## Arguments

- `<system-or-feature-description>`: What to architect (e.g., "e-commerce platform", "real-time chat", "data pipeline")
- `--variance N`: Model diversity level (1-3, default: 1)
  - **Variance 1** (default): 3 workers (Opus, Gemini Pro, GPT-5.2)
  - **Variance 2**: 4 workers (+GLM 4.7 via OpenCode)

## Why F-Thread for Architecture?

Architecture decisions are **extremely expensive to change**:

| Pattern | Best At | Struggles At |
|---------|---------|--------------|
| Monolith | Starting, small teams, shared data | Scale, independent deployment |
| Microservices | Scale, team autonomy, fault isolation | Complexity, data consistency |
| Modular Monolith | Balance, clear boundaries, easier refactor | Eventually needs splitting |

The right choice depends on YOUR context. See all three.

## Workflow

### Step 1-4: Prerequisites, Parse, Variables, Directories

(Same pattern as fusion-algorithm.md with appropriate substitutions)

**Variables** (in Step 3):
```
GEMINI_MODEL = "gemini-3-pro-preview"  # Architecture design = code generation, use Pro
```

### Step 5: Create Git Worktrees

```bash
# Worker A - Monolith architecture
git worktree add "{WORKTREE_ROOT}/impl-a" -b fusion/{SESSION_ID}/impl-a

# Worker B - Microservices architecture
git worktree add "{WORKTREE_ROOT}/impl-b" -b fusion/{SESSION_ID}/impl-b

# Worker C - Modular Monolith architecture
git worktree add "{WORKTREE_ROOT}/impl-c" -b fusion/{SESSION_ID}/impl-c
```

### Step 6: Create tasks.json

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "F-Thread (Fusion)",
  "task_type": "fusion-arch",
  "system": {
    "description": "{SYSTEM_DESC}",
    "slug": "{SYSTEM_SLUG}"
  },
  "base_branch": "{BASE_BRANCH}",
  "worktrees": {
    "impl-a": {
      "path": "{WORKTREE_ROOT}/impl-a",
      "branch": "fusion/{SESSION_ID}/impl-a",
      "worker": "worker-a",
      "provider": "claude-opus",
      "pattern": "monolith",
      "status": "pending"
    },
    "impl-b": {
      "path": "{WORKTREE_ROOT}/impl-b",
      "branch": "fusion/{SESSION_ID}/impl-b",
      "worker": "worker-b",
      "provider": "gemini-3-pro",
      "pattern": "microservices",
      "status": "pending"
    },
    "impl-c": {
      "path": "{WORKTREE_ROOT}/impl-c",
      "branch": "fusion/{SESSION_ID}/impl-c",
      "worker": "worker-c",
      "provider": "codex-gpt-5.2",
      "pattern": "modular-monolith",
      "status": "pending"
    }
  },
  "evaluation": {
    "status": "pending",
    "criteria": ["complexity", "scalability", "team_fit", "operational_cost", "time_to_market"],
    "winner": null
  }
}
```

### Step 7: Create Judge Queen Prompt

```markdown
# Judge Queen - Architecture Fusion Evaluator

You are the **Judge Queen** for an F-Thread architecture design session.

## Your Mission

Three workers are architecting the same system with different patterns. Your job is to:
1. Monitor their progress
2. Evaluate trade-offs for the user's specific context
3. Help pick the right architecture

## System to Architect

**{SYSTEM_DESC}**

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Thread Type**: F-Thread (Fusion) - Competing architectures

## Architecture Patterns

| Worker | Pattern | Characteristics |
|--------|---------|-----------------|
| worker-a | Monolith | Single deployable, shared database, simple ops |
| worker-b | Microservices | Independent services, separate DBs, complex ops |
| worker-c | Modular Monolith | Single deployable, clear module boundaries, middle ground |

## Context Questions

Before evaluating, understand the user's context:

1. **Team size**: How many developers?
2. **Scale expectations**: Users/requests expected?
3. **Deployment frequency**: How often do you ship?
4. **Operational maturity**: DevOps experience?
5. **Timeline**: MVP speed vs long-term?
6. **Domain complexity**: How many bounded contexts?

## Evaluation Framework

### Complexity Analysis

| Aspect | Monolith | Microservices | Modular Mono |
|--------|----------|---------------|--------------|
| Initial setup | Low | High | Medium |
| Local dev | Easy | Complex | Easy |
| Debugging | Easy | Hard | Easy |
| Deployment | Simple | Complex | Simple |
| Testing | Simple | Complex | Medium |

### Scalability Analysis

| Aspect | Monolith | Microservices | Modular Mono |
|--------|----------|---------------|--------------|
| Vertical scale | Yes | N/A | Yes |
| Horizontal scale | Limited | Excellent | Limited |
| Independent scale | No | Yes | No |
| Data scale | Shared DB limits | Per-service DBs | Shared DB limits |

### Team Fit Analysis

| Aspect | Monolith | Microservices | Modular Mono |
|--------|----------|---------------|--------------|
| Small team (1-5) | Excellent | Overkill | Good |
| Medium team (5-20) | Good | Possible | Excellent |
| Large team (20+) | Challenging | Excellent | Good |
| Junior-heavy | Excellent | Risky | Good |

### Operational Cost

| Aspect | Monolith | Microservices | Modular Mono |
|--------|----------|---------------|--------------|
| Infrastructure | $ | $$$ | $ |
| Monitoring | Simple | Complex | Simple |
| On-call burden | Low | High | Low |
| CI/CD complexity | Low | High | Low |

## Generate Comparison Report

Write to `.hive/sessions/{SESSION_ID}/evaluation.md`:

```markdown
# Architecture Fusion Evaluation

## System: {SYSTEM_DESC}

## Architecture Comparison

### Visual Overview

**Monolith (A)**
```
┌─────────────────────────────────────┐
│            Application              │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│  │ UI  │ │ API │ │ Svc │ │ Svc │   │
│  └─────┘ └─────┘ └─────┘ └─────┘   │
│         ┌─────────────────┐         │
│         │    Database     │         │
│         └─────────────────┘         │
└─────────────────────────────────────┘
```

**Microservices (B)**
```
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│Svc A │ │Svc B │ │Svc C │ │Svc D │
│ DB A │ │ DB B │ │ DB C │ │ DB D │
└──┬───┘ └──┬───┘ └──┬───┘ └──┬───┘
   └────────┴────┬───┴────────┘
            ┌────┴────┐
            │API Gate │
            └─────────┘
```

**Modular Monolith (C)**
```
┌─────────────────────────────────────┐
│  ┌─────────┐ ┌─────────┐ ┌───────┐ │
│  │Module A │ │Module B │ │Mod C  │ │
│  │ ─────── │ │ ─────── │ │ ───── │ │
│  │  API    │ │  API    │ │ API   │ │
│  │  Logic  │ │  Logic  │ │ Logic │ │
│  │  Data   │ │  Data   │ │ Data  │ │
│  └─────────┘ └─────────┘ └───────┘ │
│         ┌─────────────────┐         │
│         │ Shared Database │         │
│         │  (Schema per    │         │
│         │    module)      │         │
│         └─────────────────┘         │
└─────────────────────────────────────┘
```

## Project Structure Comparison

### Monolith (A)
```
/src
  /controllers
  /services
  /models
  /utils
/tests
package.json
```

### Microservices (B)
```
/services
  /user-service
    /src
    package.json
    Dockerfile
  /order-service
    /src
    package.json
    Dockerfile
  /payment-service
    ...
/infrastructure
  docker-compose.yml
  k8s/
```

### Modular Monolith (C)
```
/src
  /modules
    /users
      /api
      /domain
      /data
      index.ts  # Public API
    /orders
      /api
      /domain
      /data
      index.ts
    /payments
      ...
  /shared
    /kernel
/tests
package.json
```

## Trade-off Matrix

| Factor | Monolith (A) | Microservices (B) | Modular Mono (C) |
|--------|--------------|-------------------|------------------|
| Time to MVP | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Long-term scale | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Operational cost | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Team autonomy | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Code coupling | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Refactor ease | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |

## Recommendation Matrix

| If You Are... | Choose |
|---------------|--------|
| Startup, proving product-market fit | Monolith (A) |
| Scale-up, 50+ engineers, proven product | Microservices (B) |
| Growing, want to keep options open | Modular Monolith (C) |

## Migration Paths

```
Monolith → Modular Monolith → Microservices
   (A)           (C)              (B)
         Easy          Possible
```

**Key insight**: Modular Monolith (C) is the best "option-preserving" choice. You can:
- Extract to microservices later if needed
- Keep as monolith if scale doesn't require splitting
- Clear boundaries make future decisions easier

## Final Recommendation

**For {SYSTEM_DESC}**: **{PATTERN}**

### Why
[Explanation based on context]

### Evolution Strategy
[How to evolve if needs change]

### Red Flags to Watch
[Signs you need to reconsider]
```
```

### Step 8: Create Worker Prompts

**Worker A** (Monolith):
```markdown
# Worker A - Monolith Architecture

## Your Mission
Architect **{SYSTEM_DESC}** as a well-structured monolith.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-a
- **Branch**: fusion/{SESSION_ID}/impl-a

## Pattern: Monolith

A single deployable application with all functionality in one codebase.

## Principles

- **Simplicity first**: One repo, one deploy, one database
- **Layered architecture**: Controllers → Services → Repositories
- **Shared code is fine**: Utils, helpers, common logic
- **Single database**: All data in one place
- **Fast to build**: Minimize ceremony

## Deliverables

### 1. Project Structure
```
/src
  /controllers      # HTTP handlers
  /services         # Business logic
  /repositories     # Data access
  /models           # Domain entities
  /utils            # Shared helpers
  /middleware       # Auth, logging, etc
  /config           # Configuration
  app.ts            # Entry point
/tests
  /unit
  /integration
/docs
  architecture.md
package.json
Dockerfile
docker-compose.yml
```

### 2. Key Files to Create

- `src/app.ts` - Application setup
- `src/config/index.ts` - Configuration
- `docker-compose.yml` - Local development
- `docs/architecture.md` - Architecture docs

### 3. Sample Service Implementation

```typescript
// src/services/orderService.ts
export class OrderService {
  constructor(
    private orderRepo: OrderRepository,
    private userRepo: UserRepository,
    private paymentService: PaymentService
  ) {}

  async createOrder(userId: string, items: OrderItem[]): Promise<Order> {
    const user = await this.userRepo.findById(userId);
    if (!user) throw new NotFoundError('User not found');

    const order = await this.orderRepo.create({
      userId,
      items,
      total: this.calculateTotal(items),
      status: 'pending'
    });

    await this.paymentService.processPayment(order);
    return order;
  }
}
```

## Best Practices

- Keep services focused but not too granular
- Use dependency injection for testability
- Transaction boundaries are simple (single DB)
- Use feature flags for gradual rollouts

## Anti-patterns to Avoid

- Don't create "microservices in a monolith" (over-abstraction)
- Don't skip tests because "it's all together"
- Don't ignore code organization

## Begin

Announce: "Worker A architecting {SYSTEM_DESC} as a monolith"
```

**Worker B** (Microservices):
```markdown
# Worker B - Microservices Architecture

## Your Mission
Architect **{SYSTEM_DESC}** as a microservices system.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-b
- **Branch**: fusion/{SESSION_ID}/impl-b

## Pattern: Microservices

Independent, separately deployable services that communicate over the network.

## Principles

- **Single responsibility**: Each service does one thing well
- **Independent deployment**: Deploy without coordinating
- **Database per service**: No shared databases
- **Smart endpoints, dumb pipes**: Logic in services, not middleware
- **Design for failure**: Services will fail, handle it

## Deliverables

### 1. Project Structure
```
/services
  /user-service
    /src
      /api
      /domain
      /data
      app.ts
    package.json
    Dockerfile
    README.md
  /order-service
    /src
    package.json
    Dockerfile
  /payment-service
    /src
    package.json
    Dockerfile
  /notification-service
    /src
    package.json
    Dockerfile
/api-gateway
  /src
  package.json
  Dockerfile
/shared
  /proto         # gRPC definitions
  /events        # Event schemas
/infrastructure
  docker-compose.yml
  k8s/
    /user-service
    /order-service
    ...
/docs
  architecture.md
  service-map.md
  runbook.md
```

### 2. Service Communication

```
┌──────────────┐
│  API Gateway │
└──────┬───────┘
       │ HTTP/REST
┌──────┴───────┐
│   Services   │◄──── Sync: REST/gRPC
└──────┬───────┘      Async: Events/Queue
       │
┌──────┴───────┐
│ Message Bus  │  (RabbitMQ/Kafka/SQS)
└──────────────┘
```

### 3. Key Files to Create

- `docker-compose.yml` - Local multi-service dev
- `docs/architecture.md` - System overview
- `docs/service-map.md` - Service interactions
- Each service: Dockerfile, package.json, README

### 4. Sample Service

```typescript
// services/order-service/src/app.ts
const app = express();

// Health check (required for k8s)
app.get('/health', (req, res) => res.json({ status: 'ok' }));

// Service API
app.post('/orders', async (req, res) => {
  const order = await orderService.create(req.body);

  // Publish event for other services
  await messageBus.publish('order.created', {
    orderId: order.id,
    userId: order.userId,
    total: order.total
  });

  res.status(201).json(order);
});
```

### 5. Event Contracts

```typescript
// shared/events/order-events.ts
interface OrderCreatedEvent {
  type: 'order.created';
  orderId: string;
  userId: string;
  total: number;
  timestamp: string;
}

interface OrderShippedEvent {
  type: 'order.shipped';
  orderId: string;
  trackingNumber: string;
  timestamp: string;
}
```

## Infrastructure Requirements

- Container orchestration (K8s, ECS, etc)
- Service discovery
- API Gateway
- Message bus
- Distributed tracing
- Centralized logging

## Anti-patterns to Avoid

- Distributed monolith (services too coupled)
- Shared database between services
- Synchronous chains (A → B → C → D)
- No circuit breakers

## Begin

Announce: "Worker B architecting {SYSTEM_DESC} as microservices"
```

**Worker C** (Modular Monolith):
```markdown
# Worker C - Modular Monolith Architecture

## Your Mission
Architect **{SYSTEM_DESC}** as a modular monolith.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-c
- **Branch**: fusion/{SESSION_ID}/impl-c

## Pattern: Modular Monolith

A single deployable with **strict module boundaries** that could become microservices later.

## Principles

- **Clear boundaries**: Modules communicate through defined interfaces
- **No cross-module imports**: Only through public API
- **Schema separation**: Each module owns its tables
- **Single deploy, multiple concerns**: Best of both worlds
- **Extraction-ready**: Can split modules later

## Deliverables

### 1. Project Structure
```
/src
  /modules
    /users
      /api             # Public interface (exported)
        index.ts       # Module public API
        types.ts       # Public types
      /internal        # Private implementation
        /domain
        /data
        /services
      module.ts        # Module registration
    /orders
      /api
        index.ts
        types.ts
      /internal
        /domain
        /data
        /services
      module.ts
    /payments
      ...
    /notifications
      ...
  /shared
    /kernel           # Shared domain primitives
    /infrastructure   # Database, messaging, etc
  /app
    app.ts            # Composition root
    modules.ts        # Module registry
/tests
  /modules
    /users
    /orders
/docs
  architecture.md
  module-dependencies.md
package.json
Dockerfile
```

### 2. Module Boundary Rules

```typescript
// ✅ ALLOWED: Import from module's public API
import { UserService, User } from '@modules/users/api';

// ❌ FORBIDDEN: Import from module's internals
import { UserRepository } from '@modules/users/internal/data';

// ✅ ALLOWED: Import from shared kernel
import { Money, Email } from '@shared/kernel';
```

### 3. Module Public API

```typescript
// src/modules/users/api/index.ts
// This is the ONLY export from the users module

export { UserService } from './services';
export type { User, CreateUserInput } from './types';

// Internal implementation is hidden
// Other modules can ONLY use what's exported here
```

### 4. Inter-Module Communication

```typescript
// Option 1: Direct calls through public API
class OrderService {
  constructor(private userService: UserService) {}

  async createOrder(userId: string) {
    const user = await this.userService.getById(userId);
    // ...
  }
}

// Option 2: Events (preferred for loose coupling)
class OrderService {
  async createOrder(userId: string) {
    const order = await this.orderRepo.create(...);

    // Emit event, don't call other modules directly
    await this.events.emit('order.created', { orderId: order.id });
  }
}

// In notifications module
events.on('order.created', async (event) => {
  await notificationService.sendOrderConfirmation(event.orderId);
});
```

### 5. Database Schema Separation

```sql
-- Each module owns its schema
CREATE SCHEMA users;
CREATE SCHEMA orders;
CREATE SCHEMA payments;

-- Tables prefixed or in schema
CREATE TABLE users.users (...);
CREATE TABLE users.profiles (...);

CREATE TABLE orders.orders (...);
CREATE TABLE orders.order_items (...);

-- Cross-module references use IDs only, no FKs across schemas
-- This makes future extraction easier
```

### 6. Module Dependency Rules

```
┌─────────────────────────────────────────┐
│              Application                │
│  ┌─────────────────────────────────┐   │
│  │           Modules               │   │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ │   │
│  │  │ Users │→│Orders │→│Payment│ │   │
│  │  └───────┘ └───────┘ └───────┘ │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │         Shared Kernel           │   │
│  │   (No module can depend on      │   │
│  │    another's internals)         │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Enforcement

```typescript
// eslint config or import linter
{
  "rules": {
    "no-restricted-imports": [
      "error",
      {
        "patterns": [
          "@modules/*/internal/*"  // Can't import internals
        ]
      }
    ]
  }
}
```

## Why This Pattern?

1. **Start fast**: Single deploy, simple ops
2. **Stay organized**: Clear boundaries from day 1
3. **Extract later**: Modules can become services
4. **Avoid big rewrite**: Incremental evolution

## Begin

Announce: "Worker C architecting {SYSTEM_DESC} as a modular monolith"
```

### Output Status

```markdown
## Fusion Architecture Arena Launched!

**Thread Type**: F-Thread (True Fusion)
**Session**: {SESSION_ID}
**System**: {SYSTEM_DESC}

### Competing Architecture Patterns

| Worker | Pattern | Deploy Unit | Database |
|--------|---------|-------------|----------|
| Worker A | Monolith | Single app | Single DB |
| Worker B | Microservices | Many services | DB per service |
| Worker C | Modular Monolith | Single app | Single DB, schema per module |

### Trade-off Spectrum

```
Simple ◄─────────────────────────────────► Complex
Fast   ◄─────────────────────────────────► Scalable

       Monolith    Modular     Microservices
          │        Monolith          │
          ▼           ▼              ▼
        ████       ████████      ████████████
        Simple     Balanced      Complex
        Fast       Flexible      Scalable
```

### Key Questions

The right architecture depends on:
1. **Team size** - How many developers?
2. **Scale** - How many users/requests?
3. **Complexity** - How many bounded contexts?
4. **Timeline** - MVP speed vs long-term?
5. **Ops maturity** - DevOps experience?

### The Evolution Path

Most successful systems follow:
```
Monolith → Modular Monolith → Microservices
                 ↑
         (Best starting point for most)
```

Watch three architecture philosophies take shape!
```

### Step 9: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# mprocs configuration for Fusion Arch session: {SESSION_ID}
# Gemini CLI: using latest installed version
procs:
  judge-queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the JUDGE QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "judge-queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      FUSION_TYPE: "arch"

  worker-a-opus:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are WORKER A. Read .hive/sessions/{SESSION_ID}/worker-a-prompt.md"]
    cwd: "{WORKTREE_ROOT}/impl-a"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "a"
      FUSION_APPROACH: "monolith"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-b-gemini:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER B. Read .hive/sessions/{SESSION_ID}/worker-b-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-b"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "b"
      FUSION_APPROACH: "microservices"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-c-gpt:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER C. Read .hive/sessions/{SESSION_ID}/worker-c-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-c"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "c"
      FUSION_APPROACH: "modular-monolith"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 5 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

### Variance Workers (Optional)

**If VARIANCE >= 2, add Worker D (GLM 4.7 - Serverless/Event-driven approach):**

```yaml
  worker-d-glm:
    cmd: ["powershell", "-NoProfile", "-Command", "cd '{WORKTREE_ROOT}/impl-d'; $env:OPENCODE_YOLO='true'; opencode run --format default -m opencode/glm-4.7-free 'You are WORKER D. Architect using a serverless/event-driven pattern. Focus on Lambda/Functions, message queues, and event sourcing.'"]
    cwd: "{WORKTREE_ROOT}/impl-d"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "d"
      FUSION_APPROACH: "serverless-event"
```

Create additional worktrees for variance workers:
```bash
# If VARIANCE >= 2:
git worktree add "{WORKTREE_ROOT}/impl-d" -b fusion/{SESSION_ID}/impl-d
```
