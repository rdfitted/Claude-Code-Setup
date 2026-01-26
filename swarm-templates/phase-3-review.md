# Phase 3: Review Cycle

## Overview

After workers complete, Planners run a review cycle: Reviewer → Resolver (if needed) → Tester. This ensures domain-level quality before Queen does integration review.

---

## For Planners

### Input Files
- `tasks/planner-{X}/tasks.json` - Files that were modified
- `docs/spawn-templates.md` - Spawn commands

### Review Cycle Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Step 3a: Spawn Reviewer {X}                                 │
│          Reviews all code changes from workers              │
│          Outputs: tasks/planner-{X}/review-findings.md      │
│                                                             │
│          Wait for COMPLETED                                 │
├─────────────────────────────────────────────────────────────┤
│ Step 3b: Spawn Resolver {X} (IF issues found)               │
│          Fixes all issues from review-findings.md           │
│                                                             │
│          Wait for COMPLETED                                 │
├─────────────────────────────────────────────────────────────┤
│ Step 3c: Spawn Tester {X}                                   │
│          Runs tests for this domain                         │
│          Outputs: tasks/planner-{X}/test-results.md         │
│                                                             │
│          Wait for COMPLETED                                 │
├─────────────────────────────────────────────────────────────┤
│ Step 3d: Loop if tests fail                                 │
│          Spawn Resolver again → Re-test                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 3a: Reviewer

### Write Reviewer Task

Write to `tasks/planner-{X}/reviewer-{X}-task.md`:

```markdown
# Reviewer {X}

## Session
- **ID**: {SESSION_ID}
- **Log**: logs/reviewer-{X}.log

## Your Job
Review all code changes from Planner {X}'s workers.

## Files to Review
{LIST_FILES_FROM_TASKS_JSON}

## Review Focus
- **Security**: No vulnerabilities, proper validation
- **Quality**: Clean code, good patterns
- **Performance**: No obvious bottlenecks
- **Style**: Consistent with codebase

## Guidelines
Read `state/session-guidelines.md` for project standards.

## Output
Write to `tasks/planner-{X}/review-findings.md`:

```markdown
# Review Findings - Planner {X}

## Summary
- **Status**: PASS | ISSUES_FOUND
- **Critical**: {count}
- **Major**: {count}
- **Minor**: {count}

## Issues

### Critical
{list or "None"}

### Major
{list or "None"}

### Minor
{list or "None"}
```

Log COMPLETED when done.
```

### Spawn Reviewer

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read .swarm/sessions/{SESSION_ID}/tasks/planner-{X}/reviewer-{X}-task.md and execute.\"", "name": "reviewer-{X}", "env": {"OPENCODE_YOLO": "true"}}'
```

### Check Completion

```powershell
Select-String -Path '.swarm/sessions/{SESSION_ID}/logs/reviewer-{X}.log' -Pattern 'COMPLETED'
```

---

## Step 3b: Resolver (If Issues Found)

**Only spawn if review-findings.md shows Critical or Major issues.**

### Write Resolver Task

Write to `tasks/planner-{X}/resolver-{X}-task.md`:

```markdown
# Resolver {X}

## Session
- **ID**: {SESSION_ID}
- **Log**: logs/resolver-{X}.log

## Your Job
Fix ALL issues from review findings.

## Read First
- `tasks/planner-{X}/review-findings.md`

## Rules
- Fix every Critical and Major issue
- Fix Minor issues if straightforward
- Document each fix in your log

## Output
Update the code files directly. Log each fix:
```
FIXED: [file.ts] Issue description - how fixed
```

Log COMPLETED when all issues resolved.
```

### Spawn Resolver (Cursor CLI - Opus 4.5)

Write spawn .bat file:
```powershell
Set-Content -Path ".swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-resolver-{X}.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/resolver-{X}-task.md and execute.\\\"\", \"name\": \"resolver-{X}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

Execute:
```bash
.swarm/sessions/{SESSION_ID}/tasks/planner-{X}/spawn-resolver-{X}.bat
```

---

## Step 3c: Tester

### Write Tester Task

Write to `tasks/planner-{X}/tester-{X}-task.md`:

```markdown
# Tester {X}

## Session
- **ID**: {SESSION_ID}
- **Log**: logs/tester-{X}.log

## Your Job
Run tests for Planner {X}'s domain.

## Test Commands
{APPROPRIATE_TEST_COMMAND_FOR_PROJECT}
- npm test
- pytest
- go test ./...
- etc.

## Focus Areas
{LIST_FILES_FROM_TASKS_JSON}

## Output
Write to `tasks/planner-{X}/test-results.md`:

```markdown
# Test Results - Planner {X}

## Summary
- **Status**: PASS | FAIL
- **Tests Run**: {count}
- **Passed**: {count}
- **Failed**: {count}

## Failures
{list failures with file and description, or "None"}
```

Log COMPLETED when done.
```

### Spawn Tester

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .swarm/sessions/{SESSION_ID}/tasks/planner-{X}/tester-{X}-task.md and execute.\"", "name": "tester-{X}"}'
```

---

## Step 3d: Loop If Tests Fail

If test-results.md shows failures:

1. Write new resolver task targeting specific failures
2. Spawn resolver
3. Wait for completion
4. Re-run tester
5. Repeat until PASS

---

## Signal Planner Completion

After all steps pass:

```powershell
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/planner-{X}.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] PLANNER-{X}: PLANNER_COMPLETE - Domain: {DOMAIN}\""
```

### Write Summary

Write to `tasks/planner-{X}/summary.md`:

```markdown
# Planner {X} Summary

## Domain
{DOMAIN_NAME}

## Work Completed
- Worker 1{X}: {description}
- Worker 2{X}: {description}
- Worker 3{X}: {description}
- Worker 4{X}: {description}

## Files Modified
{list}

## Review Findings
- Critical resolved: {count}
- Major resolved: {count}

## Test Results
PASS - all tests passing

## Notes
{any important observations for integration}
```

### Phase 3 Complete (Planner)
- Review complete, issues resolved
- All tests passing
- PLANNER_COMPLETE logged
- Summary written
- **Your job is done** - Queen handles integration
