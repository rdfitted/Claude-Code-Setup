---
description: Execute scout, plan, and build workflow in succession with proper variable passing
argument-hint: [feature-description] [scout-scale]
model: claude-sonnet-4-5-20250929
allowed-tools: [SlashCommand, TodoWrite, Read, Glob]
---

# Purpose

Orchestrate a complete feature development workflow by executing `/scout`, `/plan`, and `/build` commands in succession, ensuring proper variable passing between each stage while maintaining context window efficiency.

## Variables

- `{FEATURE_DESCRIPTION}`: User's feature request
- `{SCOUT_SCALE}`: Number of scout agents (1-5, default: 2)
- `{SCOUT_RESULTS}`: File list from scout command
- `{PLAN_FILENAME}`: Generated plan file path
- `{BUILD_INPUT}`: Plan file path for build command

## Instructions

1. Parse user input to extract feature description and optional scout scale
2. Create a todo list with 3 main stages: Scout, Plan, Build
3. Execute each slash command in sequence using SlashCommand tool
4. Pass results between commands as context
5. Track progress and handle any failures gracefully
6. Report final implementation results

## Workflow

**CRITICAL**: Run the workflow in order, top to bottom. Do not stop in between steps. Complete every step in the workflow before stopping.

### Step 1: Run Scout Command
```
Run SlashCommand('/scout "[USER_PROMPT]" "[SCALE]"') -> `relevant_files_collection_path`
```
**Purpose**: Find relevant files in codebase for the feature
**Output Variable**: Store result as `relevant_files_collection_path`

### Step 2: Run Plan Command
```
Run SlashCommand('/plan "[USER_PROMPT]"') -> `path_to_plan`
```
**Purpose**: Generate implementation plan using Codex with high reasoning
**Input**: Feature description and context from `relevant_files_collection_path` (Step 1)
**Output Variable**: Store result as `path_to_plan`

### Step 3: Run Build Command
```
Run SlashCommand('/build "[path_to_plan]"') -> `build_report`
```
**Purpose**: Implement feature following the generated plan
**Input**: Uses `path_to_plan` from Step 2
**Output Variable**: Store result as `build_report`

### Step 4: Final Report
```
Finally, report the work done based on the `Report` section.
```
**Purpose**: Generate comprehensive workflow summary using all collected outputs

## Todo List Structure

Create todos at start:
```json
[
  {
    "content": "Scout codebase for relevant files",
    "activeForm": "Scouting codebase for relevant files",
    "status": "pending"
  },
  {
    "content": "Create implementation plan",
    "activeForm": "Creating implementation plan",
    "status": "pending"
  },
  {
    "content": "Build feature from plan",
    "activeForm": "Building feature from plan",
    "status": "pending"
  }
]
```

## Command Execution Flow

### Step 1: Initialize Workflow
```
1. Parse feature description and scout scale
2. Create 3-stage todo list
3. Display workflow overview
```

### Step 2: Execute Scout Command
```
Use SlashCommand tool:
command: "/scout \"{FEATURE_DESCRIPTION}\" {SCOUT_SCALE}"

Expected output:
- List of relevant files with line ranges
- Agent performance summary
- Priority files ranked by consensus

Store scout results for plan context.
```

### Step 3: Execute Plan Command
```
Use SlashCommand tool:
command: "/plan \"{FEATURE_DESCRIPTION}\""

Context to provide:
- Scout results (files found)
- Feature description

Expected output:
- Plan file path (e.g., plans/feature-name.md)
- Plan summary
- Key components identified

Extract and store plan file path.
```

### Step 4: Execute Build Command
```
Use SlashCommand tool:
command: "/build {PLAN_FILENAME}"

Input:
- Plan file path from previous stage

Expected output:
- Files created/modified
- Implementation summary
- Next steps

Collect final results.
```

### Step 5: Generate Final Report
```
Synthesize all results:
- Scout findings
- Plan details
- Implementation results

Present comprehensive summary to user.
```

## Error Handling

