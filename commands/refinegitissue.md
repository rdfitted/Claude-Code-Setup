---
description: Refine a GitHub issue using multi-agent investigation
argument-hint: <issue-number> [--mode=rewrite|comment] [--scale=N]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Write, Edit, Glob, Grep]
---

# Purpose

Refine an existing GitHub issue by reassessing the codebase with multi-agent scouts, verifying accuracy, and either rewriting the issue body or adding a detailed comment with updated findings.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (`gemini`, `codex`) via Bash for multi-model diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive reassessment.

## Variables

- `{ISSUE_NUMBER}`: GitHub issue number to refine
- `{MODE}`: "rewrite" to update issue body, "comment" to add comment (default: comment)
- `{SCALE}`: Investigation depth (1-6, default: 3) - determines agent coverage
- `{CURRENT_ISSUE}`: Fetched issue details (title, body, labels, comments)
- `{REASSESSMENT_RESULTS}`: Combined analysis from investigation agents
- `{REFINED_CONTENT}`: Final refined issue content

## Anti-Bypass Notice

This workflow REQUIRES spawning subagents that call EXTERNAL agentic tools (Gemini CLI, Codex CLI) via Bash. You are NOT permitted to:
- Use Grep/Glob/Read to investigate the codebase yourself during investigation steps
- Use native Claude subagent types ("Explore", "codebase-researcher") for the main investigation
- Skip the multi-agent investigation for "efficiency"
- Refine the issue without proper reassessment

**CORRECT**: `Task(subagent_type="general-purpose", prompt="...IMMEDIATELY use Bash tool to run: CLOUDSDK_CORE_PROJECT='' GEMINI_API_KEY=... gemini -m model -o text 'prompt'...")`
**WRONG**: `Task(subagent_type="Explore", prompt="...find files...")`

## Workflow

**CRITICAL WORKFLOW REQUIREMENTS**:
1. Run the workflow in order, top to bottom
2. Do not stop in between steps
3. Complete every step before stopping
4. Multi-agent investigation is MANDATORY

---

### Step 1: Parse Input and Fetch Issue

```bash
# Fetch current issue details
gh issue view {ISSUE_NUMBER} --json number,title,body,labels,state,comments,createdAt,author,url
```

Extract:
- `ISSUE_NUMBER`
- `ISSUE_TITLE`
- `ISSUE_BODY`
- `ISSUE_LABELS`
- `EXISTING_COMMENTS`
- `ISSUE_URL`
- `MODE` (default: comment)
- `SCALE` (default: 3)

---

### Step 2: Create Todo List

```json
[
  {
    "content": "Fetch and analyze current issue",
    "activeForm": "Fetching and analyzing current issue",
    "status": "pending"
  },
  {
    "content": "Multi-agent codebase reassessment",
    "activeForm": "Running multi-agent codebase reassessment",
    "status": "pending"
  },
  {
    "content": "Verify issue accuracy and identify changes",
    "activeForm": "Verifying issue accuracy and identifying changes",
    "status": "pending"
  },
  {
    "content": "Synthesize refinements",
    "activeForm": "Synthesizing refinements",
    "status": "pending"
  },
  {
    "content": "Apply refinement ({MODE})",
    "activeForm": "Applying refinement ({MODE})",
    "status": "pending"
  }
]
```

---

### Step 3: Multi-Agent Codebase Reassessment (MANDATORY - EXTERNAL AGENTS)

**Scale Levels:**
```
Scale 1: 4 agents  (Gemini Flash + 3 OpenCode Scouts: BigPickle, GLM 4.7, Grok Code)
Scale 2: 5 agents  (Gemini Flash, Gemini Lite + 3 OpenCode Scouts)
Scale 3: 6 agents  (Gemini Flash, Gemini Lite, Codex + 3 OpenCode Scouts)
Scale 4: 9 agents  (Above + Claude Haiku + 2 Web Search Agents: Gemini, GLM 4.7)
Scale 5: 11 agents (Above + Git History & PR verification agents)
Scale 6: 13 agents (Maximum coverage with additional documentation search)
```

