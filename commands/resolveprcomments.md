---
description: Resolve all PR comments with multi-agent codebase verification
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Edit, Write, Glob, Grep]
---

# Purpose

Systematically resolve all new PR comments by spawning multiple verification agents (using different models) to check concerns against the codebase, categorizing as VALID or MISTAKEN, and implementing fixes only for VALID issues.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (`gemini`, `codex`) via Bash for multi-model verification diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive PR comment verification.

## ⛔ ANTI-BYPASS NOTICE ⛔

This workflow REQUIRES spawning subagents via the Task tool. You are NOT permitted to:
- Use Grep/Glob/Read to verify comments yourself
- Skip the multi-agent verification step for "efficiency"
- Assume you already know whether a comment is VALID or MISTAKEN
- Replace subagent verification with direct codebase searches

**WHY**: The multi-agent approach provides diverse model perspectives and preserves context. Your role is to ORCHESTRATE the agents, not replace them.

## Workflow

**CRITICAL WORKFLOW REQUIREMENTS**:
1. Run the workflow in order, top to bottom
2. Do not stop in between steps
3. Complete every step before stopping
4. **Step 2 (Subagent Verification) is MANDATORY** - you MUST spawn Task agents, never verify directly yourself

**VALIDATION CHECKPOINT**: Before proceeding to Step 3, confirm you have spawned at least 3 Task agents. If you have not used the Task tool to spawn verification agents, STOP and go back to Step 2.

### Step 1: Get New Comments
```
git log -1 --format="%at"
gh api repos/{owner}/{repo}/pulls/{pr}/comments --jq ".[] | select((.created_at | fromdateiso8601) > {timestamp})"

Extract key concerns from each comment in memory (no files needed).
```

### Step 2: Spawn Verification Agents in Parallel

**⛔ MANDATORY - NO EXCEPTIONS ⛔**

You MUST spawn verification subagents. DO NOT:
- Skip this step
- Perform verification yourself instead of spawning agents
- Decide that agents are unnecessary
- Search the codebase directly without agents

REQUIRED ACTIONS:
1. For EVERY comment concern, spawn exactly 4 OpenCode agents
2. Launch ALL agents in parallel using a SINGLE message with multiple Task tool calls
3. WAIT for all agent results before proceeding to Step 3

Example: If 5 comments, spawn 20 agents total (5 comments × 4 agents each).

FAILURE TO SPAWN AGENTS IS A WORKFLOW VIOLATION.

**Agent 1 - OpenCode BigPickle (Deep Analysis):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase verification scout using OpenCode BigPickle.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle \"Search codebase for evidence related to: {COMMENT_CONCERN}. Find files that address this concern, existing implementations, and evidence for whether implementation is needed.\"

Report back:
- Files found that address this concern
- Existing implementations that contradict or support the PR comment
- Evidence for whether implementation is needed

Format: Bullet list of file paths with evidence summary."
)
```

**Agent 2 - OpenCode GLM 4.7 (Pattern Recognition):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase verification scout using OpenCode GLM 4.7.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free \"Search codebase for evidence related to: {COMMENT_CONCERN}. Find existing implementations and architectural patterns that address this concern.\"

Report back:
- Files found that address this concern
- Existing implementations that contradict or support the PR comment
- Evidence for whether implementation is needed

Format: Bullet list of file paths with evidence summary."
)
```

**Agent 3 - OpenCode Grok Code (Quick Search):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase verification scout using OpenCode Grok Code.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code \"Search codebase for evidence related to: {COMMENT_CONCERN}. Identify existing implementations, test coverage, and code patterns that address this concern.\"

Report back:
- Files found that address this concern
- Existing implementations that contradict or support the PR comment
- Evidence for whether implementation is needed

Format: Bullet list of file paths with evidence summary."
)
```

**Example agent spawning for multiple comments:**
Launch ALL agents in PARALLEL using a SINGLE message with multiple Task tool calls:
```
Task(subagent_type="general-purpose", prompt="[BigPickle] Verify: migration down_revision chain...")
Task(subagent_type="general-purpose", prompt="[GLM 4.7] Verify: migration down_revision chain...")
Task(subagent_type="general-purpose", prompt="[Grok Code] Verify: migration down_revision chain...")
Task(subagent_type="general-purpose", prompt="[BigPickle] Verify: TimestampMixin patterns...")
Task(subagent_type="general-purpose", prompt="[GLM 4.7] Verify: TimestampMixin patterns...")
Task(subagent_type="general-purpose", prompt="[Grok Code] Verify: TimestampMixin patterns...")
```
(continue for all comments × 3 agents each)

Collect all agent results.
```

### Step 3: Categorize Comments Using Agent Results
```
For each comment, review results from its 3 OpenCode verification agents:

Consensus logic:
- 3/3 agents agree "not found" → ✅ VALID (high confidence)
- 2/3 agents agree "not found" → ✅ VALID (medium confidence)
- 3/3 agents found existing solution → ❌ MISTAKEN (high confidence)
- 2/3 agents found existing solution → ❌ MISTAKEN (medium confidence)
- **Tie** → Claude (orchestrator) reviews all evidence and makes final call

For MISTAKEN comments, post reply with agent evidence:
gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies \
  -f body="Verified by 3 OpenCode agents (BigPickle, GLM 4.7, Grok Code): [evidence from agents]"

Store list of VALID comments for implementation.
```

### Step 3b: Spawn Grok Scouts for Context (2 per VALID comment)

