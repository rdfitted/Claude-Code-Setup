---
description: Build a feature using Codex agent - from plan file or quick feature description
argument-hint: [feature-description OR plan-file-path]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Glob, SlashCommand]
---

# Purpose

Execute feature implementation using a Claude Sonnet agent, either from an existing plan file or a quick feature description for rapid iteration. Preserves primary agent's context window while leveraging Sonnet's implementation capabilities.

**CRITICAL**: Always works on a feature/fix branch - NEVER commits directly to main/master/staging.

> **Note**: Branch protection is also enforced by the `PreToolUse` hook (`pre_tool_use.py`), which blocks Write/Edit on protected branches.

## Variables

- `{INPUT}`: User's input - either a feature description OR a path to a plan file
- `{INPUT_TYPE}`: Detected type - "plan_file" or "feature_description"
- `{PLAN_CONTENT}`: Loaded plan content (if plan_file) or feature description
- `{FEATURE_NAME}`: Extracted feature name for context
- `{CURRENT_BRANCH}`: Current git branch name
- `{NEW_BRANCH_NAME}`: Generated branch name for feature/fix (if needed)
- `{IS_PROTECTED_BRANCH}`: Boolean - true if on main/master/staging branch

## Instructions

**CRITICAL - Phase 0: Git Branch Safety Check (MUST RUN FIRST)**
1. Run `/gitinfo` slash command to get comprehensive git repository information
2. Check current branch name using `git branch --show-current`
3. **If on main, master, or staging branch**:
   - Extract feature/fix name from input
   - Generate branch name (e.g., "feature/add-login" or "fix/navigation-bug")
   - Create and checkout new branch: `git checkout -b {NEW_BRANCH_NAME}`
   - Report branch creation
4. **If already on a feature branch**: Continue with current branch
5. **IMPORTANT**: NEVER allow commits to main/master/staging - always work on feature/fix branches

**Phase 1: Parse Input and Load Context**
6. Parse user input to determine if it's a plan file path or feature description
7. **If plan file path**: Read the plan file content to understand implementation requirements
8. **If feature description**: Use description directly for quick iteration

**Phase 2: Implementation**
9. **CRITICAL**: Create comprehensive TODO list from plan/requirements using TodoWrite tool
10. Implement the feature directly using all available tools
11. **CRITICAL**: Mark each TODO as in_progress before working on it, then completed when done
12. **CRITICAL**: Continue working until ALL TODOs are completed - do not stop early
13. Create/modify files as needed following the plan or feature description

**Phase 3: Testing and Validation**
14. **CRITICAL**: Run tests to confirm the feature works correctly
15. Report implementation results and files modified/created
16. **REMINDER**: Changes are on branch `{BRANCH_NAME}` - NOT on main

## Workflow

### Step 0: Git Branch Safety Check (MUST RUN FIRST)

**CRITICAL**: This step MUST be completed before any implementation begins.

```bash
# 1. Run gitinfo slash command
Use SlashCommand tool: command="/gitinfo"

# 2. Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# 3. Check if on main/master/staging
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ] || [ "$CURRENT_BRANCH" = "staging" ]; then
  echo "⚠️ WARNING: Currently on $CURRENT_BRANCH branch!"
  echo "Creating new feature/fix branch..."

  # 4. Generate branch name from input
  # If input is a plan file, extract feature name from filename
  # If input is description, convert to kebab-case
  # Determine if it's a feature or fix based on keywords

  if [input contains "fix" or "bug"]; then
    BRANCH_PREFIX="fix"
  else
    BRANCH_PREFIX="feature"
  fi

  # Generate branch name: feature/add-login or fix/navigation-bug
  NEW_BRANCH="${BRANCH_PREFIX}/${FEATURE_NAME_KEBAB_CASE}"

  # 5. Create and checkout new branch
  git checkout -b "$NEW_BRANCH"

  echo "✅ Created and switched to branch: $NEW_BRANCH"
  WORKING_BRANCH="$NEW_BRANCH"
else
  echo "✅ Already on feature branch: $CURRENT_BRANCH"
  WORKING_BRANCH="$CURRENT_BRANCH"
fi

# 6. Check for remote repository
HAS_REMOTE=$(git remote -v | wc -l)
if [ $HAS_REMOTE -gt 0 ]; then
  echo "📡 Remote repository detected - branch protection active"
  echo "🚫 NEVER commit directly to main/master/staging"
else
  echo "📁 Local repository only - no remote"
fi

echo ""
echo "=== Ready to build on branch: $WORKING_BRANCH ==="
```