**CRITICAL**: Launch ALL agents in PARALLEL using a SINGLE message with multiple Task tool calls.

**Agent 1 - Gemini Flash (REQUIRED for all scales):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase reassessment agent using Gemini Flash.

CONTEXT - Current GitHub Issue #{ISSUE_NUMBER}:
Title: {ISSUE_TITLE}
Body: {ISSUE_BODY}
Labels: {ISSUE_LABELS}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-flash-preview -o text \"Reassess this GitHub issue against the current codebase:

Issue: {ISSUE_TITLE}
Description: {ISSUE_BODY}

Verify:
1. Do the files mentioned still exist? Have they changed?
2. Is the described problem/feature still relevant?
3. Are there new files or changes that should be referenced?
4. Is any information in the issue now outdated or incorrect?
5. What new context should be added?

Return findings with file paths and specific changes needed.\"

After the command completes, format the results as:
## Current State Verification
- [What's still accurate]
- [What has changed]

## Files to Update in Issue
- <file_path> - [why it should be added/removed/updated]

## Corrections Needed
[List specific inaccuracies]

## New Context to Add
[Additional information discovered]"
)
```

**Agent 2 - Gemini Lite (scale >= 2):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a quick verification agent using Gemini Lite.

CONTEXT - Current GitHub Issue #{ISSUE_NUMBER}:
Title: {ISSUE_TITLE}
Body: {ISSUE_BODY}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-2.5-flash-lite -o text \"Quick verification scan for issue: {ISSUE_TITLE}

Check:
1. Any recent commits or PRs related to this issue?
2. Test files that cover this area - have they changed?
3. Configuration changes that might affect this issue?
4. New dependencies or removed code?

Focus on what has CHANGED since the issue was created.\"

After the command completes, format the results as:
## Recent Changes Detected
- [List relevant changes]

## Related Commits/PRs
- [Any found]

## Test Coverage Updates
- [Changes to test files]

## Configuration Changes
- [Relevant config changes]"
)
```

**Agent 3 - Codex (scale >= 3):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a technical verification agent using OpenAI Codex.

CONTEXT - Current GitHub Issue #{ISSUE_NUMBER}:
Title: {ISSUE_TITLE}
Body: {ISSUE_BODY}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

codex exec -m gpt-5.2 -s read-only -c model_reasoning_effort=\"high\" --skip-git-repo-check \"Deep technical reassessment of issue: {ISSUE_TITLE}

Original description: {ISSUE_BODY}

Analyze:
1. Technical accuracy of the issue description
2. Are the proposed solutions still valid?
3. New edge cases or considerations discovered?
4. Security or performance implications not originally mentioned?
5. Dependencies that have been updated?

Provide technical corrections and additions needed.\"

After the command completes, format the results as:
## Technical Accuracy
- [Verified / Needs correction]

## Solution Validity
- [Still valid / Needs update because...]

## New Considerations
- Edge cases: [list]
- Security: [concerns]
- Performance: [implications]

## Dependency Updates
- [Relevant dependency changes]"
)
```

### OpenCode Scout Agents (scale >= 1)

These OpenCode scouts run as BLOCKING agents for all scales. Launch all 3 in parallel with other agents.

**Scout - OpenCode BigPickle (scale >= 1):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a reassessment scout using OpenCode BigPickle.

CONTEXT - Current GitHub Issue #{ISSUE_NUMBER}:
Title: {ISSUE_TITLE}
Body: {ISSUE_BODY}
Labels: {ISSUE_LABELS}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

opencode run -m opencode/big-pickle \"Reassess this GitHub issue against the current codebase:

Issue: {ISSUE_TITLE}
Description: {ISSUE_BODY}

Verify:
1. Do the files mentioned still exist? Have they changed?
2. Are there code quality issues not mentioned in the issue?
3. Any edge cases or potential bugs discovered?
4. What additional context should be added?

Return findings with file paths and specific observations.\"

After the command completes, format the results as:
## Code Quality Observations
- [Observations found]

## Files Verified
- <file_path> - [status: exists/changed/removed]

## Edge Cases Discovered
- [Edge cases]

## Additional Context
- [New context to add]"
)
```

