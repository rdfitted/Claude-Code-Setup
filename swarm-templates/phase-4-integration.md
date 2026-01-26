# Phase 4: Integration (Queen Only)

## Overview

After ALL Planners show PLANNER_COMPLETE, Queen runs the integration cycle. This catches cross-domain issues that individual Planners couldn't see.

---

## Prerequisites

**DO NOT start Phase 4 until:**

```powershell
# Check ALL Planners completed
Select-String -Path '.swarm/sessions/{SESSION_ID}/logs/planner-a.log' -Pattern 'PLANNER_COMPLETE'
Select-String -Path '.swarm/sessions/{SESSION_ID}/logs/planner-b.log' -Pattern 'PLANNER_COMPLETE'
# ... repeat for all Planners
```

---

## Integration Cycle Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Step 4a: Integration Reviewer (BigPickle)                   │
│          Reviews cross-domain interactions                  │
│          Outputs: state/integration-review.md               │
│                                                             │
│          Wait for COMPLETED                                 │
├─────────────────────────────────────────────────────────────┤
│ Step 4b: Integration Tester (Codex)                         │
│          Runs FULL test suite                               │
│          Outputs: state/integration-test-results.md         │
│                                                             │
│          Wait for COMPLETED                                 │
├─────────────────────────────────────────────────────────────┤
│ Step 4c: Integration Resolver (IF issues found)             │
│          Fixes cross-domain problems                        │
│          Outputs: state/integration-resolution.md           │
│                                                             │
│          Wait for COMPLETED                                 │
├─────────────────────────────────────────────────────────────┤
│ Step 4d: Loop if needed                                     │
│          Re-test after fixes                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 4a: Integration Reviewer

### Write Task File

Write to `tasks/integration-reviewer-task.md`:

```markdown
# Integration Reviewer

## Session
- **ID**: {SESSION_ID}
- **Log**: logs/integration-reviewer.log

## Your Job
Review INTEGRATION between all Planner domains. Each Planner already reviewed their own domain - you review how they work TOGETHER.

## Read First
- `state/file-ownership.md` - Domain boundaries
- `state/responsibility-matrix.md` - What each domain owns
- `tasks/planner-a/summary.md` - What Planner A did
- `tasks/planner-b/summary.md` - What Planner B did
{... additional Planners ...}

## Focus Areas
1. **API Contracts**: Do Planner A's APIs match what Planner B expects?
2. **Shared Types**: Were shared files modified consistently?
3. **Import/Export**: Do cross-domain imports resolve?
4. **Data Flow**: Does data flow correctly between domains?
5. **Error Handling**: Are errors propagated correctly across boundaries?

## Output
Write to `state/integration-review.md`:

```markdown
# Integration Review

## Summary
- **Status**: PASS | ISSUES_FOUND
- **Cross-Domain Issues**: {count}

## Domain Interactions Reviewed
| From | To | Status |
|------|-----|--------|
| Planner A | Planner B | OK / Issue |

## Issues Found
{list or "None"}

## Recommendations
{any suggestions for integration fixes}
```

Log COMPLETED when done.
```

### Spawn

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read .swarm/sessions/{SESSION_ID}/tasks/integration-reviewer-task.md and execute.\"", "name": "integration-reviewer", "env": {"OPENCODE_YOLO": "true"}}'
```

---

## Step 4b: Integration Tester

### Write Task File

Write to `tasks/integration-tester-task.md`:

```markdown
# Integration Tester

## Session
- **ID**: {SESSION_ID}
- **Log**: logs/integration-tester.log

## Your Job
Run the FULL test suite. Each Planner tested their domain - you test EVERYTHING together.

## Read First
- `state/integration-review.md` - Known issues to watch for

## Test Commands
Run full suite:
- `npm test` or `npm run test:all`
- `pytest` or `pytest --all`
- Appropriate command for this project

Focus on:
- Integration tests
- E2E tests
- Cross-module tests

## Output
Write to `state/integration-test-results.md`:

```markdown
# Integration Test Results

## Summary
- **Status**: PASS | FAIL
- **Total Tests**: {count}
- **Passed**: {count}
- **Failed**: {count}

## Failures
| Test | Domains Involved | Error |
|------|------------------|-------|
{list or "None"}

## Notes
{any observations about test coverage}
```

Log COMPLETED when done.
```

### Spawn

```bash
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read .swarm/sessions/{SESSION_ID}/tasks/integration-tester-task.md and execute.\"", "name": "integration-tester"}'
```

---

## Step 4c: Integration Resolver (If Needed)

**Only spawn if integration-review.md or integration-test-results.md show issues.**

### Write Task File

Write to `tasks/integration-resolver-task.md`:

```markdown
# Integration Resolver

## Session
- **ID**: {SESSION_ID}
- **Log**: logs/integration-resolver.log

## Your Job
Fix cross-domain integration issues.

## Read First
- `state/integration-review.md` - Review findings
- `state/integration-test-results.md` - Test failures
- `state/file-ownership.md` - Know domain boundaries

## Guidelines
1. Fix the cross-domain issues
2. Be careful modifying files owned by different Planners
3. Re-run affected tests to verify
4. Document what you fixed

## Output
Write to `state/integration-resolution.md`:

```markdown
# Integration Resolution

## Issues Fixed
| Issue | Files Modified | Fix Description |
|-------|----------------|-----------------|
{list}

## Verification
- Tests re-run: {which}
- Result: PASS / needs more work
```

Log COMPLETED when done.
```

### Spawn Integration Resolver (Cursor CLI - Opus 4.5)

Write spawn .bat file:
```powershell
Set-Content -Path ".swarm/sessions/{SESSION_ID}/spawn-integration-resolver.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/integration-resolver-task.md and execute.\\\"\", \"name\": \"integration-resolver\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

Execute:
```bash
.swarm/sessions/{SESSION_ID}/spawn-integration-resolver.bat
```

---

## Step 4d: Loop If Needed

If resolver's fixes cause new issues:
1. Re-run integration-tester
2. Check results
3. Spawn resolver again if needed
4. Repeat until PASS

---

## Phase 4 Complete

When integration-test-results.md shows PASS:

1. Log completion
2. Proceed to Phase 5 (Commit/PR)

```powershell
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Phase 4 complete. Integration verified.\""
```
