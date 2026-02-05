---
description: Investigate codebase and create a well-structured GitHub issue with linked files
argument-hint: [issue-description] [--scale=N] [--type=bug|feature|enhancement]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Write, Edit, Glob, Grep, SlashCommand]
---

# Purpose

Create well-structured GitHub issues by first investigating the codebase with multi-agent scouts to identify relevant files, then using multi-agent planning to understand scope and approach, and finally synthesizing all findings into a comprehensive GitHub issue.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (`gemini`, `codex`) via Bash for multi-model diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive investigation.

## Variables

- `{ISSUE_DESCRIPTION}`: User's description of the issue/feature to create
- `{SCALE}`: Investigation depth (1-6, default: 3) - number of parallel agents
- `{ISSUE_TYPE}`: Type of issue (bug, feature, enhancement) - auto-detected if not specified
- `{RELEVANT_FILES}`: Files discovered by multi-agent scout
- `{INVESTIGATION_RESULTS}`: Combined analysis from planning agents
- `{ISSUE_TITLE}`: Generated issue title
- `{ISSUE_BODY}`: Generated issue body with all context
- `{ISSUE_LABELS}`: Auto-suggested labels

## Anti-Bypass Notice

**For Scale 1-6**: This workflow REQUIRES spawning subagents that call EXTERNAL agentic tools (Gemini CLI, Codex CLI) via Bash. You are NOT permitted to:
- Use Grep/Glob/Read to investigate the codebase yourself during investigation steps
- Use native Claude subagent types ("Explore", "codebase-researcher") for the main investigation
- Skip the multi-agent investigation for "efficiency"
- Create the issue without proper investigation

**CORRECT**: `Task(subagent_type="general-purpose", prompt="...IMMEDIATELY use Bash tool to run: CLOUDSDK_CORE_PROJECT='' GEMINI_API_KEY=... gemini -m model -o text 'prompt'...")`
**WRONG**: `Task(subagent_type="Explore", prompt="...find files...")`

**EXCEPTION - Scale 0**: When `--scale=0` is specified, you MAY use Glob, Grep, and Read directly without subagents. This is for simple issues where multi-agent overhead is unnecessary.

## Workflow

**CRITICAL WORKFLOW REQUIREMENTS**:
1. Run the workflow in order, top to bottom
2. Do not stop in between steps
3. Complete every step before stopping
4. Multi-agent investigation is MANDATORY

---

### Step 1: Parse Input and Detect Issue Type

```
1. Extract issue description from user input
2. Extract scale parameter (default: 3)
3. Extract or auto-detect issue type:
   - "bug" keywords: fix, broken, error, crash, wrong, fails, doesn't work
   - "feature" keywords: add, new, implement, create, build
   - "enhancement" keywords: improve, optimize, refactor, update, better
4. Generate a clean issue title from description
```

---

### Step 2: Create Todo List

**For Scale 0 (Direct Investigation):**
```json
[
  {
    "content": "Investigate codebase directly",
    "activeForm": "Investigating codebase directly",
    "status": "pending"
  },
  {
    "content": "Synthesize findings into issue structure",
    "activeForm": "Synthesizing findings into issue structure",
    "status": "pending"
  },
  {
    "content": "Create GitHub issue",
    "activeForm": "Creating GitHub issue",
    "status": "pending"
  }
]
```

**For Scale 1-6 (Multi-Agent):**
```json
[
  {
    "content": "Scout codebase for relevant files",
    "activeForm": "Scouting codebase for relevant files",
    "status": "pending"
  },
  {
    "content": "Multi-agent investigation and analysis",
    "activeForm": "Running multi-agent investigation and analysis",
    "status": "pending"
  },
  {
    "content": "Synthesize findings into issue structure",
    "activeForm": "Synthesizing findings into issue structure",
    "status": "pending"
  },
  {
    "content": "Create GitHub issue",
    "activeForm": "Creating GitHub issue",
    "status": "pending"
  }
]
```

---

### Step 3: Codebase Investigation

