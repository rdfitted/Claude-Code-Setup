# Planner Cross-Reference Protocol

**PURPOSE**: Later Planners inherit context from completed Planners to save tokens and avoid redundant exploration.

---

## How It Works

1. **Queen tracks Planner status** in `state/planner-status.md`
2. **Completed Planners write summaries** to `tasks/planner-{X}/summary.md`
3. **New Planners read completed summaries** before starting work

---

## For Queen: Track Planner Status

Maintain `state/planner-status.md`:

```markdown
# Planner Status

| Planner | Status | Summary Available | Key Discoveries |
|---------|--------|-------------------|-----------------|
| A | COMPLETED | tasks/planner-a/summary.md | Backend patterns, DB schema |
| B | COMPLETED | tasks/planner-b/summary.md | Frontend state management |
| C | IN_PROGRESS | (pending) | - |
| D | NOT_STARTED | - | - |
```

Update this file whenever a Planner signals PLANNER_COMPLETE.

---

## For Planners: Write Summary on Completion

Before signaling PLANNER_COMPLETE, write `tasks/planner-{X}/summary.md`:

```markdown
# Planner {X} Summary

## Completed
- [x] Task 1 description
- [x] Task 2 description

## Files Created/Modified
- `path/to/file1.ts` - What it does
- `path/to/file2.py` - What it does

## Key Patterns Established
- Pattern 1: How we handle X
- Pattern 2: How we structure Y

## Discoveries for Future Planners
- Finding 1: Important context for later work
- Finding 2: Gotcha to watch out for

## API/Interface Contracts
- Endpoint: `POST /api/resource` - Request/response shape
- Type: `InterfaceName` - Key fields

## Dependencies Introduced
- Package X version Y - Why needed
```

---

## For New Planners: Read Completed Summaries

**BEFORE starting your work**, read all completed Planner summaries:

```markdown
## Context from Previous Planners

**READ THESE FIRST - they contain patterns and discoveries you need:**

| Planner | Status | Summary |
|---------|--------|---------|
| A | COMPLETED | `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-a/summary.md` |
| B | COMPLETED | `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-b/summary.md` |

**What to look for:**
1. Patterns established (follow them, don't reinvent)
2. API contracts (your frontend must match their backend shapes)
3. Discoveries (avoid their gotchas)
4. File structure (stay consistent)
```

---

## Queen Prompt Addition

Add to Queen prompt:

```markdown
## Planner Cross-Reference

When writing Planner prompts:

1. **Check** which Planners are COMPLETED
2. **Include** completed summaries in new Planner's "Read First" section
3. **Update** `state/planner-status.md` after each PLANNER_COMPLETE

Example for Planner C (when A and B are done):

## Context from Previous Planners (READ FIRST)

Planners A and B have completed their work. Read their summaries to:
- Follow established patterns
- Match API contracts
- Avoid discovered gotchas

1. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-a/summary.md`
2. `{PROJECT_ROOT}/.swarm/sessions/{SESSION_ID}/tasks/planner-b/summary.md`
```

---

## Token Savings

| Without Cross-Reference | With Cross-Reference |
|------------------------|---------------------|
| Planner C scans entire codebase | Planner C reads 2 summaries |
| Planner C rediscovers patterns | Planner C inherits patterns |
| Planner C might conflict with A/B | Planner C knows A/B's contracts |
| ~2000 tokens exploring | ~200 tokens reading summaries |

**Estimated savings**: 80-90% reduction in exploration tokens for later Planners.

---

## Long-Horizon Specific

For `/resolve-swarm-issue-long` with sequential waves:

- Wave 1 Planners: No prior context (they establish patterns)
- Wave 2 Planners: Read Wave 1 summaries
- Wave 3 Planners: Read Wave 1 + Wave 2 summaries
- etc.

Queen updates `state/planner-status.md` between waves.
