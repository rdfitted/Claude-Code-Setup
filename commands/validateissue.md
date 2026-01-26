---
description: Validate a GitHub issue using Task agents with external CLI tools
argument-hint: <issue-number> [--scale=N]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Write, Edit, Glob, Grep]
---

# Purpose

Validate a GitHub issue by spawning multiple investigation agents to verify that the issue is well-formed, technically accurate, and actionable. This command does NOT use the Hive structure - it uses Task agents directly with external CLI tools (Gemini, Codex).

## When to Use

Use this command when you want a quick validation without the overhead of setting up a full Hive session. The validation runs within the current Claude session using Task agents.

For full Hive-based validation with visible multi-agent coordination, use `/validate-hive-issue` instead.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (`gemini`, `codex`) via Bash for multi-model diversity.

## Variables

- `{ISSUE_NUMBER}`: GitHub issue number to validate
- `{SCALE}`: Investigation depth (1-4, default: 3) - number of parallel agents
- `{ISSUE_TITLE}`: Title of the GitHub issue
- `{ISSUE_BODY}`: Body/description of the GitHub issue
- `{ISSUE_LABELS}`: Labels attached to the issue
- `{VALIDATION_RESULTS}`: Combined results from validation agents

## Anti-Bypass Notice

This workflow REQUIRES spawning subagents that call EXTERNAL agentic tools (Gemini CLI, Codex CLI) via Bash. You are NOT permitted to:
- Use Grep/Glob/Read to validate the issue yourself during Step 2
- Use native Claude subagent types ("Explore", "codebase-researcher") for validation
- Skip the multi-agent validation step for "efficiency"

**CORRECT**: `Task(subagent_type="general-purpose", prompt="...IMMEDIATELY use Bash tool to run: gemini -m model -o text 'prompt'...")`
**WRONG**: `Task(subagent_type="Explore", prompt="...find files...")`

## Workflow

**CRITICAL WORKFLOW REQUIREMENTS**:
1. Run the workflow in order, top to bottom
2. Do not stop in between steps
3. Complete every step before stopping
4. Multi-agent validation is MANDATORY

---

### Step 1: Fetch GitHub Issue Details

```bash
# Get comprehensive issue information
gh issue view {ISSUE_NUMBER} --json number,title,body,labels,state,author,createdAt,comments,url
```

**Parse the issue to understand:**
- What claims does the issue make?
- What files/paths are referenced?
- What behavior is described?
- What are the acceptance criteria?

Extract:
- `ISSUE_NUMBER`
- `ISSUE_TITLE`
- `ISSUE_BODY`
- `ISSUE_LABELS`
- `ISSUE_URL`

---

### Step 2: Multi-Agent Validation (MANDATORY - EXTERNAL AGENTS)

**Scale Levels:**
```
Scale 1: 1 agent  (Gemini Flash - technical validation)
Scale 2: 2 agents (Gemini Flash, Codex - technical + problem validation)
Scale 3: 3 agents (Gemini Flash, Codex, Gemini Lite - comprehensive)
Scale 4: 4 agents (Above + Claude Haiku for additional coverage)
```

**CRITICAL**: Launch ALL agents in PARALLEL using a SINGLE message with multiple Task tool calls.

**Agent 1 - Gemini Flash Technical Validation (REQUIRED for all scales):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a technical validation agent using Gemini Flash.

CONTEXT - GitHub Issue #{ISSUE_NUMBER} to validate:
Title: {ISSUE_TITLE}
Body: {ISSUE_BODY}
Labels: {ISSUE_LABELS}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-flash-preview -o text \"Validate this GitHub issue against the codebase:

Issue: {ISSUE_TITLE}
Description: {ISSUE_BODY}

VALIDATION CHECKLIST:
1. TECHNICAL ACCURACY:
   - Do the file paths mentioned exist?
   - Are line numbers accurate?
   - Are function/class/API names correct?
   - Do code snippets match actual code?

2. ISSUE CLARITY:
   - Is the title clear and descriptive?
   - Is the description detailed enough?
   - Are reproduction steps provided (if bug)?
   - Are acceptance criteria defined?

3. ACTIONABILITY:
   - Is the scope reasonable?
   - Is implementation feasible?
   - Are there blocking dependencies?

For each claim in the issue, verify against the codebase and report:
- VERIFIED: claim is accurate
- INCORRECT: claim is wrong (explain why)
- UNVERIFIABLE: cannot determine (explain why)

Return a structured validation report.\"