**Scout - OpenCode GLM 4.7 (scale >= 1):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a reassessment scout using OpenCode GLM 4.7.

CONTEXT - Current GitHub Issue #{ISSUE_NUMBER}:
Title: {ISSUE_TITLE}
Body: {ISSUE_BODY}
Labels: {ISSUE_LABELS}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

opencode run -m opencode/glm-4.7-free \"Analyze this GitHub issue against current codebase state:

Issue: {ISSUE_TITLE}
Description: {ISSUE_BODY}

Focus on:
1. Architecture patterns affected by this issue
2. Backend/frontend coherence concerns
3. Data flow implications
4. Integration points that may have changed

Return structured findings with file paths.\"

After the command completes, format the results as:
## Architecture Analysis
- [Patterns identified]

## Coherence Concerns
- [Backend/frontend issues]

## Data Flow Implications
- [Data flow changes]

## Integration Points
- [Integration changes]"
)
```

**Scout - OpenCode Grok Code (scale >= 1):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a reassessment scout using OpenCode Grok Code.

CONTEXT - Current GitHub Issue #{ISSUE_NUMBER}:
Title: {ISSUE_TITLE}
Body: {ISSUE_BODY}
Labels: {ISSUE_LABELS}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

opencode run -m opencode/grok-code \"Quick verification scan for issue: {ISSUE_TITLE}

Original description: {ISSUE_BODY}

Check:
1. Test coverage for areas mentioned in the issue
2. Recent code patterns that affect this issue
3. Quick wins or low-hanging fruit discovered
4. Technical debt related to this issue

Return file paths with observations.\"

After the command completes, format the results as:
## Test Coverage Status
- [Coverage observations]

## Code Patterns
- [Patterns found]

## Quick Wins
- [Low-hanging fruit]

## Technical Debt
- [Related debt items]"
)
```

**Note**: Launch all 3 OpenCode scouts in PARALLEL with other agents. These are BLOCKING agents - wait for results.

---

**Agent 4 - Claude Haiku Native (scale >= 4):**
```
Task(
  subagent_type="Explore",
  model="haiku",
  prompt="Reassess this GitHub issue against the current codebase:

Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}
{ISSUE_BODY}

Find:
1. Current state of files mentioned in the issue
2. Any new files that should be referenced
3. Changes to the codebase since issue creation
4. Documentation that should be linked
5. Related issues or PRs

Return detailed findings with file paths and line numbers."
)
```

### Web Search Agents (scale >= 4)

These agents search for external documentation, updates, and related solutions.

**Web Search - Gemini (scale >= 4):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a web search agent using Gemini.

CONTEXT - Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}
Created: {ISSUE_CREATED_AT}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-flash-preview -o text \"Search for updates, documentation changes, and community solutions related to: {ISSUE_TITLE}

Issue context: {ISSUE_BODY}

Find:
1. Updated documentation or API changes
2. Stack Overflow solutions posted since issue creation
3. GitHub issues in related projects
4. Blog posts or tutorials addressing similar issues
5. Dependency updates that may affect this issue\"

After the command completes, format the results as:
## Documentation Updates
- [Updates found]

## Community Solutions
- [Stack Overflow, forums]

## Related GitHub Issues
- [Issues in other projects]

