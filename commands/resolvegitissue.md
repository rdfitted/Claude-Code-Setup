---
description: Resolve a GitHub issue with multi-agent investigation, branch creation, and implementation
argument-hint: [issue-number] [--scale=N]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Write, Edit, Glob, Grep, SlashCommand]
---

# Purpose

Systematically resolve a GitHub issue by fetching issue details, creating a feature branch, spawning multiple investigation agents to understand the codebase, generating an implementation plan, and then implementing the fix/feature.

## Ralph Loop Integration

This workflow uses Ralph-style autonomous looping with a maximum of 10 iterations. The stop hook will automatically continue the loop until the issue is resolved or max iterations reached.

**How it works:**
- **First run**: Full workflow (fetch issue, investigate, implement)
- **Subsequent iterations**: Minimal continuation (check git state, continue from where you left off)
- **Completion**: When tests pass + PR created + all criteria verified + you signal `<promise>ISSUE_RESOLVED</promise>`

**State file**: `.claude/resolvegitissue-loop.json` tracks iteration count, issue context, and acceptance criteria.

**Context Rot Prevention:**
- Issue state is re-fetched each iteration by the stop hook
- Acceptance criteria are extracted from issue checkboxes and tracked
- Progress comments are auto-posted to the GitHub issue
- Loop blocks completion if criteria are unverified

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (`gemini`, `codex`) via Bash for multi-model diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive investigation.

## Variables

- `{ISSUE_NUMBER}`: GitHub issue number to resolve
- `{SCALE}`: Investigation depth (1-6, default: 3) - number of parallel agents
- `{ISSUE_TITLE}`: Title of the GitHub issue
- `{ISSUE_BODY}`: Body/description of the GitHub issue
- `{ISSUE_LABELS}`: Labels attached to the issue
- `{BRANCH_NAME}`: Generated branch name (e.g., `issue/123-fix-login-bug`)
- `{INVESTIGATION_RESULTS}`: Combined results from multi-agent investigation
- `{IMPLEMENTATION_PLAN}`: Generated plan to resolve the issue

## Anti-Bypass Notice

This workflow REQUIRES spawning subagents that call EXTERNAL agentic tools (Gemini CLI, Codex CLI) via Bash. You are NOT permitted to:
- Use Grep/Glob/Read to investigate the codebase yourself during Step 3
- Use native Claude subagent types ("Explore", "codebase-researcher") for investigation
- Let spawned agents use Grep/Glob/Read instead of the external CLI tools
- Skip the multi-agent investigation step for "efficiency"
- Assume you already know the solution without investigation
- Replace external agent investigation with direct codebase searches

**CORRECT**: `Task(subagent_type="general-purpose", prompt="...IMMEDIATELY use Bash tool to run: CLOUDSDK_CORE_PROJECT='' GEMINI_API_KEY=... gemini -m model -o text 'prompt'...")`
**WRONG**: `Task(subagent_type="Explore", prompt="...find files...")`
**WRONG**: `Task(subagent_type="codebase-researcher", prompt="...")`

**WHY**: The EXTERNAL multi-agent approach (Gemini, Codex) provides diverse model perspectives from different AI providers, comprehensive codebase coverage, and preserves context. Your role is to ORCHESTRATE the external agents, not replace them with native Claude agents.

## Workflow

**CRITICAL WORKFLOW REQUIREMENTS**:
1. Run the workflow in order, top to bottom
2. Do not stop in between steps
3. Complete every step before stopping
4. **Step 3 (Multi-Agent Investigation) is MANDATORY** - unless continuing from previous iteration
5. Signal completion with `<promise>ISSUE_RESOLVED</promise>` when done

---

### Step 0: Continuation Detection and State Management

**FIRST**: Check if this is a continuation of a previous run.

```bash
# Check if state file exists
if [ -f ".claude/resolvegitissue-loop.json" ]; then
    echo "CONTINUATION DETECTED"
    cat .claude/resolvegitissue-loop.json
else
    echo "FRESH START"
fi

# Check if branch for this issue already exists
git branch --list "issue/{ISSUE_NUMBER}-*"
```