**For each VALID comment, spawn 2 Grok scouts in parallel:**

**Grok Scout 1 - Learnings Scout (per comment):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a Learnings Scout using OpenCode Grok Code.

IMMEDIATELY use the Bash tool to run this EXACT command (2 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code \"Search for relevant learnings for this PR comment: {COMMENT_TEXT}

1. Grep .ai-docs/learnings.jsonl for keywords from the comment
2. Read .ai-docs/project-dna.md for relevant patterns
3. Extract insights that might help fix this issue

Return:
## Relevant Learnings
- [learning 1]
- [learning 2]

## Project DNA Patterns
- [pattern 1]
- [pattern 2]

## Suggested Approach
- Based on past learnings, here's how to approach this fix...
\"

Report the findings."
)
```

**Grok Scout 2 - Standards Scout (per comment):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a Standards Scout using OpenCode Grok Code.

IMMEDIATELY use the Bash tool to run this EXACT command (2 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code \"Search for relevant code standards for this PR comment: {COMMENT_TEXT}

1. Read CLAUDE.md for coding standards and conventions
2. Identify standards that apply to this specific fix
3. Note any style requirements or patterns to follow

Return:
## Applicable Code Standards
- [standard 1]
- [standard 2]

## Style Requirements
- [requirement 1]
- [requirement 2]

## Must Follow
- These specific rules MUST be followed when fixing this comment...
\"

Report the findings."
)
```

**Collect scout findings** and attach to each VALID comment for use in Step 5.

### Step 4: Create Implementation Plan
```
Use TodoWrite to create task for each VALID comment.

Store implementation plan.
```

### Step 5: Implement All Fixes
```
For each VALID comment:
- Review the Grok scout findings (learnings + standards)
- Read relevant files
- Apply fix following the CODE_STANDARDS from scout findings
- Consider PROJECT_DNA patterns from scout findings
- Mark todo completed

Collect all changes made.
```

### Step 6: Code Simplification (Codex 5.2-codex)

**Spawn a Codex agent to simplify the code you just modified.**

```
Task(
  subagent_type="general-purpose",
  prompt="You are a code simplifier using Codex 5.2-codex.

IMMEDIATELY use the Bash tool to run this EXACT command:

codex --dangerously-bypass-approvals-and-sandbox -m 5.2-codex \"Review and simplify the recently modified files. Apply the code-simplifier principles:

**Principles:**
- Preserve functionality: Do not change what the code does
- Apply project standards from CLAUDE.md
- Enhance clarity: Reduce nesting, remove redundant code, improve naming, consolidate related logic, remove obvious comments, avoid nested ternaries
- Maintain balance: Avoid over-simplifying or overly clever solutions
- Focus scope: Only refine the files that were just modified

**Files to simplify:**
{LIST_OF_MODIFIED_FILES}

Apply minimal, safe refactors and keep interfaces stable.\"

Report back what was simplified."
)
```

### Step 7: Commit and Push

> **Note**: Learning capture and curation are handled automatically by the `learning_capture.py` Stop hook.
```
Clean up any temporary files created during workflow:
rm -f new_comments.json verification_results.json

Run linting and tests.
Commit changes with descriptive message including:
Co-Authored-By: Codex 5.2-codex <noreply@openai.com>

Push to remote branch.

Generate final report.
```

## Agent Configuration

**Verification Agents (3 OpenCode agents per comment concern):**
1. OpenCode BigPickle - Deep analysis, architecture patterns
2. OpenCode GLM 4.7 - Code organization and patterns
3. OpenCode Grok Code - Quick search, test coverage

Each agent uses different model perspective to verify the same PR comment concern.

**Context Scouts (2 Grok agents per VALID comment):**
- Grok Scout 1 (Learnings) - Searches learnings.jsonl + project-dna.md for relevant insights
- Grok Scout 2 (Standards) - Searches CLAUDE.md for applicable code standards

**Code Simplification Agent:**
- Codex 5.2-codex - Simplifies modified code while preserving functionality

References the `.codex/skills/code-simplifier/SKILL.md` principles.

## Agentic Tool Commands

```bash
# OpenCode BigPickle
OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle "Search codebase for: {concern}. Find existing implementations and return file paths with evidence."

# OpenCode GLM 4.7
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Search codebase for: {concern}. Find existing implementations and return file paths with evidence."

# OpenCode Grok Code
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "Search codebase for: {concern}. Find existing implementations and return file paths with evidence."

```

## Why Multi-Agent Verification

- **Context isolation**: Each agent runs in separate context, preserving main context window
- **Cost-effective**: OpenCode models are lightweight and fast for file scouts
- **Parallel execution**: All concerns verified simultaneously
- **Consensus confidence**: 3/3 or 2/3 agreement = high reliability

## Report Format

```markdown
# PR Comment Resolution Complete

## Verification Summary
- Comments verified: {count}
- Agents spawned: {count * 3} verification + {valid_count * 2} context scouts + 1 simplifier
- Models used: OpenCode BigPickle, GLM 4.7, Grok Code, Codex 5.2-codex
- VALID (needs implementation): {count}
- MISTAKEN (already exists): {count}
- Ties resolved by Claude: {count}

## Changes Made
{list of files changed}

## Code Simplification
{list of simplifications applied by Codex 5.2-codex}

## Responses Posted
{list of MISTAKEN comments with agent evidence}

## Status
✅ All changes committed and pushed
✅ PR ready for re-review
```
