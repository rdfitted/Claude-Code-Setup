---
description: Execute scout and plan workflow in succession with proper variable passing
argument-hint: [feature-description] [scout-scale]
model: claude-sonnet-4-5-20250929
allowed-tools: [SlashCommand, TodoWrite, Read, Glob]
---

# Purpose

Orchestrate a streamlined feature planning workflow by executing `/scout` and `/plan` commands in succession, ensuring documentation is gathered before multi-agent planning begins. This workflow maximizes planning quality by providing all agents with comprehensive documentation context.

## Variables

- `{FEATURE_DESCRIPTION}`: User's feature request
- `{SCOUT_SCALE}`: Number of scout agents (1-6, default: 5 for documentation)
- `{SCOUT_RESULTS}`: File list and documentation from scout command
- `{AIDOCS_PATH}`: Documentation file saved by scout (if scale >= 5)
- `{PLAN_FILENAME}`: Generated plan file path

## Instructions

1. Parse user input to extract feature description and optional scout scale
2. Create a todo list with 2 main stages: Scout, Plan
3. Execute each slash command in sequence using SlashCommand tool
4. Pass scout results (especially aidocs) to plan command as context
5. Track progress and handle any failures gracefully
6. Report final plan results with documentation references

## Workflow

**CRITICAL**: Run the workflow in order, top to bottom. Do not stop in between steps. Complete every step in the workflow before stopping.

### Step 1: Run Scout Command
```
Run SlashCommand('/scout "[USER_PROMPT]" "[SCALE]"') -> `scout_results` and `aidocs_path`
```
**Purpose**: Find relevant codebase files AND gather online documentation (if scale >= 5)
**Output Variables**:
- Store codebase files as `relevant_files_collection`
- Store documentation path as `aidocs_path` (if scale >= 5)

### Step 2: Run Plan Command
```
Run SlashCommand('/plan "[USER_PROMPT]"') -> `path_to_plan`
```
**Purpose**: Generate multi-agent implementation plan using documentation context
**Input**:
- Feature description
- Context from scout results (files + documentation)
- Aidocs path for agents to reference
**Output Variable**: Store result as `path_to_plan`

### Step 3: Final Report
```
Finally, report the work done based on the `Report` section.
```
**Purpose**: Generate comprehensive workflow summary with documentation and plan details

## Todo List Structure

Create todos at start:
```json
[
  {
    "content": "Scout codebase and gather documentation",
    "activeForm": "Scouting codebase and gathering documentation",
    "status": "pending"
  },
  {
    "content": "Create multi-agent implementation plan",
    "activeForm": "Creating multi-agent implementation plan",
    "status": "pending"
  }
]
```

## Command Execution Flow

### Step 1: Initialize Workflow
```
1. Parse feature description and scout scale (default: 5 for documentation)
2. Create 2-stage todo list
3. Display workflow overview
```

### Step 2: Execute Scout Command
```
Use SlashCommand tool:
command: "/scout \"{FEATURE_DESCRIPTION}\" {SCOUT_SCALE}"

Expected output:
- List of relevant codebase files with line ranges
- Agent performance summary
- Priority files ranked by consensus
- Documentation resources (if scale >= 5)
- Aidocs file path (if scale >= 5)

Store scout results, especially aidocs path.
```

### Step 3: Execute Plan Command
```
Use SlashCommand tool:
command: "/plan \"{FEATURE_DESCRIPTION}\""

Context to provide:
- Scout results (files found)
- Feature description
- Aidocs path for documentation reference

Expected output:
- Plan file path (e.g., plans/feature-name.md)
- Multi-agent synthesis summary
- Key components identified
- Agent contributions breakdown
- Documentation integration notes

Extract and store plan file path.
```

### Step 4: Generate Final Report
```
Synthesize all results:
- Scout findings (files + documentation)
- Plan details with agent synthesis
- Documentation integration

Present comprehensive summary to user.
```

## Error Handling

### Scout Stage Failure
- If scout times out or fails → Proceed to plan anyway with feature description
- Note: Plan will still use 4 agents but without documentation context
- Recommend re-running with working scout later

