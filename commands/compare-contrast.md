---
description: Multi-model perspective comparison using Codex, Gemini, and Claude
argument-hint: [topic] [perspective-a] [perspective-b]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Write, Edit, Glob]
---

# Purpose

Multi-agent debate system that leverages GPT-5.2, Gemini 3 Pro, and Claude Haiku to argue different perspectives on a technical decision. Each model builds evidence-based arguments for both sides, then the main agent synthesizes findings to determine the stronger position.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (`codex`, `gemini`) via Bash for multi-model debate diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive perspective comparison.

## Variables

- `{TOPIC}`: The technical decision or comparison to evaluate
- `{PERSPECTIVE_A}`: First perspective/position to argue
- `{PERSPECTIVE_B}`: Second perspective/position to argue

## Instructions

1. **Parse user input** to extract:
   - Topic (required): The issue or decision to compare
   - Perspective A (required): First position to evaluate
   - Perspective B (required): Second position to evaluate

2. **Create todo list** for tracking:
   - Agent spawning (6 parallel agents)
   - Argument collection from all agents
   - Synthesis and comparison
   - Final recommendation

3. **IMPORTANT**: DO NOT use search tools yourself (Glob, Grep, Read, etc.)
   - Let agents handle all codebase research
   - Exception: Use Write/Edit for saving final analysis

4. **Spawn 6 agents in parallel** using Task tool
   - All agents launch in SINGLE message with multiple Task calls
   - 3 models × 2 perspectives = 6 total agents

5. **Each agent runs for 10 minutes** (600000ms timeout)
   - Agents search codebase for evidence
   - Build structured argument for assigned perspective
   - Return findings to main agent

6. **Collect and synthesize** all arguments
   - Compare arguments across models for each perspective
   - Identify strongest points and weaknesses
   - Create objective comparison matrix

7. **Generate final recommendation**
   - Weigh evidence objectively
   - Determine which perspective has stronger support
   - Provide actionable decision with rationale

## Workflow

### Step 1: Spawn 6 Agents in Parallel

**CRITICAL**: Launch all 6 agents simultaneously using ONE message with 6 Task tool calls.

### Step 2: Agent Prompts

Each agent receives a specialized prompt based on their model and assigned perspective.

**Agent Task Prompt Template:**
```
You are a technical advocate arguing for a specific perspective. Your task is to build the STRONGEST possible case for your assigned position using evidence from the codebase.

**Topic**: {TOPIC}

**Your Assigned Perspective**: {PERSPECTIVE_A or PERSPECTIVE_B}

**Your Role**: Build an evidence-based argument supporting your perspective

IMMEDIATELY use the Bash tool to run this command with a 10-minute timeout:
{AGENTIC_TOOL_COMMAND}

The command will search the codebase and help you build your argument.

Return your argument in this EXACT format:

## Perspective: {PERSPECTIVE_NAME}
**Advocate**: {MODEL_NAME}

### Core Argument
[2-3 sentence summary of your position]

### Evidence from Codebase
1. **Evidence Point 1**
   - File: `path/to/file.ext:line_number`
   - Explanation: [Why this supports your perspective]

2. **Evidence Point 2**
   - File: `path/to/file.ext:line_number`
   - Explanation: [Why this supports your perspective]

3. **Evidence Point 3**
   - File: `path/to/file.ext:line_number`
   - Explanation: [Why this supports your perspective]

### Technical Benefits
- [Benefit 1 with technical reasoning]
- [Benefit 2 with technical reasoning]
- [Benefit 3 with technical reasoning]

### Addresses Common Concerns
- **Concern**: [Potential objection to your perspective]
  **Counter-argument**: [How your perspective addresses this]

### Recommended Implementation Path
[If this perspective is chosen, how should it be implemented?]

Do NOT be neutral. Argue STRONGLY for your assigned perspective using codebase evidence.
```

### Step 3: Agent-Specific Bash Commands

**Agent 1 - GPT-5.2 for Perspective A:**
```bash
codex exec -m gpt-5.2 -s read-only -c model_reasoning_effort="low" --skip-git-repo-check "You are arguing that {PERSPECTIVE_A} for the topic: {TOPIC}. Search the codebase for evidence supporting this perspective. Return specific file paths and code examples that support this position. Build the strongest possible case."
```

**Agent 2 - GPT-5.2 for Perspective B:**
```bash
codex exec -m gpt-5.2 -s read-only -c model_reasoning_effort="low" --skip-git-repo-check "You are arguing that {PERSPECTIVE_B} for the topic: {TOPIC}. Search the codebase for evidence supporting this perspective. Return specific file paths and code examples that support this position. Build the strongest possible case."
```

