---
description: Assess codebase with multi-agent analysis to generate code quality rules
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Edit, Write, Glob, Grep]
---

# Purpose

Systematically assess the codebase by spawning multiple analysis agents (using different models) to identify code patterns, anti-patterns, and quality opportunities. Synthesize findings into actionable code quality rules and regulations.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (`gemini`, `codex`) via Bash for multi-model analysis diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive codebase assessment.

## Anti-Bypass Notice

This workflow REQUIRES spawning subagents via the Task tool. You are NOT permitted to:
- Use Grep/Glob/Read to assess the codebase yourself
- Skip the multi-agent assessment step for "efficiency"
- Assume you already know the code quality issues
- Replace subagent assessment with direct codebase searches

**WHY**: The multi-agent approach provides diverse model perspectives on code quality. Your role is to ORCHESTRATE the agents, not replace them.

## Core Assessment Dimensions

Inspired by code-simplifier principles, agents will assess:

1. **Clarity & Readability**
   - Unnecessary complexity and nesting
   - Redundant code and abstractions
   - Variable and function naming quality
   - Comment quality (too many, too few, obvious ones)

2. **Consistency & Standards**
   - Import organization patterns
   - Function declaration styles
   - Error handling patterns
   - Naming conventions across codebase

3. **Maintainability**
   - Code duplication opportunities
   - Abstraction levels (over/under-abstracted)
   - Module organization
   - Test coverage patterns

4. **Anti-Patterns**
   - Nested ternary operators
   - Dense one-liners prioritizing brevity over clarity
   - Overly clever solutions
   - Mixed concerns in single functions

## Workflow

**CRITICAL WORKFLOW REQUIREMENTS**:
1. Run the workflow in order, top to bottom
2. Do not stop in between steps
3. Complete every step before stopping
4. **Step 2 (Subagent Assessment) is MANDATORY** - you MUST spawn Task agents

**VALIDATION CHECKPOINT**: Before proceeding to Step 3, confirm you have spawned 6 Task agents. If you have not used the Task tool to spawn assessment agents, STOP and go back to Step 2.

### Step 1: Identify Codebase Scope

```bash
# Get codebase structure for agents to analyze
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" -o -name "*.go" -o -name "*.rs" -o -name "*.rb" \) | head -50

# Get recent activity focus areas
git log --oneline -20 --name-only | grep -E "\.(ts|tsx|js|jsx|py|go|rs|rb)$" | sort | uniq -c | sort -rn | head -20
```

Store the primary language and key directories for agent prompts.

### Step 2: Spawn Assessment Agents in Parallel

**MANDATORY - NO EXCEPTIONS**

You MUST spawn 6 assessment subagents. DO NOT:
- Skip this step
- Perform assessment yourself instead of spawning agents
- Decide that agents are unnecessary
- Search the codebase directly without agents

REQUIRED ACTIONS:
1. Spawn exactly 6 agents (one per model) with assessment prompts
2. Launch ALL agents in parallel using a SINGLE message with multiple Task tool calls
3. WAIT for all agent results before proceeding to Step 3

**Agent 1 - Gemini Flash (Pattern Detective):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a code quality pattern detective using Gemini Flash.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-flash-preview -o text \"Assess this codebase for CODE PATTERNS. Focus on:
1. Naming conventions (variables, functions, files, classes)
2. Import/export organization patterns
3. Function declaration styles (arrow vs function keyword)
4. Type annotation patterns
5. Module organization patterns

For each pattern found, provide:
- Pattern name
- Example file paths where it appears
- Consistency score (1-10)
- Suggested rule to enforce it

Format as structured list.\"

Report back the complete Gemini output."
)
```

**Agent 2 - Codex GPT-5.2 (Anti-Pattern Hunter):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are an anti-pattern hunter using OpenAI Codex.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

codex exec -m gpt-5.2 -s read-only -c model_reasoning_effort=\"medium\" --skip-git-repo-check \"Assess this codebase for ANTI-PATTERNS and code smells. Focus on:
1. Nested ternary operators
2. Overly complex conditionals (deep nesting)
3. Dense one-liners sacrificing readability
4. Mixed concerns in single functions
5. Redundant abstractions or over-engineering
6. Inconsistent error handling
7. Code duplication opportunities
8. Missing or excessive comments

For each anti-pattern found, provide:
- Anti-pattern name
- Example file paths where it appears
- Severity (low/medium/high)
- Suggested rule to prevent it

Format as structured list.\"

Report back the complete Codex output."
)
```

