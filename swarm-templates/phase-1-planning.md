# Phase 1: Task Generation

## Overview

Phase 1 is where domains are broken into concrete tasks. Queen writes Planner prompts, Planners write worker tasks.

---

## For Queen

### Input Files
- `docs/context.md` - Task/issue details
- `state/responsibility-matrix.md` - Domain assignments
- `state/file-ownership.md` - File boundaries
- `state/session-guidelines.md` - Learnings

### Your Job

1. **Read** responsibility-matrix.md to understand domain assignments
2. **Write** thin Planner prompts (one per Planner)
3. **Spawn** Planners via mprocs using `docs/spawn-templates.md`

### Writing Planner Prompts

Write to `.swarm/sessions/{SESSION_ID}/planner-{X}-prompt.md`:

```markdown
# Planner {X} - {DOMAIN}

**Role**: Mini-queen for {DOMAIN} domain.

## Session
- **ID**: {SESSION_ID}
- **Path**: .swarm/sessions/{SESSION_ID}/
- **Your Log**: logs/planner-{X}.log
- **Your Tasks**: tasks/planner-{X}/
- **mprocs Server**: 127.0.0.1:{MPROCS_PORT}

## Read First (in order)
1. `docs/context.md`
2. `docs/model-selection.md`
3. `docs/spawn-templates.md`
4. `docs/log-protocol.md`
5. `state/responsibility-matrix.md` - Find your domain
6. `state/file-ownership.md` - Find your files

## Your Phases
Execute in order:
1. `phases/phase-1-planning.md` (For Planners section)
2. `phases/phase-2-execution.md`
3. `phases/phase-3-review.md`

## Begin
Log STARTED to logs/planner-{X}.log, then execute Phase 1.
```

### Spawning Planners

After writing all Planner prompts, spawn them:

```bash
# From docs/spawn-templates.md
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "claude --model opus --dangerously-skip-permissions \"Read .swarm/sessions/{SESSION_ID}/planner-a-prompt.md and execute.\"", "name": "planner-a"}'
```

### Phase 1 Complete (Queen)
- All Planner prompts written
- All Planners spawned
- Proceed to monitoring (wait for PLANNER_COMPLETE from all)

---

## For Planners

### Input Files
- `docs/context.md` - What we're building
- `state/responsibility-matrix.md` - Your domain assignment
- `state/file-ownership.md` - Your file boundaries

### Your Job

1. **Read** your domain from responsibility-matrix.md
2. **Read** your files from file-ownership.md
3. **Break down** your domain into 2-4 worker tasks
4. **Write** tasks.json to `tasks/planner-{X}/`
5. **Write** worker task files

### tasks.json Format

Write to `tasks/planner-{X}/tasks.json`:

```json
{
  "planner": "{X}",
  "domain": "{DOMAIN_NAME}",
  "tasks": [
    {
      "worker": "1{X}",
      "model": "opus",
      "type": "backend",
      "description": "Implement X functionality",
      "files": ["src/path/to/file.ts"],
      "depends_on": []
    },
    {
      "worker": "2{X}",
      "model": "gemini",
      "type": "frontend",
      "description": "Build Y component",
      "files": ["src/components/Y.tsx"],
      "depends_on": []
    },
    {
      "worker": "3{X}",
      "model": "grok",
      "type": "coherence",
      "description": "Verify consistency between X and Y",
      "files": ["src/path/to/file.ts", "src/components/Y.tsx"],
      "depends_on": ["1{X}", "2{X}"]
    },
    {
      "worker": "4{X}",
      "model": "codex",
      "type": "simplify",
      "description": "Simplify and clean up code",
      "files": ["src/path/to/file.ts"],
      "depends_on": ["3{X}"]
    }
  ]
}
```

### Worker Task Template

Write to `tasks/planner-{X}/worker-{N}{X}-task.md`:

```markdown
# Worker {N}{X} - {TYPE}

## Session
- **ID**: {SESSION_ID}
- **Log**: logs/worker-{N}{X}.log

## Read First
- `state/session-guidelines.md`

## Your Task
{SPECIFIC_TASK_DESCRIPTION}

## Files to Modify
{LIST_OF_FILES_FROM_TASKS_JSON}

## Context
{ANY_RELEVANT_CONTEXT_FROM_DOCS_CONTEXT_MD}

## Log Protocol
See `docs/log-protocol.md`. Log STARTED, PROGRESS, COMPLETED.

## Rules
- DO NOT commit or push
- Stay within your assigned files
- Log progress regularly

## Begin
Log STARTED, execute task, log COMPLETED.
```

### Task Assignment Guidelines

| Worker | Model | Assign Tasks Like |
|--------|-------|-------------------|
| 1{X} | Opus | Backend, APIs, business logic, architecture |
| 2{X} | Gemini | Frontend, UI, components, styling |
| 3{X} | Grok | Coherence checks, cross-file consistency |
| 4{X} | Codex | Simplification, cleanup, straightforward fixes |

### Phase 1 Complete (Planner)
- `tasks/planner-{X}/tasks.json` created
- All worker task files written
- Log: "Phase 1 complete. Ready for Phase 2."
- Proceed to Phase 2