**Agent 3 - Gemini 3 Pro for Perspective A:**
(Gemini CLI: using latest installed version)
```bash
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-pro-preview -o text "You are arguing that {PERSPECTIVE_A} for the topic: {TOPIC}. Search the codebase thoroughly for evidence supporting this perspective. Provide file paths, line numbers, and explanations for why this evidence supports your position. Build a compelling case."
```

**Agent 4 - Gemini 3 Pro for Perspective B:**
```bash
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-pro-preview -o text "You are arguing that {PERSPECTIVE_B} for the topic: {TOPIC}. Search the codebase thoroughly for evidence supporting this perspective. Provide file paths, line numbers, and explanations for why this evidence supports your position. Build a compelling case."
```

**Agent 5 - Claude Haiku for Perspective A:**
```bash
claude --model haiku -p "You are arguing that {PERSPECTIVE_A} for the topic: {TOPIC}. Quickly search the codebase for evidence supporting this perspective. Return file paths with line numbers and clear explanations of how they support your argument."
```

**Agent 6 - Claude Haiku for Perspective B:**
```bash
claude --model haiku -p "You are arguing that {PERSPECTIVE_B} for the topic: {TOPIC}. Quickly search the codebase for evidence supporting this perspective. Return file paths with line numbers and clear explanations of how they support your argument."
```

### Step 4: Timeout Handling
- Each agent has 10 minutes (600000ms timeout)
- If an agent times out, skip it and continue with successful agents
- DO NOT restart failed agents
- Minimum 4 agents required for valid comparison (2 per perspective)

### Step 5: Argument Synthesis

After collecting all agent responses, synthesize into comparison report:

1. **Group arguments by perspective**
   - Perspective A: Codex + Gemini + Haiku arguments
   - Perspective B: Codex + Gemini + Haiku arguments

2. **Identify consensus points**
   - What do multiple models agree on for each perspective?
   - Which evidence appears across multiple agents?

3. **Evaluate argument strength**
   - Quality of codebase evidence
   - Technical soundness of reasoning
   - Implementation feasibility
   - Risk assessment

4. **Create comparison matrix**
   - Side-by-side comparison of key factors
   - Objective scoring based on evidence quality

5. **Determine recommendation**
   - Which perspective has stronger evidence?
   - Are there scenarios where each perspective is better?
   - What's the recommended path forward?

## Report Format

Generate a comprehensive comparison report:

```markdown
# Compare & Contrast: {TOPIC}
**Models Used**: GPT-5.2, Gemini 3 Pro, Claude Haiku | **Perspectives**: 2 | **Total Arguments**: {COUNT}

---

## Perspectives Being Evaluated

**Perspective A**: {PERSPECTIVE_A}
**Perspective B**: {PERSPECTIVE_B}

---

## Arguments for Perspective A

### GPT-5.2 Argument
{CODEX_PERSPECTIVE_A_ARGUMENT}

### Gemini 3 Pro Argument
{GEMINI_PERSPECTIVE_A_ARGUMENT}

### Claude Haiku Argument
{HAIKU_PERSPECTIVE_A_ARGUMENT}

---

## Arguments for Perspective B

### GPT-5.2 Argument
{CODEX_PERSPECTIVE_B_ARGUMENT}

### Gemini 3 Pro Argument
{GEMINI_PERSPECTIVE_B_ARGUMENT}

### Claude Haiku Argument
{HAIKU_PERSPECTIVE_B_ARGUMENT}

---

## Synthesis & Comparison

### Consensus Points

**Perspective A - Agreement Across Models:**
- {CONSENSUS_POINT_1}
- {CONSENSUS_POINT_2}
- {CONSENSUS_POINT_3}

**Perspective B - Agreement Across Models:**
- {CONSENSUS_POINT_1}
- {CONSENSUS_POINT_2}
- {CONSENSUS_POINT_3}

### Comparison Matrix

| Factor | Perspective A | Perspective B | Winner |
|--------|---------------|---------------|--------|
| **Codebase Alignment** | {SCORE_A} | {SCORE_B} | {A/B/TIE} |
| **Implementation Complexity** | {SCORE_A} | {SCORE_B} | {A/B/TIE} |
| **Long-term Maintainability** | {SCORE_A} | {SCORE_B} | {A/B/TIE} |
| **Performance Impact** | {SCORE_A} | {SCORE_B} | {A/B/TIE} |
| **Team Expertise Required** | {SCORE_A} | {SCORE_B} | {A/B/TIE} |
| **Risk Level** | {SCORE_A} | {SCORE_B} | {A/B/TIE} |

### Strongest Arguments

**Perspective A Strongest Points:**
1. {STRONG_POINT_1_WITH_MODEL_AGREEMENT}
2. {STRONG_POINT_2_WITH_MODEL_AGREEMENT}
3. {STRONG_POINT_3_WITH_MODEL_AGREEMENT}

**Perspective B Strongest Points:**
1. {STRONG_POINT_1_WITH_MODEL_AGREEMENT}
2. {STRONG_POINT_2_WITH_MODEL_AGREEMENT}
3. {STRONG_POINT_3_WITH_MODEL_AGREEMENT}

### Identified Weaknesses

**Perspective A Weaknesses:**
- {WEAKNESS_1_IDENTIFIED_BY_AGENTS}
- {WEAKNESS_2_IDENTIFIED_BY_AGENTS}

**Perspective B Weaknesses:**
- {WEAKNESS_1_IDENTIFIED_BY_AGENTS}
- {WEAKNESS_2_IDENTIFIED_BY_AGENTS}

---

## Final Recommendation

**Recommended Perspective**: {PERSPECTIVE_A or PERSPECTIVE_B or HYBRID}

**Rationale**:
{DETAILED_EXPLANATION_OF_WHY_THIS_PERSPECTIVE_IS_STRONGER}

**Evidence Summary**:
- {KEY_EVIDENCE_1}
- {KEY_EVIDENCE_2}
- {KEY_EVIDENCE_3}

**Implementation Guidance**:
{STEP_BY_STEP_RECOMMENDED_APPROACH}

**Risk Mitigation**:
{ADDRESSING_CONCERNS_FROM_OTHER_PERSPECTIVE}

**Alternative Scenarios**:
- **If {CONDITION}**: Consider {ALTERNATIVE_PERSPECTIVE}
- **If {CONDITION}**: Consider {HYBRID_APPROACH}

---

## Agent Performance

**Perspective A Advocates:**
- ✓ GPT-5.2: {EVIDENCE_COUNT} pieces of evidence
- ✓ Gemini 3 Pro: {EVIDENCE_COUNT} pieces of evidence
- ✓ Claude Haiku: {EVIDENCE_COUNT} pieces of evidence

**Perspective B Advocates:**
- ✓ GPT-5.2: {EVIDENCE_COUNT} pieces of evidence
- ✓ Gemini 3 Pro: {EVIDENCE_COUNT} pieces of evidence
- ✓ Claude Haiku: {EVIDENCE_COUNT} pieces of evidence

**Total Evidence Reviewed**: {TOTAL_FILES_ANALYZED} files across codebase
```

## Critical Reminders

- ✅ DO launch all 6 agents in PARALLEL (single message, 6 Task calls)
- ✅ DO use 10-minute timeout per agent
- ✅ DO collect arguments from all successful agents
- ✅ DO synthesize objectively without bias
- ✅ DO provide evidence-based recommendation
- ✅ DO identify scenarios where each perspective might be better
- ✅ DO create comparison matrix with objective scoring
- ✅ DO highlight consensus points across models
- ❌ DO NOT search codebase yourself - let agents do research
- ❌ DO NOT favor one perspective over another initially
- ❌ DO NOT restart timed-out agents
- ❌ DO NOT make recommendation without evidence
- ❌ DO NOT ignore minority arguments - consider all perspectives

## Usage Examples

```bash
# API design decision
/compare-contrast "REST vs GraphQL for our API" "REST is better for our microservices architecture" "GraphQL is better for our microservices architecture"

# State management choice
/compare-contrast "Client state management library" "Use Redux for state management" "Use Zustand for state management"

# Database decision
/compare-contrast "Database choice for user data" "PostgreSQL is the best choice" "MongoDB is the best choice"

# Framework comparison
/compare-contrast "Frontend framework for dashboard" "Stick with React" "Migrate to Vue.js"

# Architecture pattern
/compare-contrast "Service architecture pattern" "Implement microservices architecture" "Keep monolithic architecture"

# Testing strategy
/compare-contrast "Testing approach for new features" "Focus on integration tests" "Focus on unit tests"

# Deployment strategy
/compare-contrast "Deployment platform choice" "Deploy to AWS ECS" "Deploy to Railway"
```

**Output**:
- 6 evidence-based arguments (3 models × 2 perspectives)
- Objective comparison matrix
- Consensus analysis across models
- Final recommendation with rationale
- Implementation guidance
- Risk mitigation strategies
