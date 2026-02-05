---
description: Search the codebase for files needed to complete the task
argument-hint: [search-query] [scale] [--agent=agent-name]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Write, Edit, Glob]
---

# Purpose

Multi-agent codebase reconnaissance using external agentic coding tools (Gemini, Codex, Claude) to efficiently search and identify files needed to complete a task while preserving the primary agent's context window.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (, ) via Bash for multi-model diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive codebase search.

## Variables

- `{SEARCH_QUERY}`: User's search request or task description
- `{SCALE}`: Number of parallel OpenCode agents to spawn (1-4)
  - 1 agent: OpenCode BigPickle (deep analysis)
  - 2 agents: + OpenCode GLM 4.7 (pattern recognition)
  - 3 agents: + OpenCode Grok Code (quick search)
- `{SUBAGENT}`: Optional specialized subagent to invoke (independent of scale)
  - Can be specified via `--agent=agent-name` flag
  - If not specified, Claude Code will auto-detect appropriate subagents based on search query
  - Available subagents: ai-sdk-planner, fastapi-specialist, pydantic-specialist, railway-specialist, gcp-deployment, supabase-specialist, livekit-planner, mcp-server-specialist, material3-expressive, codebase-researcher, teams-integration-specialist, architecture-discovery, code-reviewer, design-review-agent

## Instructions

1. **Parse user input** to extract:
   - Search query (required)
   - Scale level (default: 2)
   - Subagent flag: `--agent=agent-name` (optional)

2. **Auto-detect subagent** (if not explicitly specified):
   - Analyze search query for keywords matching specialized domains
   - AI SDK / Vercel → ai-sdk-planner
   - FastAPI / Python API → fastapi-specialist
   - Pydantic / validation → pydantic-specialist
   - Railway deployment → railway-specialist
   - GCP / Google Cloud → gcp-deployment
   - Supabase / database → supabase-specialist
   - LiveKit / voice / audio → livekit-planner
   - MCP / Model Context Protocol → mcp-server-specialist
   - Material Design / Material 3 → material3-expressive
   - Codebase analysis / architecture → codebase-researcher or architecture-discovery
   - Teams / Microsoft → teams-integration-specialist
   - Code review → code-reviewer
   - Design review / UI → design-review-agent
   - If multiple matches or ambiguous, select the most relevant or ask user

3. **Check for dependency issues and conditionally invoke dependency-verifier skill**:
   - Only invoke dependency-verifier skill when there are EXPLICIT dependency problems:
     - Build failures mentioning missing packages
     - Import/require errors for packages listed in package.json/requirements.txt
     - Version mismatch errors during installation
     - User explicitly requests dependency verification
   - **DO NOT** automatically verify dependencies for all projects with 10+ packages
   - If dependency issues detected, use Skill tool with skill name "dependency-verifier"
   - Include verification results in final scout report only when verification was performed

4. Create a todo list for tracking:
   - Dependency verification (only if explicit issues detected)
   - Parallel agent bash commands
   - Subagent invocation (if applicable)
   - Documentation saving (if scale >= 5)

5. **IMPORTANT**: DO NOT use any search tools yourself (Glob, Grep, Read, etc.) - Exception: use Read, Write, Edit, Glob ONLY for:
   - Dependency issue detection (step 3) - only when explicit problems exist
   - Documentation file management (when scale >= 5)

6. **IMPORTANT**: Use Task tool to spawn agents that will immediately call Bash tool with the appropriate agentic coding tool commands

7. **IF subagent selected**: Invoke specialized subagent using Task tool AFTER file search completes
   - Pass search query and file list to subagent
   - Subagent provides specialized analysis/planning based on its domain expertise
   - Include subagent output in final report

8. Each agent runs a 10-minute search via Bash, then returns a structured file list

9. Collect results from all agents (skip any that timeout)

10. Synthesize and deduplicate findings into final report

11. **IF scale >= 5**: Save documentation findings to `/aidocs` folder:
    - Check if `/aidocs` folder exists using Glob
    - Create folder if it doesn't exist using Bash (`mkdir aidocs`)
    - **IMPORTANT**: If agents create collaboration files during execution, ensure they are stored in `/aidocs/context` subdirectory, NOT in root
    - Check if `/aidocs/context` folder exists, create if needed using Bash (`mkdir -p aidocs/context`)
    - Generate filename from search query (e.g., `stripe-payment-integration-docs.md`)
    - If file exists, read it and update with new findings using Edit
    - If file doesn't exist, create new file using Write
    - Include search query, date, URLs, and key findings summary