**Scale Levels:**
```
Scale 0: 0 agents (Direct investigation - Claude Code only, no subagents)
Scale 1: 4 agents (Gemini Flash + 3 OpenCode Scouts: BigPickle, GLM 4.7, Grok Code)
Scale 2: 5 agents (Gemini Flash, Gemini Lite + 3 OpenCode Scouts)
Scale 3: 6 agents (Gemini Flash, Gemini Lite, Codex + 3 OpenCode Scouts)
Scale 4: 9 agents (Above + Claude Haiku + 2 Web Search Agents: Gemini, GLM 4.7)
Scale 5: 11 agents (Above + 2x documentation search via Bash)
Scale 6: 13 agents (Maximum coverage)
```

---

#### Scale 0: Direct Investigation (No Subagents)

**When to use**: Simple issues, typos, small bugs, well-understood changes where multi-agent overhead isn't needed.

**Workflow for Scale 0:**
1. Use Glob to find relevant files by pattern
2. Use Grep to search for keywords related to the issue
3. Use Read to examine the most relevant files (max 3-5 files)
4. Directly synthesize findings into issue structure

**Skip to Step 5** after completing direct investigation.

**Example direct investigation:**
```
1. Glob: Find files matching patterns related to the issue
2. Grep: Search for error messages, function names, or keywords
3. Read: Examine top 3-5 most relevant files
4. Proceed to Step 5 (Synthesize Findings)
```

---

#### Scale 1-6: Multi-Agent Investigation (EXTERNAL AGENTS)

**CRITICAL**: Launch ALL agents in PARALLEL using a SINGLE message with multiple Task tool calls.

**Agent 1 - Gemini Flash (REQUIRED for all scales):**
(Gemini CLI: using latest installed version)
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase investigation agent using Gemini Flash.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-flash-preview -o text \"Investigate codebase for: {ISSUE_DESCRIPTION}. Find all relevant files, code patterns, potential root causes, and affected areas. Return file paths with line numbers and relevance explanation.\"

After the command completes, format the results as:
## Files Found
- <file_path> (offset: N, limit: M) - Relevance: HIGH/MEDIUM/LOW - Why: [reason]

## Code Patterns Identified
[Patterns found]

## Potential Root Cause / Implementation Area
[Analysis]"
)
```

**Agent 2 - Gemini Lite (scale >= 2):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase investigation agent using Gemini Lite.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-2.5-flash-lite -o text \"Quick scan for: {ISSUE_DESCRIPTION}. Focus on entry points, key components, test files, and configuration. Return file paths with brief relevance notes.\"

After the command completes, format the results as:
## Files Found
- <file_path> (offset: N, limit: M) - [brief relevance]

## Key Components
[List of main files/modules involved]

## Test Coverage Areas
[Test files that may need updates]"
)
```

**Agent 3 - Codex (scale >= 3):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase investigation agent using OpenAI Codex.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

codex exec -m 5.2-codex -s read-only -c model_reasoning_effort=\"low\" --skip-git-repo-check \"Investigate: {ISSUE_DESCRIPTION}. Identify affected files, code patterns, dependencies, and suggest implementation approach. Focus on technical details.\"

After the command completes, format the results as:
## Files Found
- <file_path> (offset: N, limit: M) - [technical relevance]

## Dependencies & Integrations
[Dependencies that may be affected]

## Technical Approach
[Suggested implementation approach]"
)
```

**Agent 4 - Claude Haiku Native (scale >= 4):**
```
Task(
  subagent_type="Explore",
  model="haiku",
  prompt="Investigate this issue/feature request: {ISSUE_DESCRIPTION}

Find:
1. Files directly related to this issue
2. Similar patterns or implementations in the codebase
3. Test coverage for affected areas
4. Configuration or environment files that might be relevant
5. Documentation files that should be updated

Return file paths with line ranges and detailed relevance notes."
)
```

**Agents 5-6 - Documentation Search (scale >= 5):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a documentation search agent.

IMMEDIATELY use the Bash tool to run this EXACT command:

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-2.5-flash-lite -o text \"Search for documentation, best practices, and examples related to: {ISSUE_DESCRIPTION}. Find official docs, tutorials, and similar implementations.\"

Format results as:
## Documentation Resources
- **URL** - Description

## Best Practices
[Key recommendations]

## Similar Implementations
[Examples found]"
)
```

### OpenCode Scout Agents (scale >= 1)

These OpenCode scouts run as BLOCKING agents for scales 1-3. Launch all 3 in parallel.

