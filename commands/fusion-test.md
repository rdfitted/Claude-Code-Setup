---
description: F-Thread - Competing test strategies in separate worktrees, evaluate coverage and confidence
argument-hint: "<feature-or-module-to-test>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Fusion Test - True F-Thread Testing Strategy Arena

Launch 3-5 workers (based on variance level) in **separate git worktrees** to create test suites with different philosophies. A Judge Queen evaluates which strategy provides the best coverage/confidence balance.

## Thread Type: F-Thread (Fusion)

This is a TRUE fusion thread for test strategy:
- **Divergent worktrees**: Each worker builds a different test suite
- **Real artifacts**: Actual runnable tests
- **Coverage analysis**: Measure what each approach catches
- **Best-of-N selection**: Right strategy for YOUR codebase wins

## Arguments

- `<feature-or-module-to-test>`: What to test (e.g., "checkout flow", "auth module", "API endpoints")
- `--variance N`: Model diversity level (1-3, default: 1)
  - **Variance 1** (default): 3 workers (Opus, Gemini Pro, GPT-5.2)
  - **Variance 2**: 4 workers (+GLM 4.7 via OpenCode)

## Why F-Thread for Testing?

Testing philosophies are contentious. Different approaches have real trade-offs:

| Philosophy | Catches | Misses | Cost |
|------------|---------|--------|------|
| Unit-heavy | Logic bugs | Integration issues | Low |
| Integration-heavy | System bugs | Edge cases | Medium |
| E2E-heavy | User-facing bugs | Root cause | High |

See all three before committing to a strategy.

## Workflow

### Step 1-4: Prerequisites, Parse, Variables, Directories

(Same pattern as fusion-algorithm.md with appropriate substitutions)

**Variables** (in Step 3):
```
GEMINI_MODEL = "gemini-3-pro-preview"  # Test strategy = code generation, use Pro
```

### Step 5: Create Git Worktrees

```bash
# Worker A - Unit test focused (Testing Pyramid base)
git worktree add "{WORKTREE_ROOT}/impl-a" -b fusion/{SESSION_ID}/impl-a

# Worker B - Integration test focused (Testing Trophy)
git worktree add "{WORKTREE_ROOT}/impl-b" -b fusion/{SESSION_ID}/impl-b

# Worker C - E2E/Behavior test focused (Outside-in)
git worktree add "{WORKTREE_ROOT}/impl-c" -b fusion/{SESSION_ID}/impl-c
```

### Step 6: Create tasks.json

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "F-Thread (Fusion)",
  "task_type": "fusion-test",
  "target": {
    "description": "{TEST_TARGET}",
    "slug": "{TEST_SLUG}"
  },
  "base_branch": "{BASE_BRANCH}",
  "worktrees": {
    "impl-a": {
      "path": "{WORKTREE_ROOT}/impl-a",
      "branch": "fusion/{SESSION_ID}/impl-a",
      "worker": "worker-a",
      "provider": "claude-opus",
      "philosophy": "unit-focused",
      "status": "pending"
    },
    "impl-b": {
      "path": "{WORKTREE_ROOT}/impl-b",
      "branch": "fusion/{SESSION_ID}/impl-b",
      "worker": "worker-b",
      "provider": "gemini-3-pro",
      "philosophy": "integration-focused",
      "status": "pending"
    },
    "impl-c": {
      "path": "{WORKTREE_ROOT}/impl-c",
      "branch": "fusion/{SESSION_ID}/impl-c",
      "worker": "worker-c",
      "provider": "codex-gpt-5.2",
      "philosophy": "e2e-focused",
      "status": "pending"
    }
  },
  "evaluation": {
    "status": "pending",
    "criteria": ["coverage", "execution_time", "bug_detection", "maintainability", "confidence"],
    "winner": null
  }
}
```

### Step 7: Create Judge Queen Prompt

```markdown
# Judge Queen - Test Strategy Fusion Evaluator

You are the **Judge Queen** for an F-Thread testing strategy session.

## Your Mission

Three workers are creating test suites with different philosophies. Your job is to:
1. Monitor their progress
2. Evaluate the trade-offs of each approach
3. Help pick the right testing strategy

## Target to Test

**{TEST_TARGET}**

## Session Info

- **Session ID**: {SESSION_ID}
- **Session Path**: .hive/sessions/{SESSION_ID}
- **Thread Type**: F-Thread (Fusion) - Competing test strategies

## Testing Philosophies

