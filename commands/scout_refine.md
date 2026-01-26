---
description: Execute scout and refine workflow to re-assess codebase and update an existing plan
argument-hint: [plan-file-path] [scout-scale] [refinement-criteria]
model: claude-sonnet-4-5-20250929
allowed-tools: [SlashCommand, TodoWrite, Read, Glob]
---

# Purpose

Orchestrate a comprehensive plan refinement workflow by executing `/scout` and `/refine` commands in succession. This workflow re-assesses the codebase, searches for updated documentation, and then refines an existing implementation plan using multiple AI agents with fresh context.

## Variables

- `{PLAN_FILE_PATH}`: Path to existing plan file to refine
- `{SCOUT_SCALE}`: Number of scout agents (1-6, default: 5 for documentation)
- `{REFINEMENT_CRITERIA}`: Optional specific refinement criteria
- `{SCOUT_RESULTS}`: File list and documentation from scout command
- `{AIDOCS_PATH}`: Documentation file saved/updated by scout (if scale >= 5)
- `{REFINED_PLAN}`: Updated plan file after refinement

## Instructions

1. Parse user input to extract plan file path, scout scale, and optional refinement criteria
2. Verify plan file exists before starting workflow
3. Create a todo list with 2 main stages: Scout, Refine
4. Execute each slash command in sequence using SlashCommand tool
5. Pass scout results (especially aidocs) to refine command as context
6. Track progress and handle any failures gracefully
7. Report final refinement results with documentation references

## Workflow

**CRITICAL**: Run the workflow in order, top to bottom. Do not stop in between steps. Complete every step in the workflow before stopping.

### Step 1: Verify Plan Exists
```
Use Read tool to verify {PLAN_FILE_PATH} exists
Extract feature name from plan for scout context
```

### Step 2: Run Scout Command
```
Run SlashCommand('/scout "[FEATURE_FROM_PLAN]" "[SCALE]"') -> `scout_results` and `aidocs_path`
```
**Purpose**: Re-assess codebase files AND gather updated online documentation (if scale >= 5)
**Output Variables**:
- Store codebase files as `relevant_files_collection`
- Store documentation path as `aidocs_path` (if scale >= 5)
- Store key findings for refinement context

### Step 3: Run Refine Command
```
Run SlashCommand('/refine "[PLAN_FILE_PATH]" "[REFINEMENT_CRITERIA]"') -> `refined_plan_path`
```
**Purpose**: Refine existing plan using 4 AI agents with updated documentation context
**Input**:
- Existing plan file path
- Optional refinement criteria
- Context from scout results (updated files + new documentation)
- Updated aidocs path for agents to reference
**Output Variable**: Store result as `refined_plan_path`

### Step 4: Final Report
```
Finally, report the work done based on the `Report` section.
```
**Purpose**: Generate comprehensive workflow summary with scout findings and refinement details

## Todo List Structure

Create todos at start:
```json
[
  {
    "content": "Re-scout codebase and gather updated documentation",
    "activeForm": "Re-scouting codebase and gathering updated documentation",
    "status": "pending"
  },
  {
    "content": "Refine implementation plan with multi-agent analysis",
    "activeForm": "Refining implementation plan with multi-agent analysis",
    "status": "pending"
  }
]
```

## Command Execution Flow

### Step 1: Initialize Workflow
```
1. Parse plan file path, scout scale (default: 5), and refinement criteria
2. Verify plan file exists using Read tool
3. Extract feature name from plan
4. Create 2-stage todo list
5. Display workflow overview
```

### Step 2: Execute Scout Command
```
Use SlashCommand tool:
command: "/scout \"{FEATURE_NAME_FROM_PLAN}\" {SCOUT_SCALE}"

Expected output:
- List of relevant codebase files with line ranges
- Agent performance summary
- Priority files ranked by consensus
- Updated documentation resources (if scale >= 5)
- Aidocs file path (created or updated if scale >= 5)

Store scout results for refinement context.
```

