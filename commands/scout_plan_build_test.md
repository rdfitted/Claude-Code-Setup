---
description: Execute scout, plan, build, and test workflow in succession with proper variable passing
argument-hint: [feature-description] [scout-scale] [test-url]
model: claude-sonnet-4-5-20250929
allowed-tools: [SlashCommand, TodoWrite, Read, Glob, Skill]
---

# Purpose

Orchestrate a complete feature development and testing workflow by executing `/scout`, `/plan`, `/build`, and `/test_features` commands in succession, ensuring proper variable passing between each stage while maintaining context window efficiency.

## Variables

- `{FEATURE_DESCRIPTION}`: User's feature request
- `{SCOUT_SCALE}`: Number of scout agents (1-6, default: 2)
- `{TEST_URL}`: Optional URL for testing the feature
- `{SCOUT_RESULTS}`: File list from scout command
- `{PLAN_FILENAME}`: Generated plan file path
- `{BUILD_REPORT}`: Build implementation summary
- `{TEST_RESULTS}`: Test findings and analysis

## Instructions

1. Parse user input to extract feature description, optional scout scale, and optional test URL
2. Create a todo list with 4 main stages: Scout, Plan, Build, Test
3. Execute each slash command in sequence using SlashCommand tool
4. Pass results between commands as context
5. Track progress and handle any failures gracefully
6. Report final implementation and test results

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

### Step 4: Run Test Command
```
Run SlashCommand('/test_features "[FEATURE_DESCRIPTION]" "[TEST_URL]"') -> `test_results`
```
**Purpose**: Test the implemented feature using browser automation and console analysis
**Input**: Feature description and optional test URL
**Output Variable**: Store result as `test_results`

### Step 5: Final Report
```
Finally, report the work done based on the `Report` section.
```
**Purpose**: Generate comprehensive workflow summary using all collected outputs including test results

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
  },
  {
    "content": "Test feature with browser automation",
    "activeForm": "Testing feature with browser automation",
    "status": "pending"
  }
]
```

## Command Execution Flow

### Step 1: Initialize Workflow
```
1. Parse feature description, scout scale, and optional test URL
2. Create 4-stage todo list
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

Collect build results.
```

### Step 5: Execute Test Command
```
Use SlashCommand tool:
command: "/test_features \"{FEATURE_DESCRIPTION}\" {TEST_URL}"

Input:
- Feature description
- Optional test URL (can be omitted)

Expected output:
- Browser console analysis
- Application console logs
- Screenshots of feature in action
- Issue categorization (Blockers, High-Priority, Medium-Priority, Nitpicks)

Collect test results.
```

### Step 6: Generate Final Report
```
Synthesize all results:
- Scout findings
- Plan details
- Implementation results
- Test analysis and findings

Present comprehensive summary to user.
```

## Error Handling

### Scout Stage Failure
- If scout times out or fails → Proceed to plan anyway with feature description
- Note: Plan will use high reasoning without file context

### Plan Stage Failure
- If plan creation fails → Ask user if they want to proceed with quick build
- Option: Use `/build "{FEATURE_DESCRIPTION}"` (quick iteration mode)

### Build Stage Failure
- If build fails → Report error and provide plan file for manual review
- User can retry build or modify plan
- Skip test stage if build failed critically

### Test Stage Failure
- If test fails → Report error but include build results
- Provide partial test findings if available
- Note: Testing is optional validation, build is still complete

## Report Format

```markdown
# Feature Development Complete: {FEATURE_NAME}

## Workflow Summary
**Feature**: {FEATURE_DESCRIPTION}
**Scout Scale**: {SCOUT_SCALE} agents
**Test URL**: {TEST_URL or "Auto-discovered"}
**Status**: ✅ Complete with Testing

---

## Stage 1: Scout Results
**Files Found**: {FILE_COUNT}
**Top Priority Files**:
- {file_path} (offset: N, limit: M)
- {file_path} (offset: N, limit: M)

**Agent Performance**:
- ✓ Gemini Flash: {count} files
- ✓ Gemini Lite: {count} files
- ✓ Codex: {count} files

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