| Worker | Philosophy | Shape |
|--------|------------|-------|
| worker-a | Unit-Focused | Testing Pyramid (many units, few E2E) |
| worker-b | Integration-Focused | Testing Trophy (heavy middle) |
| worker-c | E2E-Focused | Outside-In (user behavior first) |

```
Testing Pyramid (A)     Testing Trophy (B)     Outside-In (C)
       /\                    ____                  ████
      /E2E\                 /    \                 ████ E2E
     /────\               /      \                ████
    / Int  \             | Integ  |               ██
   /────────\            |        |               ██ Integration
  /   Unit   \            \      /                █
 /────────────\            \____/                 █ Unit
```

## Evaluation Framework

### Metrics to Collect

For each test suite:

```bash
cd {WORKTREE_PATH}

# 1. Run tests and measure time
time npm test

# 2. Get coverage report
npm run test:coverage

# 3. Count tests by type
grep -r "describe\|it\|test(" tests/ | wc -l

# 4. Measure flakiness (run 5x)
for i in {1..5}; do npm test; done
```

### Bug Detection Experiment

Introduce known bugs and see which suite catches them:

1. **Logic bug**: Change a calculation
2. **Integration bug**: Break an API contract
3. **UI bug**: Change a selector/element
4. **Race condition**: Add async timing issue
5. **Edge case**: Pass null/undefined

Record which suite catches each.

### Trade-off Matrix

| Metric | Unit (A) | Integration (B) | E2E (C) |
|--------|----------|-----------------|---------|
| Execution time | Fast | Medium | Slow |
| Setup complexity | Low | Medium | High |
| Flakiness | Low | Medium | High |
| Refactor resistance | Low | Medium | High |
| Bug localization | Precise | Good | Poor |
| User confidence | Low | Medium | High |

## Generate Comparison Report

Write to `.hive/sessions/{SESSION_ID}/evaluation.md`:

```markdown
# Test Strategy Fusion Evaluation

## Target: {TEST_TARGET}

## Test Suite Comparison

| Metric | Unit (A) | Integration (B) | E2E (C) |
|--------|----------|-----------------|---------|
| Total tests | X | X | X |
| Execution time | Xs | Xs | Xs |
| Line coverage | X% | X% | X% |
| Branch coverage | X% | X% | X% |
| Flaky tests | X | X | X |

## Bug Detection Matrix

| Bug Type | Unit (A) | Integration (B) | E2E (C) |
|----------|----------|-----------------|---------|
| Logic error | ✓/✗ | ✓/✗ | ✓/✗ |
| API contract | ✓/✗ | ✓/✗ | ✓/✗ |
| UI regression | ✓/✗ | ✓/✗ | ✓/✗ |
| Race condition | ✓/✗ | ✓/✗ | ✓/✗ |
| Edge case | ✓/✗ | ✓/✗ | ✓/✗ |

## Test Distribution

### Suite A (Unit-Focused)
- Unit tests: X (Y%)
- Integration tests: X (Y%)
- E2E tests: X (Y%)

[Key patterns and notable tests]

### Suite B (Integration-Focused)
- Unit tests: X (Y%)
- Integration tests: X (Y%)
- E2E tests: X (Y%)

[Key patterns and notable tests]

### Suite C (E2E-Focused)
- Unit tests: X (Y%)
- Integration tests: X (Y%)
- E2E tests: X (Y%)

[Key patterns and notable tests]

## Recommendation Matrix

| If Your Priority Is... | Choose |
|------------------------|--------|
| Fast CI/CD feedback | Suite A (Unit) |
| Refactor confidence | Suite B (Integration) |
| User behavior confidence | Suite C (E2E) |
| Balanced approach | Hybrid (see below) |

## Recommended Hybrid

Take the best from each:
- From A: [specific tests]
- From B: [specific tests]
- From C: [specific tests]

## Final Recommendation

**{STRATEGY}**

### Why
[Explanation based on the target's characteristics]
```
```

### Step 8: Create Worker Prompts

**Worker A** (Unit-Focused / Testing Pyramid):
```markdown
# Worker A - Unit Test Focused Strategy

## Your Mission
Create a test suite for **{TEST_TARGET}** using a unit-test-heavy approach.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-a
- **Branch**: fusion/{SESSION_ID}/impl-a

## Philosophy: Testing Pyramid

```
       /\
      /  \      Few E2E tests (smoke tests)
     /────\
    /      \    Some integration tests
   /────────\
  /          \  Many unit tests (foundation)
 /────────────\
```

**Ratio target**: 70% unit, 20% integration, 10% E2E

## Principles

