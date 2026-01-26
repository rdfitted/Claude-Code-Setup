# Phase 6: Code Quality Loop (Queen Only)

## Overview

After PR is created, Queen monitors for external reviewer comments and spawns code-quality agents to address them.

**Loop Parameters:**
- **Wait time per cycle**: 10 minutes
- **Maximum cycles**: 3
- **Total max wait**: 30 minutes
- **Code Quality Agent**: Cursor CLI (Opus 4.5)

---

## Prerequisites

- Phase 5 complete
- PR created and pushed
- PR URL available

---

## Code Quality Loop Flow

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 6: Code Quality Loop (Up to 3 Cycles)                 │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Cycle N (N = 1, 2, 3):                                  │ │
│ │                                                         │ │
│ │ 1. Wait 10 minutes for external reviewers               │ │
│ │ 2. Check for new comments                               │ │
│ │    - If no comments → END (success)                     │ │
│ │    - If comments → continue                             │ │
│ │ 3. Write code-quality-{N} task file                     │ │
│ │ 4. Spawn code-quality-{N} agent (Cursor CLI + Opus 4.5) │ │
│ │ 5. Wait for COMPLETED in code-quality-{N}.log           │ │
│ │ 6. Agent commits and pushes fixes                       │ │
│ │ 7. If N < 3 → Cycle N+1                                 │ │
│ │    If N = 3 → END (max cycles reached)                  │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 6.1: Wait for External Reviews (10 minutes)

**⚠️ YOU MUST ACTUALLY WAIT - DO NOT SKIP ⚠️**

External reviewers (Gemini, Codex, Code Rabbit) need time to analyze the PR.

```powershell
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Code Quality Loop - Cycle {N}. Waiting 10 minutes for external reviewers...\"; Start-Sleep -Seconds 600; Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Wait complete. Checking for comments...\""
```

**DO NOT proceed until this command completes (10 minutes).**

---

## Step 6.2: Check for New Comments

```bash
# Get comment count
NEW_COMMENTS=$(gh api repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/comments --jq 'length')
```

Or:
```bash
gh pr view {PR_NUMBER} --json comments,reviews --jq '.comments | length'
```

**If NEW_COMMENTS = 0**:
```powershell
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: No new comments. PR is ready for review.\""
```
→ **END loop**

---

## Step 6.3: Write Code Quality Task Template

Write to `tasks/code-quality-task-template.md`:

```markdown
# Code Quality Task - Iteration {N}

## PR
Resolving PR #{PR_NUMBER} comments (Iteration {N})

## Session
- **Session ID**: {SESSION_ID}
- **Your Log**: logs/code-quality-{N}.log
- **PR Branch**: {BRANCH_NAME}

## Session Guidelines (MUST FOLLOW!)

**READ THIS FIRST**: `state/session-guidelines.md`

## Your Task

Resolve ALL new comments on PR #{PR_NUMBER}.

### Step 1: Fetch PR Comments

```bash
gh api repos/{OWNER}/{REPO}/pulls/{PR_NUMBER}/comments
```

### Step 2: Understand Each Comment

For each comment:
1. Read the file and line being commented on
2. Understand what the reviewer is asking for
3. Implement the requested change

### Step 3: Resolve Comments

For each unresolved comment:
1. Make the requested change
2. Log what you changed

### Step 4: Commit and Push (IMPORTANT!)

**You MUST commit and push your changes** so external reviewers can see them:

```bash
git add .
git commit -m "fix: address PR review comments (iteration {N})

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
git push origin {BRANCH_NAME}
```

## Log Protocol

```powershell
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/code-quality-{N}.log' -Value '[$(Get-Date -Format \"HH:mm:ss\")] CODE-QUALITY-{N}: message'"
```

**Required log entries:**
- `STARTED`
- `COMMENT: {summary}` - Each comment you're addressing
- `FIXED: {description}` - What you changed
- `COMMITTED: {commit_hash}` - After you commit
- `PUSHED` - After you push
- `COMPLETED`

## Instructions

1. Log STARTED
2. Fetch all PR comments
3. For each unresolved comment:
   - Read the relevant file
   - Make the requested change
   - Log FIXED
4. Commit and push your changes
5. Log COMMITTED and PUSHED
6. Log COMPLETED

## Begin
Resolve the PR comments now.
```

---

## Step 6.4: Write and Spawn Code Quality Agent (Cursor CLI - Opus 4.5)

### Step 6.4a: Write iteration-specific task file

```powershell
$template = Get-Content ".swarm/sessions/{SESSION_ID}/tasks/code-quality-task-template.md" -Raw
$taskContent = $template -replace '\{N\}', '{N}' -replace '\{PR_NUMBER\}', '{PR_NUMBER}'
Set-Content -Path ".swarm/sessions/{SESSION_ID}/tasks/code-quality-{N}-task.md" -Value $taskContent
```

### Step 6.4b: Create empty log file

```powershell
New-Item -Path ".swarm/sessions/{SESSION_ID}/logs/code-quality-{N}.log" -ItemType File -Force
```

### Step 6.4c: Spawn code-quality-{N} agent via MPROCS (Cursor CLI)

**⚠️ YOU MUST USE MPROCS - NOT TASK TOOL ⚠️**

Do NOT use the Task tool. You MUST spawn a visible mprocs agent.

**Step 1: Write spawn .bat file**

```powershell
Set-Content -Path ".swarm/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat" -Value '@echo off
mprocs --server 127.0.0.1:{MPROCS_PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"Read {PROJECT_ROOT_FORWARD_SLASH}/.swarm/sessions/{SESSION_ID}/tasks/code-quality-{N}-task.md and execute.\\\"\", \"name\": \"code-quality-{N}\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"'
```

**Step 2: Execute**

```bash
.swarm/sessions/{SESSION_ID}/spawn-code-quality-{N}.bat
```

The code-quality agent will handle the PR comments. Your job is to SPAWN and MONITOR, not to do the work yourself.

---

## Step 6.5: Monitor and Loop (Up to 3 Cycles)

1. Wait for `COMPLETED` in code-quality-{N}.log
2. Agent already committed and pushed (see task instructions)
3. Wait another 10 minutes for new reviews (Step 6.1)
4. Check for new comments (Step 6.2)
5. If new comments exist AND N < 3, spawn code-quality-{N+1} (Step 6.4)
6. Repeat until no new comments OR max 3 cycles

**Loop termination conditions:**
- No new comments after 10-minute wait → SUCCESS
- Maximum 3 iterations reached → END (alert user if still comments)

---

## Step 6.6: Log Completion

```powershell
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Code Quality Loop complete. {N} iterations. PR is ready for human review.\""
```

If max cycles reached with remaining comments:

```powershell
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: ⚠️ Max cycles (3) reached. Some PR comments may still need attention.\""
```

---

## Agent Models by Comment Type

While the primary code-quality agent is Cursor CLI (Opus 4.5), you MAY use specialized agents for specific comment types:

| Comment Type | Agent | Model | When to Use |
|--------------|-------|-------|-------------|
| Logic/bugs/complex | **Cursor CLI** | Opus 4.5 | Default - handles most comments |
| Style/formatting | Codex | GPT-5.2 | Simple style fixes |
| Security concerns | BigPickle | OpenCode | Security-focused reviews |
| Performance | Cursor CLI | Opus 4.5 | Perf optimizations |

**Default to Cursor CLI (Opus 4.5)** for the code-quality loop.

---

## Phase 6 Complete

When loop terminates:

```powershell
powershell -NoProfile -Command "Add-Content -Path '.swarm/sessions/{SESSION_ID}/logs/queen.log' -Value \"[$(Get-Date -Format 'HH:mm:ss')] QUEEN: PHASE 6 COMPLETE - Code quality loop finished.\""
```

**Session is now fully complete.**

---

## Summary

| Parameter | Value |
|-----------|-------|
| Wait per cycle | 10 minutes |
| Max cycles | 3 |
| Total max wait | 30 minutes |
| Primary agent | Cursor CLI (Opus 4.5) |
| Agent spawns via | mprocs + .bat file |
| Each agent commits | Yes (agent pushes own fixes) |