**Scout - OpenCode BigPickle (scale >= 1):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase scout using OpenCode BigPickle.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

opencode run -m opencode/big-pickle \"Investigate codebase for issue: {ISSUE_DESCRIPTION}. Identify relevant files, potential root causes, and code quality observations. Return file paths with analysis.\"

After the command completes, format the results as:
## Files Found
- <file_path> (offset: N, limit: M) - Relevance: HIGH/MEDIUM/LOW - Why: [reason]

## Code Quality Observations
[Observations found]

## Potential Root Causes
[Analysis]"
)
```

**Scout - OpenCode GLM 4.7 (scale >= 1):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase scout using OpenCode GLM 4.7.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

opencode run -m opencode/glm-4.7-free \"Analyze codebase for issue: {ISSUE_DESCRIPTION}. Focus on architecture patterns, affected components, and potential issues. Return structured findings.\"

After the command completes, format the results as:
## Files Found
- <file_path> (offset: N, limit: M) - Relevance: HIGH/MEDIUM/LOW - Why: [reason]

## Architecture Patterns
[Patterns identified]

## Affected Components
[Components list]"
)
```

**Scout - OpenCode Grok Code (scale >= 1):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase scout using OpenCode Grok Code.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

opencode run -m opencode/grok-code \"Scout codebase for issue: {ISSUE_DESCRIPTION}. Identify key files, code patterns, and technical considerations. Return file paths with observations.\"

After the command completes, format the results as:
## Files Found
- <file_path> (offset: N, limit: M) - Relevance: HIGH/MEDIUM/LOW - Why: [reason]

## Code Patterns
[Patterns found]

## Technical Considerations
[Considerations]"
)
```

**Note**: Launch all 3 OpenCode scouts in PARALLEL for scales 1-3. These are BLOCKING agents - wait for results.

---

### Web Search Agents (scale >= 4)

These agents search for external documentation, best practices, and similar implementations.

**Web Search - Gemini (scale >= 4):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a web search agent using Gemini.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-flash-preview -o text \"Search the web for documentation, tutorials, best practices, and similar implementations related to: {ISSUE_DESCRIPTION}. Find official docs, Stack Overflow solutions, and GitHub examples.\"

After the command completes, format the results as:
## Documentation Resources
- **URL** - Description

## Best Practices
[Key recommendations]

## Similar Implementations
[Examples found]

## Stack Overflow Solutions
[Relevant Q&A]"
)
```

**Web Search - GLM 4.7 (scale >= 4):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a web search agent using OpenCode GLM 4.7.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

opencode run -m opencode/glm-4.7-free \"Search for external resources, documentation, and community solutions related to: {ISSUE_DESCRIPTION}. Focus on finding tutorials, GitHub repos with similar features, and technical blog posts.\"

After the command completes, format the results as:
## External Resources
- **Resource** - Description

## Community Solutions
[Solutions found]

## Technical References
[Blog posts, tutorials]

## Related GitHub Repos
[Similar implementations]"
)
```

**Note**: Launch both Web Search agents in PARALLEL for scales 4-5. These are BLOCKING agents - wait for results.

---

### Step 4: Multi-Agent Analysis and Planning

After scout agents return, spawn planning agents to analyze findings:

**CRITICAL**: Launch planning agents in PARALLEL using a SINGLE message.

**Planning Agent 1 - Codex (Scope Analysis):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a scope analysis agent using Codex.

Context from codebase investigation:
{SCOUT_RESULTS_SUMMARY}

IMMEDIATELY use the Bash tool to run:

codex exec -m 5.2-codex -c model_reasoning_effort=\"high\" -c thinking=\"enabled\" --skip-git-repo-check \"Analyze scope and complexity for: {ISSUE_DESCRIPTION}.

Based on these files: {FILE_LIST}

Provide:
1. Scope assessment (small/medium/large)
2. Complexity estimate (low/medium/high)
3. Affected subsystems
4. Risk assessment
5. Suggested labels (bug, feature, enhancement, breaking-change, etc.)
6. Priority recommendation (critical, high, medium, low)\"

Return a structured scope analysis."
)
```

**Planning Agent 2 - Gemini (Implementation Approach):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are an implementation planning agent using Gemini.

Context from codebase investigation:
{SCOUT_RESULTS_SUMMARY}