**Branch Name Generation Rules:**
- Plan file `plans/add-user-authentication.md` → `feature/add-user-authentication`
- Description `"Fix the login bug"` → `fix/login-bug`
- Description `"Add dark mode"` → `feature/add-dark-mode`
- Keywords `fix`, `bug`, `patch` → `fix/` prefix
- Everything else → `feature/` prefix

### Step 1: Detect Input Type
```
Check if input:
- Contains ".md" extension → plan_file
- Starts with "plans/" → plan_file
- Otherwise → feature_description
```

### Step 2: Load Plan Content (if applicable)
```
if input_type == "plan_file":
    Use Read tool to load plan file content
    Extract feature name from plan
    Parse implementation steps and requirements
else:
    Use feature description directly
    Set feature name from description
```

### Step 3: Create Comprehensive TODO List

**CRITICAL**: Use TodoWrite tool to create detailed TODO list

**For Plan File Input:**
- Parse plan implementation steps into individual TODOs
- Include file creation/modification tasks
- Add testing tasks
- Add validation tasks
- Each TODO should be specific and actionable

**For Feature Description:**
- Break down feature into implementation tasks
- Include analysis/discovery tasks
- Include file creation/modification tasks
- Add testing tasks
- Each TODO should be clear and measurable

**TODO Format**:
```json
[
  {
    "content": "Analyze existing authentication files",
    "activeForm": "Analyzing existing authentication files",
    "status": "pending"
  },
  {
    "content": "Create OAuth2 provider configuration",
    "activeForm": "Creating OAuth2 provider configuration",
    "status": "pending"
  },
  {
    "content": "Implement login endpoint",
    "activeForm": "Implementing login endpoint",
    "status": "pending"
  },
  {
    "content": "Write unit tests for auth service",
    "activeForm": "Writing unit tests for auth service",
    "status": "pending"
  },
  {
    "content": "Run tests to verify implementation",
    "activeForm": "Running tests to verify implementation",
    "status": "pending"
  }
]
```

### Step 4: Implement Feature with TODO Tracking

**CRITICAL WORKFLOW**:

1. **Before each task**: Mark TODO as in_progress
2. **Execute the task**: Use appropriate tools (Read, Write, Edit, Glob, Grep, Bash)
3. **After task completion**: Mark TODO as completed
4. **Continue**: Move to next TODO immediately
5. **Do NOT stop**: Keep working until ALL TODOs are completed

**For Plan File Input:**
1. Mark first TODO as in_progress
2. Follow implementation step from plan
3. Use Read/Glob/Grep to analyze relevant files
4. Use Write/Edit to create/modify files as specified
5. Mark TODO as completed
6. Repeat for all TODOs until complete

**For Feature Description (Quick Iteration):**
1. Mark first TODO as in_progress
2. Execute the task (analyze, implement, test, etc.)
3. Use appropriate tools for the task
4. Mark TODO as completed
5. Repeat for all TODOs until complete

### Step 5: Run Tests

**CRITICAL**: After implementation is complete, run tests to verify functionality

1. Mark "Run tests" TODO as in_progress
2. Identify appropriate test command:
   - `npm test` (Node.js/JavaScript)
   - `pytest` (Python)
   - `cargo test` (Rust)
   - `go test` (Go)
   - Or appropriate command for the project