### Step 3: Execute Refine Command
```
Use SlashCommand tool:
command: "/refine \"{PLAN_FILE_PATH}\" \"{REFINEMENT_CRITERIA}\""

Context to provide:
- Scout results (updated files found)
- Updated aidocs path for documentation reference
- Refinement criteria (if specified)

Expected output:
- Updated plan file at same path
- Multi-agent refinement synthesis summary
- Key changes made to plan
- Agent contributions breakdown
- Documentation integration notes

Extract refinement summary.
```

### Step 4: Generate Final Report
```
Synthesize all results:
- Scout findings (updated files + new documentation)
- Refinement details with agent synthesis
- What changed in the plan
- Documentation integration

Present comprehensive summary to user.
```

## Error Handling

### Plan File Not Found
- If plan file doesn't exist → Report error immediately
- Cannot proceed without existing plan
- Suggest using `/plan` to create initial plan first

### Scout Stage Failure
- If scout times out or fails → Proceed to refine anyway
- Note: Refine will still use 4 agents but without updated codebase context
- Recommend re-running scout separately later

### Refine Stage Failure
- If refine fails → Report error and provide scout results
- User can review scout findings and retry refine manually
- Updated aidocs still available for manual reference

## Report Format

```markdown
# Plan Refinement Complete: {FEATURE_NAME}

## Workflow Summary
**Plan File**: `{PLAN_FILE_PATH}`
**Feature**: {FEATURE_NAME}
**Scout Scale**: {SCOUT_SCALE} agents
**Refinement Criteria**: {REFINEMENT_CRITERIA or "General improvement with updated context"}
**Status**: ✅ Complete

---

## Stage 1: Scout Results (Codebase Re-Assessment)
**Codebase Files Found**: {FILE_COUNT}
**Documentation Status**: {DOCS_STATUS}

**Top Priority Files**:
- {file_path} (offset: N, limit: M) - Found by X agents
- {file_path} (offset: N, limit: M) - Found by X agents

{If scale >= 5:
**Updated Documentation**: {URL_COUNT} resources found
**New Findings**:
- {new_finding_summary}
- {new_finding_summary}

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
- ✓ GPT-5.1-Codex-Mini #1: {count} docs
- ✓ GPT-5.1-Codex-Mini #2: {count} docs
}

---

## Stage 2: Multi-Agent Plan Refinement
**Refinement Date**: {DATE}
**Refinement Agents**: GPT-5.2, Gemini 3 Pro, Opus 4.5
**Documentation Referenced**: {AIDOCS_STATUS}

### Refinement Summary
- **Codex refined**: {key_contribution}
- **Gemini Pro refined**: {key_contribution}
- **Gemini Thinking refined**: {key_contribution}
- **Sonnet refined**: {key_contribution}

### Key Changes Made

#### Requirements
- {change_summary}

#### Architecture
- {change_summary}

#### Implementation Steps
- {change_summary}

#### Testing Strategy
- {change_summary}

#### Risks & Considerations
- {change_summary}

#### New Sections Added
{If any: list new sections}

### Agent Consensus on Improvements
**High Priority Changes** (multiple agents agreed):
- {consensus_change}
- {consensus_change}

**Valuable Unique Insights**:
- **From {Agent}**: {unique_insight}
- **From {Agent}**: {unique_insight}

### What Stayed the Same
{Aspects preserved because all agents agreed they were solid}

---

## Documentation Integration
{If new aidocs found or updated:
✅ **Documentation successfully updated and integrated**
- Scout gathered/updated: {URL_COUNT} documentation resources
- Refinement agents referenced: `{AIDOCS_PATH}`
- New insights from docs incorporated into refined plan
- Documentation file updated with latest findings
}
{If scale < 5:
⚠️ **No documentation gathered**
- Scout scale was {SCALE} (need 5+ for documentation)
- Recommendation: Re-run with `/scout_refine "{PLAN_FILE_PATH}" 5` or higher
}

---

## Codebase Context Update
**Files Assessed**: {FILE_COUNT}
**Priority Changes Detected**: {PRIORITY_CHANGES if any}

The plan has been updated to reflect:
- Current codebase state
- Updated file locations and structures
- New dependencies or patterns discovered
- Integration points with existing code

---

## Next Steps
1. 📋 **Review the refined plan**: `cat {PLAN_FILE_PATH}`
2. 📚 **Check updated documentation**: `cat {AIDOCS_PATH}`
3. 🔄 **Compare changes** (Git diff recommended): `git diff {PLAN_FILE_PATH}`
4. 🔍 **Review refinement decisions** in plan metadata
5. 🚀 **Proceed with implementation**: `/build {PLAN_FILE_PATH}`

Or continue refining:
6. 🔄 **Re-run with different criteria**: `/scout_refine "{PLAN_FILE_PATH}" {SCALE} "new criteria"`

---

📁 **Refined Plan**: `{PLAN_FILE_PATH}`
📚 **Updated Documentation**: `{AIDOCS_PATH or "None (scale < 5)"}`
🤖 **Refinement Agents**: 3 (GPT-5.2, Gemini 3 Pro, Opus 4.5)
🔍 **Scout Agents**: {SCOUT_SCALE}
🔄 **Refinement Type**: {REFINEMENT_CRITERIA or "General improvement"}
```