## Workflow

### Step 0: Dependency Verification (Conditional - Only for Explicit Issues)

**Only execute this step if there are EXPLICIT dependency problems:**

1. **Detect dependency issues**:
   - Check if search query or user context mentions:
     - Build failures with package errors
     - Missing package errors (import/require failures)
     - Version mismatch issues
     - User explicitly requesting dependency verification
   - **DO NOT** automatically check dependencies just because they exist

2. **Invoke dependency-verifier skill only when needed**:
   ```
   IF explicit_dependency_issue_detected OR user_requested_verification:
     Use Skill tool to invoke "dependency-verifier"
     Pass list of dependency file paths
     Wait for verification report
     Include verification results in final scout report
   ELSE:
     Skip dependency verification (no issues detected)
   ```

3. **Verification Report Integration** (only if verification was performed):
   - Include summary in final scout report
   - Highlight any invalid/warning packages found
   - Provide actionable recommendations from verifier

### Step 1: Determine Agent Count Based on Scale
```
if scale == 1: spawn 1 agent (OpenCode BigPickle)
if scale == 2: spawn 2 agents (BigPickle + GLM 4.7)
if scale == 3: spawn 3 agents (BigPickle + GLM 4.7 + Grok Code)
if scale >= 3: spawn 3 agents (all 3 OpenCode models) **[DEFAULT]**
```

### Step 2: Spawn Agents in Parallel
**CRITICAL**: Launch all agents in parallel using a SINGLE message with multiple Task tool calls.

### Step 3: Agent Prompts
Each Task tool prompt follows this structure:

**Agent Task Prompt Template (OpenCode Codebase Search):**
```
You are a fast file scout using OpenCode. Your ONLY job is to search the codebase for files needed for this task:

"{SEARCH_QUERY}"

IMMEDIATELY use the Bash tool to run this command with a 3-minute timeout:
OPENCODE_YOLO=true opencode run --format default -m {MODEL} "{SEARCH_PROMPT}"

The command will search the codebase and return relevant files.

Return ONLY a structured list in this exact format:
`- <path to file> (offset: N, limit: M)` where offset is starting line and limit is lines to read

Example output:
- src/auth/login.ts (offset: 1, limit: 50)
- components/UserProfile.tsx (offset: 10, limit: 100)
- utils/validation.js (offset: 1, limit: 200)

Do NOT implement anything. Do NOT read files yourself. ONLY run the bash command and format the results.
```

### Step 4: Agent-Specific Bash Commands (OpenCode Only)

All file scouts use OpenCode models for lightweight, cost-effective codebase search.

**Agent 1 - OpenCode BigPickle (Deep Analysis):**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle "Search codebase for files related to: {SEARCH_QUERY}. Identify relevant files, architecture patterns, and implementation details. Return a list of file paths with line ranges."
```

**Agent 2 - OpenCode GLM 4.7 (Pattern Recognition):**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free "Analyze codebase for: {SEARCH_QUERY}. Focus on code organization, patterns, and file relevance. Return file paths with line ranges."
```

**Agent 3 - OpenCode Grok Code (Quick Search):**
```bash
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "Scout codebase for: {SEARCH_QUERY}. Quickly identify key files, entry points, and test files. Return file paths with line ranges."
```


**Spawning Agents via Task Tool:**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a fast file scout using OpenCode.

IMMEDIATELY use the Bash tool to run this command (3-minute timeout):

OPENCODE_YOLO=true opencode run --format default -m {MODEL} \"{SEARCH_PROMPT}\"

Return ONLY a structured list in this exact format:
- <path to file> (offset: N, limit: M)

Do NOT implement anything. ONLY run the command and format the results."
)
```

### Step 5: Timeout Handling
- Each agent has 10 minutes (600000ms timeout on Bash calls)
- If an agent times out, skip it and continue with successful agents
- Do NOT restart failed agents

### Step 6: Result Synthesis
- Collect all agent responses
- Deduplicate file paths
- Merge overlapping line ranges
- Rank by frequency across agents (files found by multiple agents = higher priority)

### Step 6a: Subagent Invocation (if applicable)

**Execute this step if:**
- User specified `--agent=agent-name` flag, OR
- Auto-detection identified a relevant specialized subagent

**Subagent Task Prompt Template:**
```
You are the {SUBAGENT_NAME} specialist. A codebase scout has identified files related to this task:

"{SEARCH_QUERY}"

**Files Found:**
{FILE_LIST_WITH_PATHS_AND_LINE_RANGES}

**Documentation Resources (if available):**
{DOCUMENTATION_URLS_AND_SUMMARIES}

Your task:
1. Analyze the search query and identified files from your specialized domain perspective
2. Provide expert recommendations for:
   - Architecture patterns to follow
   - Best practices specific to your domain
   - Potential pitfalls to avoid
   - Implementation strategy
   - Additional files or resources that might be needed
3. Suggest next steps for the developer

Return a concise analysis in this format:

## Domain Analysis: {SUBAGENT_DOMAIN}

### Recommended Approach
[Your expert recommendation for how to approach this task]

### Key Considerations
- [Important consideration 1]
- [Important consideration 2]
- [Important consideration 3]

### Implementation Strategy
[Step-by-step strategy from your domain expertise]

### Additional Resources Needed
- [Resource/file 1]
- [Resource/file 2]

### Next Steps
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]
```

**Subagent Selection Logic:**
```
If user specified --agent flag:
  Use specified subagent
Else if search query contains keywords:
  "ai sdk" OR "vercel" OR "tool calling" OR "streaming" → ai-sdk-planner
  "fastapi" OR "python api" OR "uvicorn" → fastapi-specialist
  "pydantic" OR "validation" OR "schema" → pydantic-specialist
  "railway" OR "railway deploy" → railway-specialist
  "gcp" OR "google cloud" OR "cloud run" → gcp-deployment
  "supabase" OR "postgres" OR "database" → supabase-specialist
  "livekit" OR "voice" OR "audio" OR "webrtc" → livekit-planner
  "mcp" OR "model context protocol" → mcp-server-specialist
  "material 3" OR "material design" OR "m3" → material3-expressive
  "codebase" OR "architecture" OR "patterns" → codebase-researcher
  "teams" OR "microsoft teams" → teams-integration-specialist
  "review code" → code-reviewer
  "design review" OR "ui review" → design-review-agent
Else:
  No subagent (optional enhancement, not required)
```

### Step 7: Store Scout Results (Optional)

**For complex searches**, optionally save results to `.ai-docs/scout-results/`:

1. **Create directory if needed**:
   ```bash
   mkdir -p .ai-docs/scout-results
   ```

2. **Save results** with timestamp:
   ```markdown
   # Scout Results: {SEARCH_QUERY}
   Date: {CURRENT_DATE}

   ## Files Found
   {DEDUPLICATED_FILE_LIST}

   ## Agent Consensus
   - BigPickle: {findings}
   - GLM 4.7: {findings}
   - Grok Code: {findings}
   ```

## Report Format

Generate a structured report:

```markdown
# Scout Results: {SEARCH_QUERY}
**Agents Used**: {AGENT_COUNT} | **Files Found**: {UNIQUE_FILE_COUNT} | **Specialist**: {SUBAGENT_NAME or "None"}

## 📦 Dependency Verification (only if explicit issues detected)

**Status**: {Verified / Skipped (no issues) / Failed}
**Trigger**: {Build failure / Missing packages / Version mismatch / User requested / Not applicable}
**Total Dependencies**: {COUNT} (if verified)
**Verification Method**: dependency-verifier skill (Haiku 4.5)

### Summary (if verification ran)
- ✅ Valid: {count} packages
- ⚠️  Warnings: {count} packages
- ❌ Invalid: {count} packages

### ❌ Invalid Packages (Blockers)
{LIST_OF_INVALID_PACKAGES_WITH_REASONS}

### ⚠️  Package Warnings
{LIST_OF_WARNING_PACKAGES}

### 🔧 Recommended Actions
{ACTIONABLE_RECOMMENDATIONS_FROM_VERIFIER}

---

## Priority Files
(Ranked by agent consensus)

- **<file_path>** (offset: N, limit: M) - Found by X agents
  Brief relevance description