## Dependency News
- [Relevant updates]"
)
```

**Web Search - GLM 4.7 (scale >= 4):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a web search agent using OpenCode GLM 4.7.

CONTEXT - Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}
Created: {ISSUE_CREATED_AT}

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

opencode run -m opencode/glm-4.7-free \"Search for external resources and updates related to: {ISSUE_TITLE}

Issue context: {ISSUE_BODY}

Focus on finding:
1. Technical blog posts addressing similar issues
2. Framework or library updates since issue creation
3. Best practices that have evolved
4. Security advisories relevant to this issue
5. Performance benchmarks or comparisons\"

After the command completes, format the results as:
## Technical Resources
- [Blog posts, tutorials]

## Framework/Library Updates
- [Relevant updates]

## Evolved Best Practices
- [New recommendations]

## Security Advisories
- [Relevant advisories]"
)
```

**Note**: Launch both Web Search agents in PARALLEL for scales 4+. These are BLOCKING agents - wait for results.

---

**Agents 5-6 - Git History & PR Verification (scale >= 5):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a git history verification agent.

CONTEXT - Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}
Created: {ISSUE_CREATED_AT}

IMMEDIATELY use the Bash tool to run these commands:

1. Check git log for related changes:
git log --oneline --since=\"{ISSUE_CREATED_AT}\" --all --grep=\"{KEYWORDS}\" 2>/dev/null | head -20

2. Check for related PRs:
gh pr list --state all --search \"{KEYWORDS}\" --json number,title,state,mergedAt --limit 10

3. Check for commits touching related files:
git log --oneline --since=\"{ISSUE_CREATED_AT}\" -- {RELATED_FILES} 2>/dev/null | head -20

Format results as:
## Related Commits
- [commit hash] - [message]

## Related PRs
- PR #{number} - {title} ({state})

## File History
- [Changes to files mentioned in issue]"
)
```

---

### Step 4: Synthesize Reassessment Findings

Combine all agent results to determine:

1. **Accuracy Assessment**
   - What in the original issue is still accurate?
   - What needs correction?

2. **Changes Since Creation**
   - Codebase changes affecting the issue
   - Related PRs or commits
   - New files or removed files

3. **Missing Context**
   - New edge cases discovered
   - Security/performance considerations
   - Updated dependencies

4. **Recommendations**
   - Priority adjustment needed?
   - Scope change needed?
   - Should issue be closed as resolved/stale?

---

### Step 5: Generate Refined Content

**If MODE is "rewrite":**

Generate updated issue body:
```markdown
## Description

[Updated description incorporating all findings]

## Current State (Reassessed {DATE})

**Status**: [Still relevant / Partially addressed / Needs scope change]

## Relevant Files (Updated)

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `path/to/file.ts` | 1-50 | NEW | [Added in reassessment] |
| `path/to/old.ts` | - | REMOVED | [No longer exists] |
| `path/to/changed.ts` | 10-100 | UPDATED | [File has changed] |

## Analysis

### Original Issue
[What the issue originally described]

### Current State
[What the reassessment found]

### Changes Since Creation
- [List of relevant changes]

## Updated Acceptance Criteria

- [ ] [Updated criterion 1]
- [ ] [Updated criterion 2]

## Additional Considerations

[New findings: edge cases, security, performance]

---

*Refined on {DATE} via multi-agent reassessment*
*Agents used: {count} | Files verified: {count}*
```

**If MODE is "comment":**

Generate reassessment comment:
```markdown
## Issue Reassessment - {DATE}

I've conducted a multi-agent reassessment of this issue against the current codebase.

### Summary

**Status**: [Still relevant / Partially addressed / Needs update / Consider closing]

### What's Changed

#### Codebase Changes
- [List of relevant changes since issue creation]

#### Related Activity
- [PRs, commits, or other issues]

### Accuracy Check

#### Still Accurate
- [List items that remain correct]

#### Needs Correction
- [List items that are now incorrect/outdated]

### New Findings

#### Additional Files
- `path/to/new/file.ts` - [relevance]

#### Edge Cases Discovered
- [New edge cases]

#### Technical Considerations
- [Security, performance, etc.]

### Recommendations

1. [Recommendation 1]
2. [Recommendation 2]

---