After the command completes, format the results as:
## Technical Accuracy
| Claim | Status | Notes |
|-------|--------|-------|
| [claim] | VERIFIED/INCORRECT/UNVERIFIABLE | [details] |

## Issue Clarity Score
- Title: PASS/FAIL
- Description: PASS/FAIL
- Reproduction: PASS/FAIL/NA
- Acceptance Criteria: PASS/FAIL/NA

## Actionability
- Scope: REASONABLE/TOO_BROAD/TOO_VAGUE
- Feasibility: FEASIBLE/BLOCKED/UNCLEAR

## Verdict
VALID / NEEDS_REFINEMENT / INVALID"
)
```

**Agent 2 - Codex Problem Verification (scale >= 2):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a problem verification agent using OpenAI Codex.

CONTEXT - GitHub Issue #{ISSUE_NUMBER} to validate:
Title: {ISSUE_TITLE}
Body: {ISSUE_BODY}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

codex exec -m gpt-5.2 -s read-only -c model_reasoning_effort=\"high\" --skip-git-repo-check \"Verify this GitHub issue by checking if the described problem/feature actually exists:

Issue: {ISSUE_TITLE}
Description: {ISSUE_BODY}

VERIFICATION TASKS:
1. PROBLEM/FEATURE VERIFICATION:
   - Does the bug actually exist? Can it be reproduced?
   - Is the feature actually missing?
   - Has this already been fixed in recent commits?
   - Is this a duplicate of another issue?

2. CODE ANALYSIS:
   - Find the actual code related to this issue
   - Verify the behavior described matches actual behavior
   - Check if the proposed solution is valid

3. CONTEXT CHECK:
   - Any related PRs or commits?
   - Any configuration that affects this?
   - Any dependencies that matter?

Return findings with evidence from the codebase.\"

After the command completes, format the results as:
## Problem Verification
- **Problem Exists**: YES/NO/PARTIALLY
- **Evidence**: [specific code/behavior found]
- **Already Fixed**: YES/NO (PR/commit if yes)
- **Duplicate**: YES/NO (issue # if yes)

## Code Analysis
- **Related Files**: [list with paths]
- **Actual Behavior**: [what code actually does]
- **Proposed Solution Valid**: YES/NO/NEEDS_MODIFICATION

## Verdict
VALID / NEEDS_REFINEMENT / INVALID"
)
```

**Agent 3 - Gemini Lite File Verification (scale >= 3):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a file verification agent using Gemini Lite.

CONTEXT - GitHub Issue #{ISSUE_NUMBER} to validate:
Title: {ISSUE_TITLE}
Body: {ISSUE_BODY}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-2.5-flash-lite -o text \"Quick file and path verification for issue: {ISSUE_TITLE}

Description: {ISSUE_BODY}

VERIFY:
1. All file paths mentioned - do they exist?
2. All line numbers mentioned - are they accurate?
3. All function/class names - do they exist?
4. All imports/dependencies mentioned - are they correct?
5. Any screenshots/links - are they accessible?

Return a checklist of all verifications.\"

After the command completes, format the results as:
## File Path Verification
| Path | Exists | Notes |
|------|--------|-------|
| path/to/file.ts | YES/NO | [details] |

## Line Number Verification
| File | Line | Accurate | Notes |
|------|------|----------|-------|
| file.ts | 42 | YES/NO | [details] |

## Name Verification
| Name | Type | Exists | Notes |
|------|------|--------|-------|
| handleLogin | function | YES/NO | [details] |

## Verdict
VALID / NEEDS_REFINEMENT / INVALID"
)
```

**Agent 4 - Claude Haiku Comprehensive Check (scale >= 4):**
```
Task(
  subagent_type="Explore",
  model="haiku",
  prompt="Validate this GitHub issue by exploring the codebase:

Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}
{ISSUE_BODY}

Find and verify:
1. All files mentioned in the issue
2. Whether the described problem/feature exists
3. Similar patterns in the codebase
4. Any related issues or documentation
5. Test coverage for the affected area

Return detailed findings with file paths and evidence."
)
```

---

### Step 3: Synthesize Validation Results

After all agents return, synthesize findings:

1. **Aggregate verdicts** - What did each agent conclude?
2. **Identify consensus** - Where do agents agree/disagree?
3. **List verified claims** - What was confirmed accurate?
4. **List invalid claims** - What was found incorrect?
5. **Determine overall verdict**:
   - **VALID**: Majority of claims verified, issue is actionable
   - **NEEDS_REFINEMENT**: Some issues but fixable
   - **INVALID**: Major problems, should be closed or rejected

---

### Step 4: Generate Validation Report

```markdown
# Issue Validation Report: #{ISSUE_NUMBER}