- **Test in isolation**: Mock dependencies
- **Fast feedback**: Tests run in milliseconds
- **High coverage**: Test every function/method
- **Edge cases**: Test boundaries and errors
- **Pure functions**: Easiest to test, prioritize

## What to Test

### Unit Tests (Primary Focus)
- All pure functions
- Class methods in isolation
- State transformations
- Validation logic
- Error handling paths
- Edge cases and boundaries

### Integration Tests (Secondary)
- Module interfaces
- Database queries (with test DB)
- API request/response

### E2E Tests (Minimal)
- Critical happy paths only
- Smoke tests for deployment

## Deliverables

1. **Test files** in appropriate structure
2. **Coverage report** showing >80% coverage
3. **Test documentation** explaining strategy
4. **Mock/stub patterns** used

## Testing Patterns

```typescript
// Unit test example - isolated, fast
describe('calculateTotal', () => {
  it('sums items correctly', () => {
    const items = [{ price: 10 }, { price: 20 }];
    expect(calculateTotal(items)).toBe(30);
  });

  it('handles empty array', () => {
    expect(calculateTotal([])).toBe(0);
  });

  it('handles decimal precision', () => {
    const items = [{ price: 0.1 }, { price: 0.2 }];
    expect(calculateTotal(items)).toBeCloseTo(0.3);
  });
});
```

## Begin

Announce: "Worker A creating unit-focused test suite for {TEST_TARGET}"
```

**Worker B** (Integration-Focused / Testing Trophy):
```markdown
# Worker B - Integration Test Focused Strategy

## Your Mission
Create a test suite for **{TEST_TARGET}** using an integration-test-heavy approach.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-b
- **Branch**: fusion/{SESSION_ID}/impl-b

## Philosophy: Testing Trophy

```
    ____
   /    \     E2E: Few, critical paths
  /      \
 |        |   Integration: MOST tests here
 |        |   (Test real interactions)
  \      /
   \____/     Unit: Some, for complex logic
```

**Ratio target**: 20% unit, 60% integration, 20% E2E

## Principles

- **Test real interactions**: Don't mock everything
- **Confidence over coverage**: Test what matters
- **Realistic scenarios**: Test how code actually runs
- **Database included**: Use test database, not mocks
- **API contracts**: Test real HTTP calls

## What to Test

### Integration Tests (Primary Focus)
- API endpoints with real database
- Service-to-service communication
- Authentication flows
- Data pipelines
- Third-party integrations (with sandboxes)

### Unit Tests (For Complex Logic)
- Complex algorithms
- Business rule calculations
- Validation logic

### E2E Tests (Critical Paths)
- Main user journeys
- Payment flows
- Authentication

## Deliverables

1. **Integration test suite** with test database
2. **API test collection** (real HTTP)
3. **Docker compose** for test environment
4. **Seed data** for consistent testing

## Testing Patterns

```typescript
// Integration test example - real database
describe('POST /api/orders', () => {
  beforeEach(async () => {
    await db.seed(); // Real test database
  });

  it('creates order and updates inventory', async () => {
    const response = await request(app)
      .post('/api/orders')
      .send({ productId: 'abc', quantity: 2 });

    expect(response.status).toBe(201);

    // Verify real database state
    const order = await db.orders.findById(response.body.id);
    expect(order.status).toBe('pending');

    const product = await db.products.findById('abc');
    expect(product.inventory).toBe(8); // Was 10
  });
});
```

## Begin

Announce: "Worker B creating integration-focused test suite for {TEST_TARGET}"
```

**Worker C** (E2E-Focused / Outside-In):
```markdown
# Worker C - E2E/Behavior Test Focused Strategy

## Your Mission
Create a test suite for **{TEST_TARGET}** using an E2E/behavior-driven approach.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-c
- **Branch**: fusion/{SESSION_ID}/impl-c

## Philosophy: Outside-In / BDD

```
████████████  E2E: Most tests here
████████████  (User perspective)
████████████
████          Integration: Some
████          (System boundaries)
██            Unit: Few
██            (Critical algorithms)
```

**Ratio target**: 20% unit, 20% integration, 60% E2E/behavior

## Principles

- **User perspective**: Test what users experience
- **Behavior over implementation**: Test outcomes, not code
- **Real browser**: Playwright/Cypress for UI
- **Given-When-Then**: BDD style scenarios
- **Acceptance criteria**: Tests ARE the spec

## What to Test

### E2E Tests (Primary Focus)
- Complete user journeys
- Cross-browser behavior
- Mobile responsiveness
- Accessibility (a11y)
- Error states users see
- Loading/empty states