**Agent 3 - Claude Haiku (Standards Synthesizer):**
```
Task(
  subagent_type="Explore",
  model="haiku",
  prompt="You are a code standards synthesizer. Thoroughly explore this codebase to assess CODE QUALITY OPPORTUNITIES. Focus on:

1. Clarity improvements - where could code be clearer?
2. Consistency gaps - where do patterns break?
3. Maintainability risks - what would be hard to change?
4. Testing patterns - how is testing organized?
5. Documentation quality - where is it helpful vs missing?

For each opportunity found, provide:
- Category (clarity/consistency/maintainability/testing/docs)
- Description of the opportunity
- Example file paths
- Impact (low/medium/high)
- Suggested rule or guideline

Format as structured list."
)
```

**Agent 4 - OpenCode BigPickle (Architecture Reviewer):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are an architecture reviewer using OpenCode BigPickle.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle \"Assess this codebase for ARCHITECTURAL PATTERNS and structural quality. Focus on:
1. Module boundaries and separation of concerns
2. Dependency direction (are dependencies flowing correctly?)
3. Layering patterns (presentation, business, data)
4. Circular dependency risks
5. API contract consistency
6. Configuration management patterns

For each finding, provide:
- Pattern/Issue name
- Example file paths
- Severity (low/medium/high)
- Suggested architectural rule

Format as structured list.\"

Report back the complete BigPickle output."
)
```

**Agent 5 - OpenCode Grok Code (Coherence Analyst):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a coherence analyst using OpenCode Grok Code.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code \"Assess this codebase for CROSS-CUTTING COHERENCE. Focus on:
1. Frontend/backend contract alignment (API shapes match usage)
2. Type consistency across boundaries
3. Error handling propagation patterns
4. State management coherence
5. Data flow consistency (transformations between layers)

For each finding, provide:
- Coherence issue name
- Files involved (both sides of boundary)
- Impact (low/medium/high)
- Suggested rule to maintain coherence

Format as structured list.\"

Report back the complete Grok output."
)
```

**Agent 6 - OpenCode Grok Code (Technical Debt Scanner):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a technical debt scanner using OpenCode Grok Code.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code \"Assess this codebase for TECHNICAL DEBT and maintenance risks. Focus on:
1. TODO/FIXME/HACK comments and their age
2. Deprecated API usage
3. Dead code and unused exports
4. Test coverage gaps
5. Security anti-patterns (hardcoded secrets, injection risks)
6. Performance anti-patterns (N+1 queries, unbounded loops)

For each finding, provide:
- Debt item name
- Example file paths
- Priority (low/medium/high/critical)
- Suggested remediation rule

Format as structured list.\"

Report back the complete Grok output."
)
```

### Step 3: Synthesize Agent Findings

Review results from all 6 agents and synthesize into categories:

**Synthesis Framework:**
```
For each finding across all agents:

1. PATTERNS (from Gemini Flash):
   - Extract consistent patterns worth codifying
   - Note consistency scores

2. ANTI-PATTERNS (from Codex GPT-5.2):
   - Extract anti-patterns to prohibit
   - Note severity levels

3. OPPORTUNITIES (from Claude Haiku):
   - Extract improvement opportunities
   - Note impact levels

4. ARCHITECTURE (from BigPickle):
   - Extract architectural patterns and issues
   - Note structural concerns

5. COHERENCE (from Grok Code):
   - Extract cross-boundary consistency issues
   - Note integration concerns

6. TECHNICAL DEBT (from Grok Code):
   - Extract debt items and maintenance risks
   - Note priority levels

Cross-reference findings:
- Where do multiple agents agree? (high confidence - 4+ agents)
- Where do 2-3 agents agree? (medium confidence)
- Where do agents conflict? (needs investigation)
- What unique insights does each provide?
```

### Step 4: Generate Code Quality Rules

Create a structured rules document based on synthesized findings:

```markdown
# Code Quality Rules

