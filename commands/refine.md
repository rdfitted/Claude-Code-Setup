---
description: Refine an existing implementation plan using multiple AI planning agents
argument-hint: [plan-file-path] [refinement-criteria]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Write, Glob, Read, Edit]
---

# Purpose

Re-assess an existing implementation plan using multiple high-reasoning AI agents (GPT-5.2, Gemini 3 Pro, Opus 4.5) to refine it based on new criteria, codebase changes, or updated documentation. The main agent synthesizes the best refinements from all agents into an updated plan.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (`codex`, `gemini` via Python SDK) via Bash for multi-model refinement diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive plan refinement.

## Variables

- `{PLAN_FILE_PATH}`: Path to existing plan file (e.g., "plans/user-authentication.md")
- `{REFINEMENT_CRITERIA}`: Optional specific refinement criteria (e.g., "add security considerations", "optimize for performance")
- `{EXISTING_PLAN}`: Content of the current plan
- `{PLANS_DIR}`: Directory for storing plans (default: "plans/")
- `{AIDOCS_DIR}`: Directory with documentation from scout command (default: "aidocs/")
- `{CODEX_REFINEMENT}`: Refinement suggestions from GPT-5.2
- `{GEMINI_REFINEMENT}`: Refinement suggestions from Gemini 3 Pro
- `{SONNET_REFINEMENT}`: Refinement suggestions from Sonnet 4.5
- `{REFINED_PLAN}`: Final refined plan combining best elements from all agents

## Instructions

1. Parse user input to extract plan file path and optional refinement criteria
2. Verify the plan file exists using Read tool
3. Check if `aidocs/` directory exists and look for relevant documentation files
4. **IMPORTANT**: DO NOT refine the plan yourself
5. **IMPORTANT**: Use Task tool to spawn 3 planning agents in PARALLEL
6. Each agent analyzes the existing plan and provides refinement suggestions
7. **IMPORTANT**: Main agent synthesizes the best refinements from all 3 agents
8. Update the existing plan file with refined content using Edit tool
9. Report back the refinement summary and changes made

## Workflow

### Step 1: Load Existing Plan and Check Documentation
```
1. Use Read tool to load the existing plan file
2. Extract feature name and current plan structure
3. **CRITICAL - Ensure context subdirectory exists for agent collaboration files**:
   - Use Bash to create: mkdir -p plans/context
   - **IMPORTANT**: Any collaboration files created by agents during execution MUST be stored in `plans/context/`, NEVER in the root directory
4. Use Glob to check if aidocs/ directory exists: pattern="aidocs/*"
5. If aidocs/ exists, use Glob to find relevant doc files matching plan keywords
6. If relevant docs found, note their paths for context inclusion
7. If refinement criteria provided, add to context
```

### Step 2: Spawn Multiple Refinement Agents in Parallel
**CRITICAL**: Use Task tool to spawn 3 planning agents in a SINGLE message (parallel execution):
- Agent 1: GPT-5.2 with high reasoning and thinking mode
- Agent 2: Gemini 3 Pro (via Python SDK)
- Agent 3: Opus 4.5 (native Claude Code subagent with deep reasoning)

Each agent will:
- Receive the existing plan content and optional refinement criteria
- Analyze the plan for areas of improvement
- Provide specific refinement suggestions
- Return the refinement suggestions to the main agent (NOT update file yet)

### Step 3: Agent Prompt Templates

**Context to Include in All Agent Prompts:**
```
Existing Plan: {EXISTING_PLAN}
Refinement Criteria: {REFINEMENT_CRITERIA if provided, otherwise "General improvement and updates"}
Relevant Documentation: {AIDOCS_PATHS if found, otherwise "None"}
```