3. Run test command using Bash tool
4. Analyze test results
5. If tests fail:
   - Create new TODOs to fix failing tests
   - Continue until all tests pass
6. Mark "Run tests" TODO as completed

### Step 6: Final Validation

Before reporting complete:
- ✅ All TODOs marked as completed
- ✅ Tests run successfully
- ✅ All files created/modified
- ✅ Feature fully functional

### Step 7: Report Results
- List all files created/modified with descriptions
- Summarize implementation approach
- Report test results
- Note any deviations from plan (if applicable)
- Report any issues or assumptions made

## Report Format

### For Plan-Based Implementation:
```markdown
# Feature Implemented: {FEATURE_NAME}
**Source**: Plan file `{PLAN_FILE_PATH}`
**Agent**: Claude Sonnet (plan-guided)
**Branch**: `{WORKING_BRANCH}` {if new branch: "✨ (newly created)" else: "(existing)"}

## Git Branch Information
- **Working Branch**: `{WORKING_BRANCH}`
- **Created New Branch**: {YES/NO}
- **Protected branch safe**: ✅ Changes NOT on main/master/staging
- **Remote Repository**: {YES/NO}

## TODOs Completed
✅ All {TODO_COUNT} tasks completed

## Files Modified/Created
- `path/to/file1.ts` - [Brief description]
- `path/to/file2.tsx` - [Brief description]
- `path/to/file3.test.ts` - [Brief description]

## Implementation Summary
[Key changes and approach]

## Test Results
**Test Command**: `{TEST_COMMAND}`
**Status**: ✅ PASSED / ❌ FAILED
**Output**: [Test output summary]

## Deviations from Plan
[Any changes from original plan with rationale]

## Next Steps
1. ✅ Implementation complete on branch `{WORKING_BRANCH}`
2. ✅ Tests passed
3. Review changes if needed
4. Commit changes: `git add . && git commit -m "feat: {FEATURE_NAME}"`
5. Push to remote (if exists): `git push -u origin {WORKING_BRANCH}`
6. Create pull request to merge into main

---
✅ Implementation complete and tested on branch `{WORKING_BRANCH}`
🚫 Protected: No commits to main/master/staging
```

### For Quick Feature Implementation:
```markdown
# Feature Implemented: {FEATURE_NAME}
**Source**: Quick iteration (no plan)
**Agent**: Claude Sonnet (autonomous)
**Branch**: `{WORKING_BRANCH}` {if new branch: "✨ (newly created)" else: "(existing)"}

## Git Branch Information
- **Working Branch**: `{WORKING_BRANCH}`
- **Created New Branch**: {YES/NO}
- **Protected branch safe**: ✅ Changes NOT on main/master/staging
- **Remote Repository**: {YES/NO}

## TODOs Completed
✅ All {TODO_COUNT} tasks completed

## Files Modified/Created
- `path/to/file1.ts` - [Brief description]
- `path/to/file2.tsx` - [Brief description]

## Implementation Approach
[Explanation of approach taken]

## Test Results
**Test Command**: `{TEST_COMMAND}`
**Status**: ✅ PASSED / ❌ FAILED
**Output**: [Test output summary]

## Assumptions Made
[Any assumptions or decisions made during implementation]

## Next Steps
1. ✅ Implementation complete on branch `{WORKING_BRANCH}`
2. ✅ Tests passed
3. Review changes if needed
4. Consider creating a formal plan for similar complex features
5. Commit changes: `git add . && git commit -m "feat: {FEATURE_NAME}"`
6. Push to remote (if exists): `git push -u origin {WORKING_BRANCH}`
7. Create pull request to merge into main

---
✅ Quick implementation complete and tested on branch `{WORKING_BRANCH}`
🚫 Protected: No commits to main/master/staging
```

## Critical Reminders