### Plan Stage Failure
- If plan creation fails → Report error and provide scout results
- User can review scout findings and retry plan manually
- Aidocs still available for manual reference

## Report Format

```markdown
# Feature Planning Complete: {FEATURE_NAME}

## Workflow Summary
**Feature**: {FEATURE_DESCRIPTION}
**Scout Scale**: {SCOUT_SCALE} agents
**Status**: ✅ Complete

---

## Stage 1: Scout Results
**Codebase Files Found**: {FILE_COUNT}
**Documentation Gathered**: {DOCS_STATUS}

**Top Priority Files**:
- {file_path} (offset: N, limit: M) - Found by X agents
- {file_path} (offset: N, limit: M) - Found by X agents

{If scale >= 5:
**Documentation Resources**: {URL_COUNT} URLs found
**Key Findings**:
- {finding_summary}
- {finding_summary}

📁 **Documentation saved to**: `{AIDOCS_PATH}`
}

**Agent Performance**:
- ✓ Gemini Flash: {count} files
- ✓ Gemini Lite: {count} files
- ✓ Codex: {count} files
- ✓ Claude Haiku: {count} files
{If scale >= 5:
- ✓ Gemini Flash Light #1: {count} docs
- ✓ Gemini Flash Light #2: {count} docs
}
{If scale == 6:
- ✓ GPT-5-Codex-Mini #1: {count} docs
- ✓ GPT-5-Codex-Mini #2: {count} docs
}

---

## Stage 2: Multi-Agent Plan Created
**Plan File**: `{PLAN_FILENAME}`
**Planning Agents**: GPT-5.2, Gemini 3 Pro, Opus 4.5
**Documentation Referenced**: {AIDOCS_STATUS}

### Synthesis Summary
- **Codex contributed**: {key_contribution}
- **Gemini Pro contributed**: {key_contribution}
- **Gemini Thinking contributed**: {key_contribution}
- **Sonnet contributed**: {key_contribution}

### Plan Highlights
- **Implementation Steps**: {count} detailed steps
- **Key Components**: {component_list}
- **Architecture Approach**: {chosen_architecture}
- **Estimated Effort**: {estimate}

### Agent Consensus
**Areas of Agreement**:
- {consensus_point}
- {consensus_point}

**Key Differences Resolved**:
- {divergence_and_resolution}

---

## Documentation Integration
{If aidocs found:
✅ **Documentation successfully integrated**
- Scout gathered: {URL_COUNT} documentation resources
- Planning agents referenced: `{AIDOCS_PATH}`
- Key insights from docs incorporated into plan
}
{If aidocs not found:
⚠️ **No documentation gathered**
- Scout scale was {SCALE} (need 5+ for documentation)
- Recommendation: Re-run with `/scout_plan "{FEATURE}" 5` or higher
}

---

## Next Steps
1. 📋 **Review the synthesized plan**: `cat {PLAN_FILENAME}`
2. 📚 **Check documentation** (if gathered): `cat {AIDOCS_PATH}`
3. 🔍 **Refine requirements** if needed
4. 🚀 **Begin implementation**: `/build {PLAN_FILENAME}`

Or continue with full workflow:
5. 🏗️ **Scout → Plan → Build**: Already done first 2 steps!
6. ▶️ **Just run**: `/build {PLAN_FILENAME}`

---

📋 **Synthesized Plan**: `{PLAN_FILENAME}`
📚 **Documentation**: `{AIDOCS_PATH or "None (scale < 5)"}`
🤖 **Planning Agents**: 3 (GPT-5.2, Gemini 3 Pro, Opus 4.5)
🔍 **Scout Agents**: {SCOUT_SCALE}
```

## Critical Reminders

- ✅ DO use SlashCommand tool to execute each command
- ✅ DO wait for each command to complete before proceeding
- ✅ DO pass scout results to plan command as context
- ✅ DO update todos after each stage
- ✅ DO handle errors gracefully with fallback options
- ✅ DO recommend scale >= 5 for documentation gathering
- ✅ DO verify aidocs path exists before referencing
- ❌ DO NOT execute commands in parallel
- ❌ DO NOT skip stages (unless handling errors)
- ❌ DO NOT lose context between stages
- ❌ DO NOT forget to pass aidocs context to plan command