IMMEDIATELY use the Bash tool to run:

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-pro-preview -o text \"You are an expert software architect. Analyze implementation approach for: {ISSUE_DESCRIPTION}. Files identified: {FILE_LIST}. Provide: 1. Recommended implementation approach 2. Key considerations and gotchas 3. Testing requirements 4. Documentation needs 5. Acceptance criteria suggestions 6. Potential blockers\"

Return the implementation analysis."
)
```

**Planning Agent 3 - Opus (Deep Analysis):**
```
Task(
  subagent_type="Plan",
  model="opus",
  prompt="You are a deep analysis specialist. Analyze this issue/feature request with thorough reasoning:

Issue: {ISSUE_DESCRIPTION}

Files identified by investigation:
{FILE_LIST_WITH_RELEVANCE}

Provide deep analysis:
1. Root cause analysis (for bugs) or feature rationale (for features)
2. Impact assessment on existing functionality
3. Edge cases and potential regressions
4. Security considerations
5. Performance implications
6. User experience impact
7. Detailed acceptance criteria

Think deeply about trade-offs and provide a comprehensive analysis."
)
```

---

### Step 5: Synthesize Findings into Issue Structure

Combine investigation results into a structured GitHub issue:

**Issue Title Generation:**
- Bug: "fix: [concise description of the problem]"
- Feature: "feat: [concise description of the feature]"
- Enhancement: "improve: [concise description of the enhancement]"

---

**Scale 0 Issue Body Template (Simplified):**
```markdown
## Description

[Clear description of the issue/feature]

## Relevant Files

| File | Lines | Notes |
|------|-------|-------|
| `path/to/file.ts` | 10-50 | [why relevant] |

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]

---
*Issue created with Claude Code (direct investigation)*
```

---

**Scale 1-6 Issue Body Template (Full):**
```markdown
## Description

[Clear description of the issue/feature synthesized from investigation]

## Context

**Type**: {bug|feature|enhancement}
**Scope**: {small|medium|large}
**Complexity**: {low|medium|high}
**Priority**: {critical|high|medium|low}

## Relevant Files

Files identified by multi-agent investigation (ranked by relevance):

| File | Lines | Relevance | Notes |
|------|-------|-----------|-------|
| `path/to/file1.ts` | 1-50 | HIGH | [why relevant] |
| `path/to/file2.tsx` | 10-100 | MEDIUM | [why relevant] |

## Analysis

### Root Cause / Rationale
[From deep analysis agent]

### Impact Assessment
[From planning agents]

### Technical Approach
[Recommended implementation approach]

## Acceptance Criteria

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Testing Requirements

- [ ] Unit tests for [component]
- [ ] Integration tests for [flow]
- [ ] Edge cases: [list]

## Additional Considerations

### Security
[Security considerations if any]

### Performance
[Performance implications if any]

### Documentation
[Documentation updates needed]

---

**Investigation Summary**:
- Agents used: {count}
- Files identified: {count}
- Confidence: {HIGH|MEDIUM|LOW}

*Issue created with multi-agent investigation using Claude Code*
```

---

### Step 6: Create GitHub Issue

```bash
# Create the issue with labels
gh issue create \
  --title "{ISSUE_TITLE}" \
  --body "$(cat <<'EOF'
{ISSUE_BODY}
EOF
)" \
  --label "{LABELS}"

# Capture and report issue URL
```

**Label Suggestions:**
- Bug: `bug`, `needs-triage`
- Feature: `enhancement`, `feature-request`
- Enhancement: `enhancement`, `improvement`
- Additional: `good-first-issue`, `help-wanted`, `breaking-change`, `documentation`

---

## Report Format

```markdown
# GitHub Issue Created: {ISSUE_TITLE}

## Issue Details
**URL**: {ISSUE_URL}
**Number**: #{ISSUE_NUMBER}
**Type**: {bug|feature|enhancement}
**Labels**: {LABELS}

## Investigation Summary
- **Agents Spawned**: {count}
- **Files Analyzed**: {unique_file_count}
- **Confidence Level**: {HIGH|MEDIUM|LOW}