**Git Branch Safety (MOST CRITICAL - RUN FIRST):**
- ✅ DO run `/gitinfo` slash command BEFORE starting implementation
- ✅ DO check current branch with `git branch --show-current`
- ✅ DO create new feature/fix branch if on main/master/staging
- ✅ DO generate appropriate branch name (feature/* or fix/*)
- ✅ DO verify remote repository existence
- ✅ DO include branch information in final report
- 🚫 NEVER EVER commit directly to main/master/staging branch
- 🚫 NEVER allow implementation to proceed on main/master/staging without creating new branch
- 🚫 NEVER skip the git branch safety check

**Implementation and Testing:**
- ✅ DO create comprehensive TODO list at the start using TodoWrite
- ✅ DO mark TODOs as in_progress before working on them
- ✅ DO mark TODOs as completed after finishing each task
- ✅ DO continue working until ALL TODOs are completed
- ✅ DO run tests to verify the implementation works
- ✅ DO detect input type (plan file vs. feature description)
- ✅ DO read plan file if provided
- ✅ DO implement the feature directly (you are the builder)
- ✅ DO use all available tools (Read, Write, Edit, Glob, Grep, Bash, SlashCommand)
- ✅ DO follow plan steps methodically if plan provided
- ✅ DO fix failing tests and continue until all tests pass
- ❌ DO NOT spawn sub-agents for implementation
- ❌ DO NOT skip important steps in the plan
- ❌ DO NOT stop before all TODOs are completed
- ❌ DO NOT skip running tests
- ❌ DO NOT skip git branch safety check

## Input Detection Examples

**Plan File Inputs** (will read file):
- `plans/user-authentication.md`
- `plans/payment-processing.md`
- `user-auth-plan.md`

**Feature Description Inputs** (quick iteration):
- `Add login button to homepage`
- `Fix the navigation menu alignment`
- `Implement dark mode toggle`
- `Create API endpoint for user profile`

## Usage Examples

### From Plan File:
```bash
/build plans/user-authentication.md
/build plans/payment-processing.md
```

### Quick Feature (No Plan):
```bash
/build "Add a logout button to the header"
/build "Fix the mobile navigation menu"
/build "Create a user profile API endpoint"
/build "Implement search functionality"
```

## Implementation Strategy

| Input Type | Approach | Process |
|------------|----------|---------|
| Plan file | Follow plan steps | **Git Safety Check** → Read plan → Follow implementation steps → Create/modify files → Report |
| Feature description | Autonomous implementation | **Git Safety Check** → Analyze request → Scout codebase → Determine approach → Implement → Report |

This ensures quality implementation whether working from a detailed plan or quick feature request.

## Git Branch Safety Workflow (Detailed)

### Why This Matters

**CRITICAL**: Never commit directly to main/master/staging. This:
- ✅ Prevents breaking production code
- ✅ Enables code review via pull requests
- ✅ Maintains clean git history
- ✅ Allows easy rollback of changes
- ✅ Follows industry best practices

### Step-by-Step Branch Safety Process

**1. Run gitinfo to understand current state:**
```bash
/gitinfo
```

**2. Check current branch:**
```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"
```

**3. If on main/master/staging, create feature/fix branch:**
```bash
# Determine branch type from input
if [input contains "fix", "bug", "patch"]; then
  PREFIX="fix"
else
  PREFIX="feature"
fi

# Generate branch name
# From plan file: plans/add-user-auth.md → feature/add-user-auth
# From description: "Fix login bug" → fix/login-bug
BRANCH_NAME="${PREFIX}/${FEATURE_NAME_KEBAB_CASE}"

# Create and checkout new branch
git checkout -b "$BRANCH_NAME"
echo "✅ Created new branch: $BRANCH_NAME"
```

**4. Proceed with implementation on safe branch**

### Example Scenarios

#### Scenario 1: Starting on main branch with plan file
```bash
# User runs:
/build plans/add-stripe-payments.md

# Build command does:
1. Runs /gitinfo → Shows currently on "main"
2. Detects main branch → ⚠️ WARNING
3. Extracts "add-stripe-payments" from filename
4. Creates branch: git checkout -b feature/add-stripe-payments
5. ✅ Safe to proceed on feature/add-stripe-payments
6. Implements feature
7. Reports: "Changes on branch feature/add-stripe-payments"
```

#### Scenario 2: Starting on main with quick feature
```bash
# User runs:
/build "Fix the navigation menu bug"

# Build command does:
1. Runs /gitinfo → Shows currently on "main"
2. Detects main branch → ⚠️ WARNING
3. Detects "Fix" and "bug" keywords
4. Converts to kebab-case: "navigation-menu-bug"
5. Creates branch: git checkout -b fix/navigation-menu-bug
6. ✅ Safe to proceed on fix/navigation-menu-bug
7. Implements fix
8. Reports: "Changes on branch fix/navigation-menu-bug"
```

#### Scenario 3: Already on feature branch
```bash
# User runs:
/build "Add dark mode toggle"

# Build command does:
1. Runs /gitinfo → Shows currently on "feature/ui-improvements"
2. Detects feature branch → ✅ Already safe
3. Reports: "Proceeding on existing branch: feature/ui-improvements"
4. Implements feature
5. Reports: "Changes on branch feature/ui-improvements"
```

#### Scenario 4: Starting on staging branch
```bash
# User runs:
/build "Add email notification feature"

# Build command does:
1. Runs /gitinfo → Shows currently on "staging"
2. Detects staging branch → ⚠️ WARNING
3. Detects feature request (no fix/bug keywords)
4. Converts to kebab-case: "add-email-notification-feature"
5. Creates branch: git checkout -b feature/add-email-notification-feature
6. ✅ Safe to proceed on feature/add-email-notification-feature
7. Implements feature
8. Reports: "Changes on branch feature/add-email-notification-feature"
```

#### Scenario 5: Repository with remote
```bash
# User runs:
/build plans/add-api-endpoint.md

# Build command does:
1. Runs /gitinfo → Shows remote repository exists
2. Detects main branch → Creates feature/add-api-endpoint
3. Implements feature
4. Reports next steps include:
   - Commit changes
   - Push to remote: git push -u origin feature/add-api-endpoint
   - Create pull request
```

### Branch Naming Conventions

**Feature branches:**
- `feature/add-login` - Adding new login functionality
- `feature/dark-mode` - Adding dark mode
- `feature/stripe-integration` - Integrating Stripe
- `feature/user-dashboard` - Creating user dashboard

**Fix branches:**
- `fix/login-bug` - Fixing login bug
- `fix/navigation` - Fixing navigation issues
- `fix/memory-leak` - Fixing memory leak
- `fix/validation-error` - Fixing validation error

**Generated from plan files:**
- `plans/add-user-authentication.md` → `feature/add-user-authentication`
- `plans/fix-payment-bug.md` → `fix/payment-bug`

**Generated from descriptions:**
- "Add OAuth2 login" → `feature/add-oauth2-login`
- "Fix the header styling" → `fix/header-styling`
- "Implement search" → `feature/implement-search`

### Protection Guarantees

**This build command GUARANTEES:**
1. 🚫 Will NEVER commit to main/master/staging
2. ✅ Will ALWAYS create a feature/fix branch if on main/master/staging
3. ✅ Will ALWAYS run `/gitinfo` first to check status
4. ✅ Will ALWAYS report which branch changes were made on
5. ✅ Will ALWAYS include branch info in final report
6. ✅ Will ALWAYS detect remote repositories
7. ✅ Will ALWAYS guide user to proper PR workflow

**If you're on main/master/staging, the command will:**
- Refuse to proceed until new branch is created
- Automatically create appropriate branch
- Report branch creation clearly
- Ensure all commits go to the new branch

This protection prevents accidental commits to protected branches (main/master/staging) and enforces DevOps best practices for all implementations.