## Summary

**Issue**: [{ISSUE_TITLE}]({ISSUE_URL})
**Verdict**: VALID | NEEDS_REFINEMENT | INVALID
**Confidence**: HIGH | MEDIUM | LOW
**Agents Used**: {count}

## Quick Assessment

| Category | Status | Details |
|----------|--------|---------|
| Technical Accuracy | PASS/FAIL | {summary} |
| Issue Clarity | PASS/FAIL | {summary} |
| Problem Exists | YES/NO/PARTIAL | {summary} |
| Actionable | YES/NO | {summary} |

## Detailed Findings

### Technical Accuracy Verification

| Claim | Agent | Status | Evidence |
|-------|-------|--------|----------|
| {claim} | {agent} | VERIFIED/INCORRECT | {evidence} |

### File & Path Verification

| Path | Exists | Line Numbers | Notes |
|------|--------|--------------|-------|
| {path} | YES/NO | ACCURATE/INACCURATE | {notes} |

### Problem/Feature Verification

- **Problem/Feature Exists**: YES/NO/PARTIALLY
- **Already Fixed**: YES/NO
- **Duplicate of**: #{number} or N/A
- **Evidence**: {specific findings}

### Agent Consensus

| Agent | Verdict | Confidence | Key Finding |
|-------|---------|------------|-------------|
| Gemini Flash | {verdict} | {conf} | {finding} |
| Codex | {verdict} | {conf} | {finding} |
| Gemini Lite | {verdict} | {conf} | {finding} |
| Claude Haiku | {verdict} | {conf} | {finding} |

## Recommendations

### If VALID:
- Issue is ready to work on
- Suggested priority: HIGH/MEDIUM/LOW
- Next step: `/resolvegitissue {ISSUE_NUMBER}`

### If NEEDS_REFINEMENT:
The following corrections are needed:
1. [ ] {correction 1}
2. [ ] {correction 2}
3. [ ] {correction 3}

Consider running `/refinegitissue {ISSUE_NUMBER}` to update the issue.

### If INVALID:
- **Reason**: {why the issue is invalid}
- **Recommended Action**:
  - Close as duplicate of #{number}
  - Close as not reproducible
  - Close as already fixed in PR #{number}
  - Close as out of scope

## Next Steps

Based on the validation:
- **VALID**: Proceed with `/resolvegitissue {ISSUE_NUMBER}`
- **NEEDS_REFINEMENT**: Run `/refinegitissue {ISSUE_NUMBER}` first
- **INVALID**: Close the issue with the recommended reason

---
*Validated with {AGENT_COUNT} agents*
*Issue URL: {ISSUE_URL}*
```

---

## Critical Reminders

**Validation Phase (MANDATORY - USE EXTERNAL AGENTS):**
- ✅ DO spawn Task agents with `subagent_type="general-purpose"` for Agents 1-3
- ✅ DO include the LITERAL Bash command in each agent prompt
- ✅ DO launch all agents in PARALLEL (single message, multiple Task calls)
- ✅ DO wait for all agents before synthesizing
- ✅ DO use 10-minute timeout per agent (600000ms)
- ❌ DO NOT use native subagent types for main validation agents
- ❌ DO NOT validate the issue yourself during Step 2
- ❌ DO NOT skip multi-agent validation
- ❌ DO NOT assume the issue is valid without verification

**Output:**
- ✅ DO provide clear VALID/NEEDS_REFINEMENT/INVALID verdict
- ✅ DO include specific evidence for each claim
- ✅ DO provide actionable next steps
- ❌ DO NOT be ambiguous about the verdict
- ❌ DO NOT skip the recommendations

---

## Usage Examples

```bash
# Basic validation (default scale 3)
/validateissue 42

# Quick validation (1 agent)
/validateissue 123 --scale=1

# Thorough validation (4 agents)
/validateissue 789 --scale=4

# Shorthand
/validateissue 7 2    # Issue #7, scale 2
```

---

## Comparison with /validate-hive-issue

| Feature | /validateissue | /validate-hive-issue |
|---------|----------------|----------------------|
| Structure | Task agents in session | Full Hive with mprocs |
| Visibility | Results in chat | Separate terminal windows |
| Setup | None required | Requires mprocs installed |
| Best for | Quick validation | Complex issues needing coordination |
| Output | Report in chat | Report file + visible agents |

Use `/validateissue` for quick inline validation.
Use `/validate-hive-issue` when you want to watch the multi-agent coordination.