**If CONTINUATION DETECTED:**
1. Read the state file to get issue number, branch name, iteration count
2. Run `git log --oneline -10` to see previous commits
3. Run `git status` to see current state
4. Run `gh issue view {ISSUE_NUMBER}` ONLY to refresh acceptance criteria (don't re-investigate)
5. **SKIP Steps 1-5** (issue already fetched, branch exists, investigation done)
6. **JUMP TO Step 6** to continue implementation from where you left off

**If FRESH START:**
1. Proceed with Steps 1-2 first
2. After Step 2 (branch created), create the enhanced state file with GitHub integration:

```bash
mkdir -p .claude

# Get repo name
REPO_NAME=$(gh repo view --json nameWithOwner -q '.nameWithOwner' 2>/dev/null || echo "")

# Extract acceptance criteria from issue body checkboxes
# This parses lines like "- [ ] Task" or "- [x] Completed task"
ISSUE_BODY=$(gh issue view {ISSUE_NUMBER} --json body -q '.body' 2>/dev/null)

# Build acceptance_criteria JSON array using jq if available
if command -v jq &> /dev/null; then
    CRITERIA_JSON=$(echo "$ISSUE_BODY" | grep -E '^\s*-\s*\[[ xX]\]' | while read line; do
        # Extract status (x = verified, space = pending)
        if echo "$line" | grep -qE '^\s*-\s*\[[xX]\]'; then
            STATUS="verified"
        else
            STATUS="pending"
        fi
        # Extract text after checkbox
        TEXT=$(echo "$line" | sed 's/^\s*-\s*\[[ xX]\]\s*//' | sed 's/"/\\"/g')
        echo "{\"id\": \"ac-$(echo "$TEXT" | md5sum | cut -c1-8)\", \"text\": \"$TEXT\", \"status\": \"$STATUS\"}"
    done | jq -s '.')
else
    CRITERIA_JSON="[]"
fi

# Create enhanced state file
cat > .claude/resolvegitissue-loop.json << EOF
{
    "issue_number": {ISSUE_NUMBER},
    "branch_name": "issue/{ISSUE_NUMBER}-{TITLE_KEBAB}",
    "iteration": 1,
    "max_iterations": 10,
    "test_command": "npm test",
    "github": {
        "repo": "$REPO_NAME",
        "fetch_on_iteration": true,
        "post_progress": true,
        "last_fetched_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    },
    "acceptance_criteria": $CRITERIA_JSON,
    "iteration_history": []
}
EOF

echo "Enhanced state file created for Ralph loop (max 10 iterations)"
echo "GitHub integration enabled: re-fetch on iteration, progress posting"
echo "Acceptance criteria extracted: $(echo "$CRITERIA_JSON" | jq 'length' 2>/dev/null || echo "0") items"
```

**Note**: If jq is not available, acceptance criteria will be empty and you should manually track them.

3. Continue with Step 3 onwards

---

### Step 1: Fetch GitHub Issue Details

```bash
# Get comprehensive issue information
gh issue view {ISSUE_NUMBER} --json number,title,body,labels,state,author,createdAt,comments

# Extract key information:
# - Issue title (for branch naming)
# - Issue body (for understanding requirements)
# - Labels (bug, feature, enhancement, etc.)
# - Comments (additional context)
```

**Parse the issue to understand:**
- Is this a bug fix, feature, or enhancement?
- What are the acceptance criteria?
- Are there any linked PRs or related issues?
- What context do comments provide?

---

### Step 2: Create Feature Branch (Git Safety Check)

**CRITICAL**: Never work on main/master/staging directly.

```bash
# 1. Run gitinfo slash command
Use SlashCommand tool: command="/gitinfo"

# 2. Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# 3. Generate branch name from issue
# Format: issue/{number}-{kebab-case-title}
# Examples:
#   Issue #42 "Fix login timeout" → issue/42-fix-login-timeout
#   Issue #123 "Add dark mode" → issue/123-add-dark-mode

# 4. Create and checkout new branch
git checkout -b issue/{ISSUE_NUMBER}-{ISSUE_TITLE_KEBAB_CASE}

echo "✅ Created branch: issue/{ISSUE_NUMBER}-{ISSUE_TITLE_KEBAB_CASE}"
```

**Branch Naming Rules:**
- Always prefix with `issue/`
- Include issue number for traceability
- Convert title to kebab-case (max 50 chars)
- Remove special characters

---

### Step 3: Multi-Agent Investigation (MANDATORY - OpenCode AGENTS)

**VALIDATION CHECKPOINT**: You MUST spawn Task agents that call OpenCode CLI via Bash. All file scouts use OpenCode models for lightweight, cost-effective codebase search.

**Scale Levels:**
```
Scale 1: 1 agent  (OpenCode BigPickle)
Scale 2: 2 agents (BigPickle + GLM 4.7)
Scale 3: 3 agents (BigPickle + GLM 4.7 + Grok Code)
Scale 4: 4 agents (all 4 OpenCode models) **[DEFAULT]**
```

**HOW TO SPAWN AGENTS - EXACT FORMAT:**

You MUST use the Task tool with `subagent_type="general-purpose"` and include the EXACT Bash command in the prompt. The agent's job is to run the Bash command and return results.

**Agent 1 - OpenCode BigPickle (Deep Analysis):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase investigation agent using OpenCode BigPickle.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle \"Investigate codebase for GitHub issue: {ISSUE_TITLE}. {ISSUE_BODY}. Find all relevant files, architecture patterns, and potential solutions. Return file paths with line numbers.\"

After the command completes, format the results as:
## Files Found
- <file_path> (offset: N, limit: M) - Relevance: HIGH/MEDIUM/LOW

## Root Cause Analysis
[BigPickle's analysis]

## Recommended Fix
[BigPickle's recommendation]"
)
```

**Agent 2 - OpenCode GLM 4.7 (Pattern Recognition) - scale >= 2:**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase investigation agent using OpenCode GLM 4.7.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free \"Analyze codebase for GitHub issue: {ISSUE_TITLE}. Focus on code organization, patterns, and affected components. Return file paths with observations.\"

After the command completes, format the results as:
## Files Found
- <file_path> (offset: N, limit: M)

## Code Patterns
[Patterns identified by GLM 4.7]

## Key Components
[List of main files/modules involved]"
)
```

**Agent 3 - OpenCode Grok Code (Quick Search) - scale >= 3:**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase investigation agent using OpenCode Grok Code.

IMMEDIATELY use the Bash tool to run this EXACT command (3 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code \"Scout codebase for GitHub issue: {ISSUE_TITLE}. {ISSUE_BODY}. Identify entry points, test files, and implementation approach. Return file paths with notes.\"

After the command completes, format the results as:
## Files Found
- <file_path> (offset: N, limit: M)

## Entry Points
[Key entry points identified]

## Implementation Approach
[Grok's recommended approach]"
)
```

**CRITICAL EXECUTION RULES:**
1. Launch ALL agents in parallel using a SINGLE message with multiple Task tool calls
2. Each agent MUST use `subagent_type="general-purpose"`
3. Each agent prompt MUST include the literal Bash command to run
4. Use 180000ms (3 minute) timeout on Bash calls
5. Use ONLY OpenCode agents (BigPickle, GLM 4.7, Grok Code) for file scouts
6. **If tie on findings**: Claude (orchestrator) reviews evidence and decides

---

### Step 4: Synthesize Investigation Results

After all agents return, synthesize findings:

1. **Deduplicate file paths** - Merge overlapping findings
2. **Rank by consensus** - Files found by multiple agents = higher priority
3. **Categorize findings**:
   - Core files to modify
   - Test files to update
   - Configuration changes needed
   - Documentation updates

4. **Identify**:
   - Root cause (for bugs)
   - Implementation approach (for features)
   - Potential risks or blockers

---

### Step 5: Generate Implementation Plan

Based on investigation results, create a detailed implementation plan:

```markdown
# Implementation Plan: Issue #{ISSUE_NUMBER}

## Issue Summary
**Title**: {ISSUE_TITLE}
**Type**: Bug Fix / Feature / Enhancement
**Branch**: issue/{ISSUE_NUMBER}-{title}

## Investigation Summary
- **Agents Used**: {count}
- **Files Identified**: {count}
- **Consensus Level**: {HIGH/MEDIUM/LOW}

## Root Cause / Requirements Analysis
{Analysis from investigation}

## Implementation Steps
1. [ ] Step 1 - Specific file and changes
2. [ ] Step 2 - Specific file and changes
...

## Files to Modify
- `path/to/file1.ts` - Description of changes
- `path/to/file2.tsx` - Description of changes

## Files to Create
- `path/to/new/file.ts` - Purpose

## Tests to Add/Update
- `path/to/test.spec.ts` - Test cases to add

## Acceptance Criteria
- [ ] Criterion 1 (from issue)
- [ ] Criterion 2 (from issue)

## Risks & Considerations
- Risk 1: Mitigation
- Risk 2: Mitigation
```

---

### Step 6: Create TODO List and Implement

Use TodoWrite to create comprehensive task list from the plan:

```json
[
  {"content": "Modify core file X", "activeForm": "Modifying core file X", "status": "pending"},
  {"content": "Update related component Y", "activeForm": "Updating related component Y", "status": "pending"},
  {"content": "Add unit tests", "activeForm": "Adding unit tests", "status": "pending"},
  {"content": "Update integration tests", "activeForm": "Updating integration tests", "status": "pending"},
  {"content": "Run test suite", "activeForm": "Running test suite", "status": "pending"}
]
```

**Implementation Process:**
1. Mark TODO as in_progress before starting each task
2. Read relevant files identified in investigation
3. Make required changes using Edit/Write tools
4. Mark TODO as completed
5. Continue until all TODOs complete

---

### Step 7: Test and Validate

```bash
# Run appropriate test commands based on project type
npm test          # Node.js
pytest            # Python
cargo test        # Rust
go test ./...     # Go

# Run linting
npm run lint      # or equivalent

# Type checking (if applicable)
npm run typecheck # TypeScript
mypy .            # Python
```

**If tests fail:**
1. Analyze failure output
2. Create new TODOs for fixes
3. Iterate until all tests pass

---

### Step 8: Commit, Push, and Report

```bash
# Stage all changes
git add .

# Commit with conventional commit format referencing issue
git commit -m "fix: {brief description}

Resolves #{ISSUE_NUMBER}

- Change 1
- Change 2
- Change 3

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote
git push -u origin issue/{ISSUE_NUMBER}-{title}

# Optionally create PR
gh pr create --title "Fix: {ISSUE_TITLE}" --body "Resolves #{ISSUE_NUMBER}

## Changes
- Change 1
- Change 2

## Testing
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing completed

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

---

### Step 9: Signal Completion (REQUIRED for Ralph Loop)

After PR is created and all tests pass, you MUST signal completion to exit the Ralph loop.

1. **Verify completion criteria:**
```bash
# Verify PR exists
gh pr list --head "issue/{ISSUE_NUMBER}-{title}" --json number,url

# Verify git is clean
git status --porcelain

# Verify tests pass (run one more time)
npm test  # or appropriate test command

# Verify all acceptance criteria are marked as verified
if command -v jq &> /dev/null; then
    UNVERIFIED=$(jq '[.acceptance_criteria[] | select(.status != "verified")] | length' .claude/resolvegitissue-loop.json 2>/dev/null || echo "0")
    echo "Unverified criteria: $UNVERIFIED"
fi
```

2. **Mark acceptance criteria as verified:**

Before signaling completion, update the state file to mark criteria as verified:
```bash
# Mark a specific criterion as verified (use jq)
if command -v jq &> /dev/null; then
    # Mark criterion by matching text (example)
    jq '(.acceptance_criteria[] | select(.text | contains("YOUR_CRITERION_TEXT"))) .status = "verified"' \
        .claude/resolvegitissue-loop.json > /tmp/state.json && \
        mv /tmp/state.json .claude/resolvegitissue-loop.json
fi
```

Or mark all criteria as verified if you've addressed them all:
```bash
if command -v jq &> /dev/null; then
    jq '.acceptance_criteria[].status = "verified"' \
        .claude/resolvegitissue-loop.json > /tmp/state.json && \
        mv /tmp/state.json .claude/resolvegitissue-loop.json
fi
```

3. **If ALL criteria met, output the completion signal:**

```
<promise>ISSUE_RESOLVED</promise>
```

4. **The stop hook will verify and clean up:**
- The stop hook checks PR exists, git is clean, and all criteria are verified
- If verification passes, it cleans up the state file automatically
- If verification fails, the loop continues

**CRITICAL**: Only output `<promise>ISSUE_RESOLVED</promise>` when:
- PR has been created and pushed
- All tests are passing
- Git working directory is clean
- All acceptance criteria are marked as "verified" in the state file

Do NOT output this promise to escape the loop early. The loop exists to ensure complete resolution.

---

## Report Format

```markdown
# GitHub Issue Resolved: #{ISSUE_NUMBER}

## Issue Details
**Title**: {ISSUE_TITLE}
**Type**: {bug/feature/enhancement}
**Labels**: {labels}
**Branch**: `issue/{ISSUE_NUMBER}-{title}`

## Investigation Summary
- **Agents Spawned**: {count}
- **Files Analyzed**: {count}
- **Investigation Time**: {duration}

### Agent Results (OpenCode)
| Agent | Files Found | Key Insight |
|-------|-------------|-------------|
| BigPickle | {count} | {insight} |
| GLM 4.7 | {count} | {insight} |
| Grok Code | {count} | {insight} |

**Consensus**: {3/3 | 2/3 | TIE → Claude tie-breaker}

### Consensus Analysis
- **High Confidence Files**: {list}
- **Root Cause Identified**: {yes/no}
- **Solution Approach**: {approach}

## Implementation Summary
- **Files Modified**: {count}
- **Files Created**: {count}
- **Tests Added**: {count}
- **Lines Changed**: +{added} -{removed}

### Files Changed
- `path/to/file1.ts` - Description
- `path/to/file2.tsx` - Description

## Test Results
**Status**: ✅ PASSED / ❌ FAILED
**Test Command**: {command}
**Coverage**: {if available}

## Git Operations
- ✅ Branch created: `issue/{ISSUE_NUMBER}-{title}`
- ✅ Changes committed
- ✅ Pushed to remote
- ✅ PR created: {PR_URL}

## Next Steps
1. Review PR: {PR_URL}
2. Request code review
3. Address any feedback
4. Merge when approved

---
✅ Issue #{ISSUE_NUMBER} resolved on branch `issue/{ISSUE_NUMBER}-{title}`
🔗 PR: {PR_URL}
```

---

## Critical Reminders

**Investigation Phase (MANDATORY - USE OpenCode AGENTS):**
- ✅ DO use ONLY OpenCode agents (BigPickle, GLM 4.7, Grok Code) for file scouts
- ✅ DO spawn Task agents with `subagent_type="general-purpose"`
- ✅ DO include the LITERAL Bash command in each agent prompt (`opencode run`)
- ✅ DO launch all agents in PARALLEL (single message, multiple Task calls)
- ✅ DO wait for all agents before synthesizing
- ✅ DO use 3-minute timeout per agent (180000ms)
- ❌ DO NOT use Gemini, Codex, or Claude Haiku for file scouts
- ❌ DO NOT let agents use Grep/Glob/Read instead of OpenCode CLI
- ❌ DO NOT search codebase yourself during Step 3
- ❌ DO NOT skip multi-agent investigation
- ❌ DO NOT assume you know the solution

**Git Safety:**
- ✅ DO always create feature branch from issue
- ✅ DO include issue number in branch name
- ✅ DO reference issue in commit message
- 🚫 NEVER commit directly to main/master/staging

**Implementation:**
- ✅ DO create comprehensive TODO list
- ✅ DO mark TODOs as in_progress/completed
- ✅ DO run tests before committing
- ✅ DO create PR with issue reference
- ❌ DO NOT stop before all TODOs complete
- ❌ DO NOT skip testing

**Ralph Loop (Autonomous Continuation):**
- ✅ DO check for continuation state in Step 0
- ✅ DO skip investigation if continuing (state file exists)
- ✅ DO create enhanced state file after branch creation (first run)
- ✅ DO signal `<promise>ISSUE_RESOLVED</promise>` when truly complete
- ✅ DO mark acceptance criteria as "verified" before signaling completion
- ✅ DO let the stop hook clean up the state file
- ❌ DO NOT output completion promise until PR created + tests pass + criteria verified
- ❌ DO NOT re-run multi-agent investigation on continuation
- ❌ DO NOT exceed 10 iterations without human review

**GitHub Integration (Context Rot Prevention):**
- ✅ DO extract acceptance criteria from issue checkboxes into state file
- ✅ DO enable `fetch_on_iteration` and `post_progress` in state file
- ✅ DO mark criteria as "verified" as you complete them
- ✅ DO let the stop hook post progress comments to the issue
- ❌ DO NOT manually delete the state file (hook handles cleanup)
- ❌ DO NOT forget to verify all criteria before signaling completion

---

## Usage Examples

```bash
# Basic usage (default scale 3)
/resolvegitissue 42

# With scale parameter
/resolvegitissue 123 --scale=5

# Shorthand
/resolvegitissue 7 2    # Issue #7, scale 2
```

---

## Why Multi-Agent Investigation

- **Context isolation**: Each agent runs in separate context, preserving main context window
- **Model diversity**: Different models (Gemini, GPT, Claude) provide different perspectives
- **Parallel execution**: All investigations run simultaneously
- **Higher confidence**: Multiple models agreeing = higher confidence in findings
- **Comprehensive coverage**: Different models may find different relevant files
- **Reduced bias**: Multiple perspectives reduce single-model blind spots