**Agent 1 - GPT-5.2 (High Reasoning with Thinking Mode) Prompt:**
```
You are a plan refinement specialist using GPT-5.2. Analyze and refine this existing implementation plan:

EXISTING PLAN:
"""
{EXISTING_PLAN}
"""

REFINEMENT CRITERIA: {REFINEMENT_CRITERIA or "General improvement, updated best practices, and any missing considerations"}

{If aidocs found: "Reference these documentation files for updated context: {AIDOCS_PATHS}"}

IMMEDIATELY use the Bash tool to run this command with high reasoning and thinking mode:
codex exec -m gpt-5.2 -c model_reasoning_effort="high" -c thinking="enabled" --skip-git-repo-check "Analyze this implementation plan and provide specific refinements:

EXISTING PLAN:
{EXISTING_PLAN}

REFINEMENT CRITERIA: {REFINEMENT_CRITERIA}

Provide your refinements in this structure:

# Plan Refinement Analysis

## What's Working Well
[Aspects of the current plan that are solid and should be preserved]

## Areas for Improvement
[Specific sections or aspects that need refinement]

## Recommended Changes

### Requirements
[Specific changes to requirements section]

### Architecture
[Specific changes to architecture section]

### Implementation Steps
[Specific changes to implementation steps]

### Testing Strategy
[Specific changes to testing approach]

### Risks & Considerations
[Additional risks or updated risk assessments]

### Other Improvements
[Any other refinements: security, performance, scalability, etc.]

## Updated Best Practices
[Any new best practices or patterns to incorporate]

## Documentation Integration
[If new documentation found: how to integrate new findings]
"

After the command completes, return the FULL REFINEMENT ANALYSIS to the main agent.

Do NOT update the file. Do NOT create the refinement manually. ONLY run the Codex bash command and return the analysis.
```

**Agent 2 - Gemini 3 Pro Prompt:**
```
You are a plan refinement specialist using Gemini 3 Pro. Analyze and refine this existing implementation plan:

EXISTING PLAN:
"""
{EXISTING_PLAN}
"""

REFINEMENT CRITERIA: {REFINEMENT_CRITERIA or "General improvement, updated best practices, and any missing considerations"}

{If aidocs found: "Reference these documentation files for updated context: {AIDOCS_PATHS}"}

IMMEDIATELY run this exact command using the Bash tool:
(Gemini CLI: using latest installed version)

CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-pro-preview -o text "You are an expert software architect specializing in plan refinement. Analyze this implementation plan and identify architectural improvements, potential pitfalls, and optimization opportunities based on modern best practices. EXISTING PLAN: {EXISTING_PLAN}. REFINEMENT CRITERIA: {REFINEMENT_CRITERIA}. Return as markdown with sections: What's Working Well, Areas for Improvement, Recommended Changes (Requirements, Architecture, Implementation Steps, Testing Strategy, Risks & Considerations), Updated Best Practices, Documentation Integration. Provide specific, actionable improvements while preserving what works well."

CRITICAL: Use gemini-3-pro-preview model. The CLI will have access to the codebase context.

After the command completes, return the FULL REFINEMENT ANALYSIS to the main agent.

Do NOT update the file. Return the analysis only.
```

**Agent 3 - Opus 4.5 (Native Claude Code Subagent with Deep Reasoning) Prompt:**
Use the Task tool instead of Bash (with Opus model for high-reasoning refinement):
```
Task(
  subagent_type="Plan",
  model="opus",
  prompt="You are a plan refinement specialist using Claude Opus 4.5 with deep reasoning. Analyze and refine this existing implementation plan:

EXISTING PLAN:
{EXISTING_PLAN}

REFINEMENT CRITERIA: {REFINEMENT_CRITERIA or General improvement, updated best practices, and any missing considerations}

{If aidocs found: Reference these documentation files for updated context: {AIDOCS_PATHS}}

Think deeply about trade-offs, identify optimal approaches, and suggest improvements.

Return as markdown with sections:
- What's Working Well
- Areas for Improvement
- Recommended Changes (Requirements, Architecture, Implementation Steps, Testing Strategy, Risks & Considerations)
- Updated Best Practices
- Documentation Integration

Return the FULL REFINEMENT ANALYSIS."
)
```

### Step 4: Collect All Refinement Analyses
- Wait for all 3 agents to complete (run in parallel)
- Collect refinement analysis from each agent:
  - Codex Refinement
  - Gemini 3 Pro Refinement
  - Opus Refinement

### Step 5: Synthesize Best Refinements
**Main Agent Task**: Analyze all 3 refinement analyses and create a synthesized refined plan that:
1. **Preserves what's working well** across all agent analyses
2. **Identifies consensus improvements**:
   - Changes recommended by multiple agents (high priority)
   - Unique valuable insights from individual agents
3. **Resolves conflicts**:
   - Where agents disagree, choose the most sound approach
   - Document why certain suggestions were chosen over others
4. **Integrates new documentation** if found in aidocs
5. **Applies refinement criteria** specifically
6. **Maintains plan structure** while improving content
7. **Adds refinement metadata** showing what changed and why