## Critical Reminders

- ✅ DO verify plan file exists before starting
- ✅ DO use SlashCommand tool to execute each command
- ✅ DO wait for each command to complete before proceeding
- ✅ DO pass scout results to refine command as context
- ✅ DO update todos after each stage
- ✅ DO handle errors gracefully with fallback options
- ✅ DO recommend scale >= 5 for documentation gathering
- ✅ DO verify aidocs path exists before referencing
- ✅ DO extract feature name from plan for scout context
- ❌ DO NOT execute commands in parallel
- ❌ DO NOT skip stages (unless handling errors)
- ❌ DO NOT lose context between stages
- ❌ DO NOT forget to pass updated aidocs context to refine command
- ❌ DO NOT proceed if plan file doesn't exist

## Variable Passing Example

```
User Input: /scout_refine "plans/stripe-payment-integration.md" 6 "Add security best practices"

Stage 1 - Verify Plan:
  Input: "plans/stripe-payment-integration.md"
  Action: Read file, extract feature name "Stripe payment integration"
  Output: Plan exists ✓, Feature name extracted

Stage 2 - Scout:
  Input: "Stripe payment integration", scale=6
  Output:
    - Codebase files → [payment.service.ts, stripe.config.ts, checkout.controller.ts]
    - Documentation → aidocs/stripe-payment-integration-docs.md
      * Updated with 8 new URLs
      * New security best practices found
      * PCI compliance documentation
    - Agents: 4 codebase + 4 documentation scouts

Stage 3 - Refine:
  Input:
    - Plan file="plans/stripe-payment-integration.md"
    - Refinement criteria="Add security best practices"
  Context:
    - Scout found updated payment.service.ts, stripe.config.ts, checkout.controller.ts
    - Updated documentation at aidocs/stripe-payment-integration-docs.md
    - New security docs available (PCI compliance, best practices)
  Refinement Agents: Codex, Gemini Pro, Gemini Thinking, Sonnet
  Process:
    - All 4 agents receive updated aidocs with new security docs
    - Each analyzes existing plan for security gaps
    - Each suggests security improvements
    - Main agent synthesizes best security refinements
  Output: Plan updated with:
    - New "Security & PCI Compliance" section
    - Enhanced error handling for payment failures
    - Added webhook signature verification
    - Updated testing strategy with security tests
    - New risk considerations for payment data
  File: plans/stripe-payment-integration.md (updated in place)
```

## Usage Examples

```bash
# Re-assess and refine with documentation (recommended)
/scout_refine "plans/user-authentication.md" 5

# Comprehensive re-assessment with specific refinement
/scout_refine "plans/user-authentication.md" 6 "Add OAuth2 security best practices"

# Quick re-assessment (no new docs)
/scout_refine "plans/api-endpoints.md" 2 "Optimize for performance"

# Full documentation update and refinement
/scout_refine "plans/real-time-chat.md" 6 "Scale to 10k concurrent users"

# Re-assess after codebase changes
/scout_refine "plans/payment-integration.md" 5 "Update for new API version"

# Default scale (5 - includes documentation)
/scout_refine "plans/database-migration.md"
```

## Execution Timeline