### Agent Results
| Agent | Files Found | Key Insight |
|-------|-------------|-------------|
| Gemini Flash | {count} | {insight} |
| Gemini Lite | {count} | {insight} |
| Codex | {count} | {insight} |
| OpenCode BigPickle | {count} | {insight} |
| OpenCode GLM 4.7 | {count} | {insight} |
| OpenCode Grok Code | {count} | {insight} |
| Claude Haiku | {count} | {insight} |
| Web Search Gemini | {count} | {insight} |
| Web Search GLM 4.7 | {count} | {insight} |

### Planning Analysis
| Agent | Contribution |
|-------|--------------|
| Codex (Scope) | {scope_assessment} |
| Gemini (Approach) | {implementation_approach} |
| Opus (Deep) | {deep_analysis_summary} |

## Files Linked in Issue
{FILE_TABLE}

## Acceptance Criteria Generated
{CRITERIA_LIST}

## Next Steps
1. Review issue: {ISSUE_URL}
2. Add to project board if applicable
3. Assign to team member
4. Begin implementation when ready: `/resolvegitissue {ISSUE_NUMBER}`

---
✅ Issue #{ISSUE_NUMBER} created successfully
🔗 URL: {ISSUE_URL}
🤖 Investigation: {AGENT_COUNT} agents, {FILE_COUNT} files analyzed
```

---

## Critical Reminders

**Scale 0 (Direct Investigation):**
- ✅ DO use Glob, Grep, and Read directly
- ✅ DO keep investigation focused (3-5 files max)
- ✅ DO proceed directly to synthesis after investigation
- ❌ DO NOT spawn any Task agents or subagents
- ❌ DO NOT use Bash commands for investigation

**Scale 1-6 (Multi-Agent Investigation):**
- ✅ DO spawn Task agents with `subagent_type="general-purpose"` for external agents
- ✅ DO include the LITERAL Bash command in each agent prompt
- ✅ DO launch all agents in PARALLEL (single message, multiple Task calls)
- ✅ DO wait for all agents before synthesizing
- ✅ DO use 10-minute timeout per agent (600000ms)
- ❌ DO NOT use native subagent types for main investigation agents
- ❌ DO NOT search codebase yourself during investigation
- ❌ DO NOT skip multi-agent investigation
- ❌ DO NOT create issue without proper investigation

**Issue Creation:**
- ✅ DO generate clear, actionable issue title
- ✅ DO include file references with line numbers
- ✅ DO provide acceptance criteria
- ✅ DO suggest appropriate labels
- ✅ DO include investigation confidence level
- ❌ DO NOT create vague or incomplete issues
- ❌ DO NOT skip acceptance criteria
- ❌ DO NOT forget to include relevant files

---

## Usage Examples

```bash
# Scale 0 - Direct investigation (no subagents, fastest)
/create-issue "Typo in error message on login page" --scale=0
/create-issue "Update copyright year in footer" --scale=0

# Scale 1 - Quick single-agent investigation
/create-issue "Button alignment off on mobile" --scale=1

# Basic usage (default scale 3)
/create-issue "Login button not working on mobile Safari"

# With explicit type
/create-issue "Add dark mode toggle to settings" --type=feature

# High-scale investigation for complex issues
/create-issue "Performance degradation in dashboard loading" --scale=5

# Full investigation with documentation
/create-issue "Implement OAuth2 authentication" --scale=6 --type=feature
```

---

## Why Multi-Agent Investigation for Issue Creation

1. **Comprehensive File Discovery**: Multiple models find different relevant files
2. **Diverse Perspectives**: Different AI providers identify different aspects
3. **Better Scope Assessment**: Multiple analyses lead to more accurate scope/complexity
4. **Quality Acceptance Criteria**: Deep analysis generates actionable criteria
5. **Reduced Ambiguity**: Well-investigated issues are clearer for implementers
6. **Faster Resolution**: Issues with linked files and analysis are easier to resolve
7. **Context Preservation**: Main agent context preserved for synthesis

---

## Integration with Other Commands

After creating an issue, you can:

1. **Resolve the issue**: `/resolvegitissue {ISSUE_NUMBER}`
2. **Plan the implementation**: `/plan "{issue description}"`
3. **Scout for more context**: `/scout "{issue keywords}" 5`

Or use the full workflow:
```bash
/create-issue "Add payment processing" --type=feature
# Issue #42 created
/resolvegitissue 42 --scale=4
# Automatically resolves the issue
```