*Reassessment performed with {AGENT_COUNT} investigation agents*
*Files analyzed: {FILE_COUNT} | Confidence: {HIGH|MEDIUM|LOW}*
```

---

### Step 6: Apply Refinement

**For rewrite:**
```bash
gh issue edit {ISSUE_NUMBER} --body "$(cat <<'EOF'
{REFINED_BODY}
EOF
)"
```

**For comment:**
```bash
gh issue comment {ISSUE_NUMBER} --body "$(cat <<'EOF'
{COMMENT_CONTENT}
EOF
)"
```

---

### Step 7: Report Completion

```markdown
# GitHub Issue Refined: #{ISSUE_NUMBER}

## Details
**Issue**: #{ISSUE_NUMBER} - {ISSUE_TITLE}
**URL**: {ISSUE_URL}
**Mode**: {MODE}
**Action Taken**: {Rewrote issue body / Added reassessment comment}

## Reassessment Summary
- **Agents Spawned**: {count}
- **Files Verified**: {count}
- **Status**: {Still relevant / Partially addressed / Needs scope change / Consider closing}
- **Confidence**: {HIGH|MEDIUM|LOW}

### Agent Results
| Agent | Key Finding |
|-------|-------------|
| Gemini Flash | {finding} |
| Gemini Lite | {finding} |
| Codex | {finding} |
| OpenCode BigPickle | {finding} |
| OpenCode GLM 4.7 | {finding} |
| OpenCode Grok Code | {finding} |
| Claude Haiku | {finding} |
| Web Search Gemini | {finding} |
| Web Search GLM 4.7 | {finding} |
| Git History | {finding} |

### Changes Identified
- Corrections made: {count}
- New files added: {count}
- Outdated references removed: {count}
- New considerations added: {count}

## Next Steps
1. Review the refinement: {ISSUE_URL}
2. Update labels if needed
3. Adjust priority if recommended
4. Continue with resolution: `/resolvegitissue {ISSUE_NUMBER}`

---
✅ Issue #{ISSUE_NUMBER} refined successfully ({MODE})
🔗 URL: {ISSUE_URL}
🤖 Reassessment: {AGENT_COUNT} agents, {FILE_COUNT} files verified
```

---

## Critical Reminders

**Investigation Phase (MANDATORY - USE EXTERNAL AGENTS):**
- ✅ DO spawn Task agents with `subagent_type="general-purpose"` for external agents
- ✅ DO include the LITERAL Bash command in each agent prompt
- ✅ DO launch all agents in PARALLEL (single message, multiple Task calls)
- ✅ DO wait for all agents before synthesizing
- ✅ DO use 10-minute timeout per agent (600000ms)
- ❌ DO NOT use native subagent types for main investigation agents
- ❌ DO NOT search codebase yourself during investigation
- ❌ DO NOT skip multi-agent investigation
- ❌ DO NOT refine without proper reassessment

**Refinement:**
- ✅ DO preserve accurate original information
- ✅ DO clearly mark what changed
- ✅ DO include reassessment metadata
- ✅ DO provide actionable recommendations
- ❌ DO NOT lose valuable original context
- ❌ DO NOT add speculation without evidence
- ❌ DO NOT skip the synthesis step

---

## Usage Examples

```bash
# Add a reassessment comment (default)
/refinegitissue 123

# Rewrite the issue body with updated information
/refinegitissue 123 --mode=rewrite

# Quick reassessment (1 agent)
/refinegitissue 456 --scale=1

# Deep reassessment with git history verification
/refinegitissue 789 --mode=comment --scale=5

# Full reassessment and rewrite
/refinegitissue 42 --mode=rewrite --scale=6
```

---

## When to Use This Command

**Use /refinegitissue when:**
- Issue has been open for a while and may be stale
- Codebase has changed significantly since issue creation
- Issue lacks detail or has inaccurate information
- Before starting work on an old issue
- After a related PR was merged but issue wasn't updated
- To verify an issue is still relevant before prioritizing

**Modes:**
- `comment` (default): Non-destructive, adds findings as a comment
- `rewrite`: Updates the issue body (use when significant corrections needed)