### Scout Stage Failure
- If scout times out or fails � Proceed to plan anyway with feature description
- Note: Plan will use high reasoning without file context

### Plan Stage Failure
- If plan creation fails � Ask user if they want to proceed with quick build
- Option: Use `/build "{FEATURE_DESCRIPTION}"` (quick iteration mode)

### Build Stage Failure
- If build fails � Report error and provide plan file for manual review
- User can retry build or modify plan

## Report Format

```markdown
# Feature Development Complete: {FEATURE_NAME}

## Workflow Summary
**Feature**: {FEATURE_DESCRIPTION}
**Scout Scale**: {SCOUT_SCALE} agents
**Status**:  Complete

---

## Stage 1: Scout Results
**Files Found**: {FILE_COUNT}
**Top Priority Files**:
- {file_path} (offset: N, limit: M)
- {file_path} (offset: N, limit: M)

**Agent Performance**:
-  Gemini Flash: {count} files
-  Gemini Lite: {count} files
-  Codex: {count} files

---

## Stage 2: Plan Created
**Plan File**: `{PLAN_FILENAME}`
**Key Components**:
- {component_list}
- {architecture_notes}
- {implementation_steps_count} steps defined

---

## Stage 3: Implementation Complete
**Files Created/Modified**:
- `{file_path}` - {description}
- `{file_path}` - {description}

**Implementation Summary**:
{summary_from_build}

**Deviations from Plan**:
{deviations_if_any}

---

## Next Steps
1.  Review implementation in modified files
2.  Run tests: `npm test` (or appropriate command)
3.  Test feature manually
4.  Review plan: `cat {PLAN_FILENAME}`
5.  Commit changes if satisfied

---

=� **Full Plan**: `{PLAN_FILENAME}`
=� **Implementation**: Complete
<� **Ready for Testing**
```

## Critical Reminders

-  DO use SlashCommand tool to execute each command
-  DO wait for each command to complete before proceeding
-  DO pass results between stages as context
-  DO update todos after each stage
-  DO handle errors gracefully with fallback options
- L DO NOT execute commands in parallel
- L DO NOT skip stages (unless handling errors)
- L DO NOT lose context between stages

## Variable Passing Example

```
User Input: "Add user authentication with OAuth2" (scale: 3)

Stage 1 - Scout:
  Input: "Add user authentication with OAuth2", scale=3
  Output: Files found � [auth.service.ts, user.model.ts, oauth.config.ts]

Stage 2 - Plan:
  Input: Feature="Add user authentication with OAuth2"
  Context: Scout found auth.service.ts, user.model.ts, oauth.config.ts
  Output: Plan saved � plans/add-user-authentication-with-oauth2.md

Stage 3 - Build:
  Input: plans/add-user-authentication-with-oauth2.md
  Context: Plan includes scout findings, implementation steps
  Output: Files created/modified � [final implementation]
```

## Usage Examples

```bash
# Basic workflow with default scout scale (2)
/scout_plan_build "Add user authentication with OAuth2"

# Workflow with custom scout scale
/scout_plan_build "Add payment processing" 4

# Complex feature with deep scouting
/scout_plan_build "Implement real-time chat with WebSockets" 5

# Quick feature with minimal scouting
/scout_plan_build "Add logout button to header" 1
```

## Execution Timeline

| Stage | Command | Duration Estimate | Output |
|-------|---------|------------------|--------|
| Scout | `/scout` | 30s - 3min | File list with line ranges |
| Plan | `/plan` | 1-2min | Plan file (plans/*.md) |
| Build | `/build` | 2-5min | Implemented feature |
| **Total** | | **3-10min** | **Complete feature** |

## Benefits of This Workflow

1. **Context Window Efficiency**: Each stage uses separate agent contexts
2. **Proper Scoping**: Scout ensures relevant files are identified
3. **Structured Planning**: Codex creates comprehensive implementation plan
4. **Consistent Execution**: Build follows plan with medium reasoning
5. **Full Traceability**: Each stage is documented and tracked
6. **Error Recovery**: Graceful handling with fallback options