## High Confidence Rules (Multiple Agents Agreed)
[Rules where 2+ agents identified the same pattern/anti-pattern]

## Patterns to Enforce
[Codified patterns from the codebase]
- Rule name
- Why: Reasoning
- Example: Good vs Bad
- Enforcement: How to check

## Anti-Patterns to Prevent
[Anti-patterns identified with severity]
- Anti-pattern name
- Why it's problematic
- Example of the issue
- Alternative approach

## Suggested Guidelines
[Lower confidence recommendations]
- Guideline
- Context where it applies
- Flexibility notes

## Investigation Needed
[Conflicting agent findings requiring human decision]
```

### Step 5: Output Recommendations

Present findings in actionable format:

```markdown
# Codebase Assessment Complete

## Assessment Summary
- Agents spawned: 6 (Gemini, Codex, Haiku, BigPickle, Grok x2)
- Patterns identified: {count}
- Anti-patterns found: {count}
- Opportunities noted: {count}
- Architecture issues: {count}
- Coherence gaps: {count}
- Technical debt items: {count}

## Proposed Rules for CLAUDE.md

### Must-Have Rules (High Confidence)
{rules from high-confidence findings}

### Should-Have Guidelines (Medium Confidence)
{guidelines from single-agent findings}

### Discuss with Team
{conflicting findings needing human input}

## Next Steps
1. Review proposed rules with team
2. Add approved rules to CLAUDE.md
3. Consider adding linting rules for enforcement
4. Schedule follow-up assessment in [timeframe]
```

## Agent Configuration

**Assessment Agents (6 total):**

| Agent | Model | Focus |
|-------|-------|-------|
| Agent 1 | Gemini Flash | **Pattern Detective** - naming, imports, function styles |
| Agent 2 | Codex GPT-5.2 | **Anti-Pattern Hunter** - code smells, complexity |
| Agent 3 | Claude Haiku | **Standards Synthesizer** - quality opportunities |
| Agent 4 | OpenCode BigPickle | **Architecture Reviewer** - modules, dependencies, layering |
| Agent 5 | OpenCode Grok Code | **Coherence Analyst** - frontend/backend alignment |
| Agent 6 | OpenCode Grok Code | **Technical Debt Scanner** - TODOs, deprecated APIs, security |

Each agent uses a different model perspective to assess different dimensions of code quality.

## Agentic Tool Commands

```bash
# Agent 1 - Gemini Flash (Pattern Detective)
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-flash-preview -o text "Assess codebase for patterns: {focus_area}"

# Agent 2 - Codex GPT-5.2 (Anti-Pattern Hunter)
codex exec -m gpt-5.2 -s read-only -c model_reasoning_effort="medium" --skip-git-repo-check "Assess codebase for anti-patterns: {focus_area}"

# Agent 3 - Claude Haiku (Standards Synthesizer)
Task(
  subagent_type="Explore",
  model="haiku",
  prompt="Assess codebase for quality opportunities: {focus_area}"
)

# Agent 4 - OpenCode BigPickle (Architecture Reviewer)
OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle "Assess codebase for architectural patterns: {focus_area}"

# Agent 5 - OpenCode Grok Code (Coherence Analyst)
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "Assess codebase for cross-boundary coherence: {focus_area}"

# Agent 6 - OpenCode Grok Code (Technical Debt Scanner)
OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code "Assess codebase for technical debt: {focus_area}"
```

## Why Multi-Agent Assessment (6 Agents)

- **Perspective diversity**: 6 different models notice different patterns
- **Specialization**: Each agent has a focused assessment lens
- **Cross-validation**: 4+ models agreeing = high confidence rules
- **Comprehensiveness**: Covers patterns, anti-patterns, opportunities, architecture, coherence, and technical debt
- **Provider diversity**: Anthropic, Google, OpenAI, and OpenCode models provide independent perspectives

## Optional Arguments

```
$ARGUMENTS - Optional focus area or file patterns to assess
```

If provided, scope agents to focus on specific directories or file types.