### Step 6: Update Existing Plan File
- Use Edit tool to update the existing plan file at `{PLAN_FILE_PATH}`
- Add refinement metadata at top showing:
  - Date of refinement
  - Refinement criteria applied
  - Agents consulted
  - Summary of key changes
- Preserve original plan metadata
- Update relevant sections with refinements
- Add new sections if needed

## Report Format

After plan refinement, display:

```markdown
# Plan Refined: {FEATURE_NAME}
**File**: `{PLAN_FILE_PATH}`
**Refinement Date**: {DATE}
**Refinement Agents**: GPT-5.2, Gemini 3 Pro, Opus 4.5
**Refinement Criteria**: {REFINEMENT_CRITERIA or "General improvement"}
**Documentation Referenced**: {AIDOCS_FILES or "None"}

## Refinement Summary
This plan was refined using insights from 3 advanced AI planning agents:
- **Codex**: {key refinement contribution}
- **Gemini 3 Pro**: {key refinement contribution}
- **Sonnet**: {key refinement contribution}

## Key Changes Made
### Requirements
- {change summary}

### Architecture
- {change summary}

### Implementation Steps
- {change summary}

### Testing Strategy
- {change summary}

### Risks & Considerations
- {change summary}

### New Sections Added
- {new sections if any}

## Agent Consensus on Improvements
**High Priority Changes** (multiple agents agreed):
- {consensus_change}
- {consensus_change}

**Valuable Unique Insights**:
- **From {Agent}**: {unique_insight}
- **From {Agent}**: {unique_insight}

## Refinement Decision Points
**Conflicting Suggestions Resolved**:
- {conflict}: Chose {chosen_approach} because {reason}

## Documentation Integration
{If new aidocs found: "Integrated new documentation findings from: {file_list}"}
{If aidocs referenced: "Referenced existing documentation: {file_list}"}
{If not found: "No new documentation found. Plan refined based on agents' updated knowledge."}

## What Stayed the Same
{Aspects of the plan that all agents agreed were solid and should be preserved}

## Next Steps
1. 📋 Review the refined plan: `cat {PLAN_FILE_PATH}`
2. 📚 Check documentation updates: {aidocs_paths}
3. 🔄 Compare with original (Git diff recommended)
4. 🚀 Proceed with implementation: `/build {PLAN_FILE_PATH}`

---
📁 **Refined plan**: `{PLAN_FILE_PATH}`
🤖 **Agents consulted**: 3 (GPT-5.2, Gemini 3 Pro, Opus 4.5)
🔄 **Refinement type**: {REFINEMENT_CRITERIA}
📚 **Docs referenced**: {count}
```

## Critical Reminders

- ✅ DO use Task tool to spawn refinement agents
- ✅ DO have agents immediately run Bash with their respective CLIs
- ✅ DO use model_reasoning_effort="high" for detailed analysis
- ✅ DO read the existing plan file first
- ✅ DO create `plans/context/` subdirectory for agent collaboration files
- ✅ DO preserve what's working well in the current plan
- ✅ DO add refinement metadata to the updated plan
- ✅ DO check for updated documentation in aidocs/
- ❌ DO NOT create a new plan file - UPDATE the existing one
- ❌ DO NOT refine the plan yourself
- ❌ DO NOT discard good parts of the existing plan
- ❌ DO NOT skip the synthesis step
- ❌ DO NOT implement the feature - ONLY refine the plan
- 🚫 NEVER allow agents to create collaboration files in root directory - ALWAYS use /plans/context

## Refinement Criteria Examples

Common refinement criteria:
- "Add security considerations and threat modeling"
- "Optimize for performance and scalability"
- "Update with latest framework best practices"
- "Add comprehensive error handling"
- "Improve testing strategy with edge cases"
- "Add accessibility requirements"
- "Update for new API version"
- "Add monitoring and observability"
- "Simplify architecture for faster implementation"
- "Add database migration strategy"

## Usage Examples

```bash
/refine "plans/user-authentication.md"
/refine "plans/user-authentication.md" "Add OAuth2 security best practices"
/refine "plans/payment-integration.md" "Update for Stripe API v2023-10-16"
/refine "plans/real-time-chat.md" "Optimize for 10k concurrent users"
/refine "plans/api-endpoints.md" "Add rate limiting and caching strategies"
```

## Refined Plan File Template

The main agent will update the existing plan file with refinement metadata like:

```markdown
# User Authentication with OAuth2

---
**Plan Metadata**
- **Originally Generated**: {ORIGINAL_DATE}
- **Last Refined**: {REFINEMENT_DATE}
- **Planning Agents**: GPT-5.2, Gemini 3 Pro, Opus 4.5
- **Documentation Referenced**: {AIDOCS_PATHS}

**Refinement History:**
1. {REFINEMENT_DATE} - {REFINEMENT_CRITERIA}
   - Agents: Codex, Gemini 3 Pro, Sonnet
   - Key changes: {summary}

**Agent Contributions (Latest Refinement):**
- Codex: {specific_contribution}
- Gemini 3 Pro: {specific_contribution}
- Sonnet: {specific_contribution}
---

## Overview
[Refined overview with improvements...]

## Requirements
### Functional Requirements
[Updated/refined requirements...]

### Security Requirements ⭐ NEW
[Added based on refinement...]

## Architecture
[Refined architecture with improvements...]

## Implementation Steps
[Updated steps with refinements...]

## Testing Strategy
[Enhanced testing approach...]

## Risks & Considerations
[Updated risk assessment with new considerations...]

## Performance Optimization ⭐ NEW
[New section added during refinement...]

## Success Criteria
[Refined success criteria...]
```

## Multi-Agent Refinement Workflow Details

### Agent Roles in Refinement

**GPT-5.2 (High Reasoning with Thinking Mode)**:
- Deep technical analysis of implementation details
- Identify missing edge cases
- Suggest code-level improvements
- Validate architectural decisions with extended reasoning

**Gemini 3 Pro (via Python SDK)**:
- Modern best practices updates
- Framework-specific improvements
- Performance optimization opportunities
- Clean architecture pattern refinements
- Deep trade-off analysis
- Alternative approach evaluation
- Long-term maintenance considerations
- Scalability implications

**Opus 4.5 (Deep Reasoning)**:
- Security and privacy improvements
- User experience considerations
- Ethical implications
- Accessibility requirements

### Refinement Synthesis Process

The main Claude Code agent performs the following synthesis:

1. **Analyze** each refinement for:
   - Validity (is the suggestion sound?)
   - Priority (how important is this change?)
   - Consensus (do multiple agents agree?)
   - Feasibility (can this be implemented?)

2. **Categorize** suggestions:
   - **Must-have**: Critical improvements (security, correctness)
   - **Should-have**: Important improvements (performance, maintainability)
   - **Nice-to-have**: Optional improvements (polish, optimization)

3. **Resolve** conflicts:
   - When agents disagree, evaluate trade-offs
   - Document decision rationale
   - Prefer consensus approaches when possible

4. **Preserve** existing quality:
   - Don't change what's working well
   - Maintain plan structure and readability
   - Keep valuable existing details

5. **Document** changes:
   - Track what was changed and why
   - Attribute refinements to agents
   - Maintain refinement history

6. **Integrate** new information:
   - Add newly discovered documentation
   - Update for changed best practices
   - Incorporate new framework features

## When to Use /refine vs /plan

**Use /refine when**:
- ✅ You have an existing plan that needs updates
- ✅ Codebase has changed since original plan
- ✅ New documentation or best practices available
- ✅ Specific aspect needs improvement (security, performance, etc.)
- ✅ API versions or dependencies have been updated
- ✅ You want to re-assess with fresh AI perspective

**Use /plan when**:
- ✅ Starting a new feature from scratch
- ✅ No existing plan available
- ✅ Complete redesign needed (not refinement)

## Execution Timeline

| Stage | Duration | Details |
|-------|----------|---------|
| Load Plan & Docs | 5-10s | Read existing plan, check aidocs/ |
| Agent Refinement | 2-4min | 3 agents analyze in parallel |
| Refinement Synthesis | 1-2min | Main agent synthesizes improvements |
| File Update | 5-10s | Edit existing plan with refinements |
| **Total** | **3-6min** | **Refined multi-agent plan** |

## Benefits of Multi-Agent Refinement

1. **Fresh Perspectives**: 3 different AI models review the plan
2. **Consensus Validation**: Multiple agents validate or challenge assumptions
3. **Comprehensive Improvement**: Different agents catch different issues
4. **Updated Best Practices**: Benefit from latest model knowledge
5. **Documentation Integration**: New docs incorporated into plan
6. **Traceable Changes**: Clear record of what changed and why
7. **Preserves Quality**: Doesn't discard what's already working
8. **Targeted Refinement**: Focus on specific criteria when needed