## Variable Passing Example

```
User Input: "Add Stripe payment integration" (scale: 6)

Stage 1 - Scout:
  Input: "Add Stripe payment integration", scale=6
  Output:
    - Codebase files → [payment.service.ts, checkout.controller.ts, billing.model.ts]
    - Documentation → aidocs/add-stripe-payment-integration-docs.md (15 URLs, key findings)
    - Agents: Gemini Flash, Lite, Codex, Haiku + 4 documentation scouts

Stage 2 - Plan:
  Input: Feature="Add Stripe payment integration"
  Context:
    - Scout found payment.service.ts, checkout.controller.ts, billing.model.ts
    - Documentation available at aidocs/add-stripe-payment-integration-docs.md
  Planning Agents: Codex, Gemini Pro, Gemini Thinking, Sonnet
  Process:
    - All 4 agents receive aidocs context
    - Each creates a plan referencing Stripe documentation
    - Main agent synthesizes best plan from all 4
  Output: Plan saved → plans/add-stripe-payment-integration.md
```

## Usage Examples

```bash
# Basic workflow with documentation (recommended)
/scout_plan "Add user authentication with OAuth2" 5

# Maximum documentation gathering
/scout_plan "Stripe payment integration" 6

# Quick planning with minimal scouting (no docs)
/scout_plan "Add logout button to header" 2

# Complex feature with comprehensive documentation
/scout_plan "Real-time chat with WebSockets" 6

# Default scout scale (5 - includes documentation)
/scout_plan "Implement GraphQL API"
```

## Execution Timeline

| Stage | Command | Duration Estimate | Output |
|-------|---------|------------------|--------|
| Scout | `/scout` | 30s - 3min | Files + Documentation |
| Plan | `/plan` | 3-6min | Multi-agent synthesized plan |
| **Total** | | **3.5-9min** | **Plan with documentation** |

## Benefits of This Workflow

1. **Documentation-First Planning**: Documentation gathered before planning begins
2. **Context Window Efficiency**: Each stage uses separate agent contexts
3. **Informed Planning**: All 4 planning agents have documentation context
4. **Proper Scoping**: Scout ensures relevant files and docs are identified
5. **Multi-Agent Synthesis**: Codex, Gemini (2x), and Sonnet perspectives combined
6. **Full Traceability**: Documentation and planning both tracked and saved
7. **Time Efficient**: Streamlined 2-stage workflow (vs 3-4 separate commands)
8. **Quality Maximization**: Best documentation + best planning = best outcome

## Recommended Scout Scales

- **Scale 1-2**: Quick codebase search only (no documentation)
- **Scale 3-4**: Comprehensive codebase search (no documentation)
- **Scale 5**: Codebase + basic documentation (2 doc agents) ⭐ **Recommended default**
- **Scale 6**: Codebase + extensive documentation (4 doc agents) ⭐ **Best for complex features**

## When to Use This Command

✅ **Use `/scout_plan`** when:
- You want comprehensive planning with documentation
- You need multi-agent plan synthesis
- You want to gather docs and plan in one workflow
- You're starting a new feature from scratch

❌ **Use separate commands** when:
- You only need documentation (`/scout` with scale 5-6)
- You only need a plan (`/plan`)
- You want to review scout results before planning
- You already have documentation and just need a plan

## Follow-Up Workflow

After `/scout_plan` completes, you can:

1. **Review and Refine**:
   - Review plan: `cat plans/{filename}`
   - Review docs: `cat aidocs/{filename}`
   - Make manual adjustments

2. **Continue to Build**:
   - Run: `/build plans/{filename}`
   - Or full workflow: `/scout_plan_build` (if you want to start fresh)

3. **Test Implementation**:
   - After build, run: `/test_features "{feature}" {url}`
   - Or full workflow: `/scout_plan_build_test`