## All Discovered Files
- <file_path> (offset: N, limit: M)
- <file_path> (offset: N, limit: M)
...

## Documentation Resources (if scale >= 5)
- **<documentation_url>** - Brief description
  Found by: [Gemini Flash Light / 5.2-codex]
- **<documentation_url>** - Brief description
...

### Key Findings Summary (from Documentation Agents)
{COMBINED_KEY_FINDINGS_FROM_AGENTS}

📁 **Full documentation saved to**: `aidocs/{filename}`

---

## Specialist Analysis (if subagent invoked)

**Specialist**: {SUBAGENT_NAME}

{SUBAGENT_ANALYSIS_OUTPUT}

---

## Agent Performance
**OpenCode Codebase Search:**
- ✓ BigPickle: {file_count} files (deep analysis)
- ✓ GLM 4.7: {file_count} files (pattern recognition)
- ✓ Grok Code: {file_count} files (quick search)

**Consensus:** {4/4 | 3/4 | 2-2 TIE → Claude tie-breaker}

**Specialized Analysis:**
- {SUBAGENT_NAME}: Expert recommendations provided
```

## Critical Reminders

- ✅ DO use ONLY OpenCode agents (BigPickle, GLM 4.7, Grok Code) for file scouts
- ✅ Default scale is 3 agents (BigPickle + GLM 4.7 + Grok Code)
- ✅ DO invoke dependency-verifier skill ONLY when explicit dependency issues are detected
- ✅ DO use Task tool to spawn agents
- ✅ DO have each agent immediately run Bash with `opencode run` commands
- ✅ DO launch agents in PARALLEL (single message, multiple Task calls)
- ✅ DO use 3-minute timeout per agent (lightweight scouts)
- ✅ DO auto-detect or use specified subagent when relevant
- ✅ DO invoke subagent AFTER file search completes (not in parallel with search agents)
- ✅ DO pass file list to subagent for specialized analysis
- ✅ DO include subagent analysis in final report when applicable
- ❌ DO NOT use Gemini, Codex, or Claude Haiku for file scouts (use OpenCode only)
- ❌ DO NOT automatically verify dependencies just because 10+ packages exist
- ❌ DO NOT search the codebase yourself
- ❌ DO NOT use Glob, Grep, Read tools for codebase search
- ❌ DO NOT implement the task - ONLY search for files
- ❌ DO NOT restart timed-out agents
- ❌ DO NOT invoke subagent if no relevant specialist matches the search query

## Usage Examples

```bash
# Basic search with OpenCode agents (scale 1-3)
# NOTE: Dependency verification only runs when explicit issues are detected
/scout "authentication logic" 1      # BigPickle only
/scout "database migration files" 2  # BigPickle + GLM 4.7
/scout "React rendering performance" 3  # All 3 OpenCode agents (DEFAULT)

# Example with dependency verification (only when needed)
/scout "fix build failure - missing @ai-sdk/react package" 2
# → Detects explicit dependency issue in search query (build failure + missing package)
# → Invokes dependency-verifier skill to check all npm packages
# → Then executes regular scout search with 2 OpenCode agents

# With explicit subagent invocation
/scout "AI SDK streaming implementation" 3 --agent=ai-sdk-planner
/scout "Railway deployment configuration" 2 --agent=railway-specialist
/scout "Supabase RLS policies" 3 --agent=supabase-specialist

# Auto-detect subagent (intelligent matching)
/scout "FastAPI async endpoints with Pydantic validation" 3
# → 3 OpenCode agents + automatically invokes fastapi-specialist + pydantic-specialist

/scout "LiveKit voice agent integration" 3
# → 3 OpenCode agents + automatically invokes livekit-planner

/scout "Material 3 design system components" 2
# → 2 OpenCode agents + automatically invokes material3-expressive

# Complex search with auto-detect subagent
/scout "MCP server implementation with tool calling" 3
# → 3 OpenCode agents + auto-invokes mcp-server-specialist + ai-sdk-planner
```

**Notes**:
- Scale is **independent** of subagent invocation (scale 1-3 controls OpenCode agent count)
- Subagents are invoked AFTER file search completes for specialized domain analysis
- Auto-detection analyzes search query keywords to match specialized domains
- Use `--agent=name` to explicitly specify a subagent