## Stage 4: Test Results
**Testing Method**: Browser automation with Gemini Computer Use
**Console Analysis**: {console_status}
**Screenshots Captured**: {screenshot_count}

### Issues Found:
**🚨 Blockers** ({blocker_count}):
- {critical_issue_list}

**⚠️ High-Priority** ({high_count}):
- {high_priority_list}

**📝 Medium-Priority** ({medium_count}):
- {medium_priority_list}

**💡 Nitpicks** ({nitpick_count}):
- {nitpick_list}

### Test Summary:
{test_summary_analysis}

---

## Next Steps
1. 📋 **Review test findings** above and address any blockers
2. 🔍 **Review implementation** in modified files
3. 🐛 **Fix high-priority issues** identified during testing
4. ✅ **Verify fixes** by running `/test_features` again
5. 📁 **Review plan**: `cat {PLAN_FILENAME}`
6. 💾 **Commit changes** if satisfied

---

📋 **Full Plan**: `{PLAN_FILENAME}`
✅ **Implementation**: Complete
🧪 **Testing**: Complete
🚀 **Ready for {next_action}**
```

## Critical Reminders

- ✅ DO use SlashCommand tool to execute each command
- ✅ DO wait for each command to complete before proceeding
- ✅ DO pass results between stages as context
- ✅ DO update todos after each stage
- ✅ DO handle errors gracefully with fallback options
- ✅ DO run test stage even if build has minor issues
- ❌ DO NOT execute commands in parallel
- ❌ DO NOT skip stages (unless handling critical errors)
- ❌ DO NOT lose context between stages
- ❌ DO NOT skip testing unless build failed critically

## Variable Passing Example

```
User Input: "Add user authentication with OAuth2" (scale: 3) (url: http://localhost:3000)

Stage 1 - Scout:
  Input: "Add user authentication with OAuth2", scale=3
  Output: Files found → [auth.service.ts, user.model.ts, oauth.config.ts]

Stage 2 - Plan:
  Input: Feature="Add user authentication with OAuth2"
  Context: Scout found auth.service.ts, user.model.ts, oauth.config.ts
  Output: Plan saved → plans/add-user-authentication-with-oauth2.md

Stage 3 - Build:
  Input: plans/add-user-authentication-with-oauth2.md
  Context: Plan includes scout findings, implementation steps
  Output: Files created/modified → [final implementation]

Stage 4 - Test:
  Input: Feature="Add user authentication with OAuth2", url=http://localhost:3000
  Context: Feature implemented, needs validation
  Output: Test report → 2 blockers, 3 high-priority issues, screenshots
```

## Usage Examples

```bash
# Basic workflow with default scout scale (2), no test URL
/scout_plan_build_test "Add user authentication with OAuth2"

# Workflow with custom scout scale and test URL
/scout_plan_build_test "Add payment processing" 4 http://localhost:3000/checkout

# Complex feature with deep scouting and specific page testing
/scout_plan_build_test "Implement real-time chat with WebSockets" 5 http://localhost:3000/chat

# Quick feature with minimal scouting and auto-discover URL
/scout_plan_build_test "Add logout button to header" 1

# Feature with documentation search (scale 5-6) and testing
/scout_plan_build_test "Stripe payment integration" 6 http://localhost:3000/payments
```

## Execution Timeline

| Stage | Command | Duration Estimate | Output |
|-------|---------|------------------|--------|
| Scout | `/scout` | 30s - 3min | File list with line ranges |
| Plan | `/plan` | 1-2min | Plan file (plans/*.md) |
| Build | `/build` | 2-5min | Implemented feature |
| Test | `/test_features` | 1-3min | Test report with screenshots |
| **Total** | | **5-13min** | **Complete & tested feature** |

## Benefits of This Workflow

1. **Context Window Efficiency**: Each stage uses separate agent contexts
2. **Proper Scoping**: Scout ensures relevant files are identified
3. **Structured Planning**: Codex creates comprehensive implementation plan
4. **Consistent Execution**: Build follows plan with medium reasoning
5. **Automated Testing**: Browser automation validates implementation
6. **Full Traceability**: Each stage is documented and tracked
7. **Error Recovery**: Graceful handling with fallback options
8. **Quality Assurance**: Testing catches issues before manual review