| Stage | Command | Duration Estimate | Output |
|-------|---------|------------------|--------|
| Verify | Read plan | 1-2s | Feature name extracted |
| Scout | `/scout` | 30s - 3min | Updated files + Documentation |
| Refine | `/refine` | 3-6min | Multi-agent refined plan |
| **Total** | | **4-9min** | **Refined plan with updated context** |

## Benefits of This Workflow

1. **Fresh Context**: Re-assess codebase before refining plan
2. **Updated Documentation**: Gather latest docs and best practices (scale >= 5)
3. **Multi-Agent Refinement**: 4 different AI models review and improve plan
4. **Codebase Awareness**: Plan updated to reflect current code state
5. **Context Window Efficiency**: Each stage uses separate agent contexts
6. **Comprehensive Improvement**: Both code changes and doc updates incorporated
7. **Traceable Changes**: Clear record of scout findings and refinements
8. **Time Efficient**: Streamlined 2-stage workflow vs 3+ separate commands
9. **Quality Maximization**: Fresh scout data + multi-agent refinement = best outcome

## Recommended Scout Scales

- **Scale 1-2**: Quick codebase re-assessment only (no documentation)
- **Scale 3-4**: Comprehensive codebase re-assessment (no documentation)
- **Scale 5**: Codebase + updated documentation (2 doc agents) ⭐ **Recommended default**
- **Scale 6**: Codebase + extensive documentation (4 doc agents) ⭐ **Best for comprehensive updates**

## When to Use This Command

✅ **Use `/scout_refine`** when:
- Codebase has changed since original plan was created
- You want to incorporate latest documentation and best practices
- Dependencies or API versions have been updated
- You need fresh multi-agent perspective on existing plan
- You want to add specific improvements (security, performance, etc.)
- Time has passed and you want to update plan with current knowledge

❌ **Use separate commands** when:
- You only need to re-scout codebase (`/scout`)
- You only need to refine plan without new scout (`/refine`)
- You want to review scout results before refining
- Plan is brand new and doesn't need re-assessment

## Follow-Up Workflow

After `/scout_refine` completes, you can:

1. **Review Changes**:
   - Review refined plan: `cat {PLAN_FILE_PATH}`
   - Review updated docs: `cat {AIDOCS_PATH}`
   - Compare changes: `git diff {PLAN_FILE_PATH}`

2. **Further Refinement**:
   - Run again with different criteria: `/scout_refine "{PLAN_FILE_PATH}" {scale} "new criteria"`
   - Manually edit plan if needed

3. **Continue to Implementation**:
   - Run: `/build {PLAN_FILE_PATH}`
   - Or: `/scout_plan_build` if you want completely fresh implementation

4. **Test Implementation**:
   - After build, run: `/test_features "{feature}" {url}`

## Comparison: /scout_refine vs /scout_plan

| Aspect | /scout_refine | /scout_plan |
|--------|---------------|-------------|
| **Input** | Existing plan file | Feature description |
| **Output** | Refined existing plan | New plan file |
| **Use Case** | Update existing plan | Create new plan |
| **Scout Purpose** | Re-assess codebase changes | Initial discovery |
| **Documentation** | Update existing aidocs | Create new aidocs |
| **Planning** | 4 agents refine | 4 agents create |
| **Result** | Plan updated in place | New plan file |
| **When** | Plan exists, needs update | No plan exists yet |

## Refinement Criteria Ideas

When using `/scout_refine`, consider these refinement criteria:

**Security-Focused**:
- "Add comprehensive security and threat modeling"
- "Add PCI compliance requirements"
- "Add OAuth2/OIDC security best practices"
- "Add OWASP Top 10 mitigation"

**Performance-Focused**:
- "Optimize for high-traffic scenarios"
- "Add caching and rate limiting strategies"
- "Scale to {N} concurrent users"
- "Reduce API response times"

**Quality-Focused**:
- "Add comprehensive error handling"
- "Improve testing strategy with edge cases"
- "Add monitoring and observability"
- "Enhance code documentation"

**Update-Focused**:
- "Update for {Framework} version {X}"
- "Update for new API version"
- "Incorporate latest best practices"
- "Add newly released framework features"

**Architectural**:
- "Simplify architecture for faster MVP"
- "Add microservices architecture"
- "Improve modularity and separation of concerns"
- "Add event-driven patterns"