### Integration Tests (Secondary)
- API contracts
- Event flows
- Background jobs

### Unit Tests (Minimal)
- Complex business logic only

## Deliverables

1. **Playwright/Cypress test suite**
2. **User journey documentation**
3. **Visual regression tests**
4. **Accessibility audit tests**
5. **BDD feature files** (optional)

## Testing Patterns

```typescript
// E2E test example - user perspective
describe('Checkout Flow', () => {
  test('user can complete purchase', async ({ page }) => {
    // Given: User has items in cart
    await page.goto('/cart');
    await expect(page.locator('[data-testid="cart-count"]')).toHaveText('2');

    // When: User completes checkout
    await page.click('button:has-text("Checkout")');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="card"]', '4242424242424242');
    await page.click('button:has-text("Pay Now")');

    // Then: Order confirmation shown
    await expect(page).toHaveURL(/\/confirmation/);
    await expect(page.locator('h1')).toHaveText('Order Confirmed!');

    // And: Email sent (check mailbox or mock)
    // And: Inventory updated (verify via API)
  });

  test('shows error for declined card', async ({ page }) => {
    // Test error handling from user perspective
  });

  test('works on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    // Same flow works on mobile
  });
});
```

## BDD Feature Format (Optional)

```gherkin
Feature: Checkout

  Scenario: Successful purchase
    Given I have 2 items in my cart
    When I proceed to checkout
    And I enter valid payment details
    And I click "Pay Now"
    Then I should see "Order Confirmed"
    And I should receive a confirmation email
```

## Begin

Announce: "Worker C creating E2E/behavior-focused test suite for {TEST_TARGET}"
```

### Output Status

```markdown
## Fusion Test Arena Launched!

**Thread Type**: F-Thread (True Fusion)
**Session**: {SESSION_ID}
**Target**: {TEST_TARGET}

### Competing Test Philosophies

| Worker | Philosophy | Test Distribution |
|--------|------------|-------------------|
| Worker A | Unit-Focused (Pyramid) | 70% unit, 20% int, 10% E2E |
| Worker B | Integration-Focused (Trophy) | 20% unit, 60% int, 20% E2E |
| Worker C | E2E-Focused (Outside-In) | 20% unit, 20% int, 60% E2E |

### What Gets Compared

- **Execution time**: How fast does the suite run?
- **Coverage**: What percentage of code is tested?
- **Bug detection**: Which bugs does each suite catch?
- **Flakiness**: How reliable are the tests?
- **Maintenance**: How easy to update?

### The Testing Debate

This is one of the most contentious topics in software:
- Kent Beck: "Test Pyramid" (unit-heavy)
- Kent C. Dodds: "Testing Trophy" (integration-heavy)
- BDD advocates: "Outside-in" (E2E-heavy)

**All are valid. Which is right for YOUR code?**

Watch three testing philosophies compete!
```

### Step 9: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# mprocs configuration for Fusion Test session: {SESSION_ID}
# Gemini CLI: using latest installed version
procs:
  judge-queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the JUDGE QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "judge-queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      FUSION_TYPE: "test"

  worker-a-opus:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are WORKER A. Read .hive/sessions/{SESSION_ID}/worker-a-prompt.md"]
    cwd: "{WORKTREE_ROOT}/impl-a"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "a"
      FUSION_APPROACH: "unit-focused"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-b-gemini:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER B. Read .hive/sessions/{SESSION_ID}/worker-b-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-b"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "b"
      FUSION_APPROACH: "integration-focused"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-c-gpt:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER C. Read .hive/sessions/{SESSION_ID}/worker-c-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-c"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "c"
      FUSION_APPROACH: "e2e-focused"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 5 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

### Variance Workers (Optional)

**If VARIANCE >= 2, add Worker D (GLM 4.7 - Contract/Snapshot testing):**

```yaml
  worker-d-glm:
    cmd: ["powershell", "-NoProfile", "-Command", "cd '{WORKTREE_ROOT}/impl-d'; $env:OPENCODE_YOLO='true'; opencode run --format default -m opencode/glm-4.7-free 'You are WORKER D. Create a contract/snapshot testing strategy. Focus on API contracts, schema validation, snapshot tests, and golden file testing.'"]
    cwd: "{WORKTREE_ROOT}/impl-d"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "d"
      FUSION_APPROACH: "contract-snapshot"
```

Create additional worktrees for variance workers:
```bash
# If VARIANCE >= 2:
git worktree add "{WORKTREE_ROOT}/impl-d" -b fusion/{SESSION_ID}/impl-d
```
