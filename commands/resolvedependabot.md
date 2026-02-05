---
description: Resolve all Dependabot dependency updates with multi-agent conflict detection
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Edit, Write, Glob, Grep]
---

# Purpose

Systematically process all Dependabot dependency updates by spawning multiple verification agents (using different models) to detect conflicts between updates and the codebase, categorizing as SAFE or HAS_CONFLICTS, and implementing updates only after resolving conflicts.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (`gemini`, `codex`) via Bash for multi-model conflict detection diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive dependency conflict detection.

## ⛔ ANTI-BYPASS NOTICE ⛔

This workflow REQUIRES spawning subagents via the Task tool. You are NOT permitted to:
- Use Grep/Glob/Read to detect conflicts yourself
- Skip the multi-agent conflict detection step for "efficiency"
- Assume you already know whether an update is SAFE or HAS_CONFLICTS
- Replace subagent conflict detection with direct codebase searches

**WHY**: The multi-agent approach provides diverse model perspectives and preserves context. Your role is to ORCHESTRATE the agents, not replace them.

## Workflow

**CRITICAL WORKFLOW REQUIREMENTS**:
1. Run the workflow in order, top to bottom
2. Do not stop in between steps
3. Complete every step before stopping
4. **Step 2 (Subagent Conflict Detection) is MANDATORY** - you MUST spawn Task agents, never detect conflicts directly yourself

**VALIDATION CHECKPOINT**: Before proceeding to Step 3, confirm you have spawned at least 3 Task agents. If you have not used the Task tool to spawn conflict detection agents, STOP and go back to Step 2.

### Step 1: Get Dependabot Alerts and PRs
```
# Get all open Dependabot PRs
gh pr list --author "app/dependabot" --json number,title,headRefName,url --state open

# Get Dependabot security alerts
gh api /repos/{owner}/{repo}/dependabot/alerts --jq '.[] | select(.state == "open")'

Extract key dependency updates from each PR/alert in memory (no files needed).
Store: package name, current version, target version, update type (major/minor/patch)
```

### Step 2: Spawn Conflict Detection Agents in Parallel

**⛔ MANDATORY - NO EXCEPTIONS ⛔**

You MUST spawn conflict detection subagents. DO NOT:
- Skip this step
- Perform conflict detection yourself instead of spawning agents
- Decide that agents are unnecessary
- Search the codebase directly without agents

REQUIRED ACTIONS:
1. For EVERY dependency update, spawn exactly 3 agents (one per model)
2. Launch ALL agents in parallel using a SINGLE message with multiple Task tool calls
3. WAIT for all agent results before proceeding to Step 3

Example: If 5 Dependabot updates, spawn 15 agents total (5 updates × 3 agents each).

FAILURE TO SPAWN AGENTS IS A WORKFLOW VIOLATION.

**Agent 1 - Gemini Flash (Changelog Analysis):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a conflict detection agent using Gemini Flash.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

CLOUDSDK_CORE_PROJECT=\"\" GOOGLE_CLOUD_PROJECT=\"\" GCLOUD_PROJECT=\"\" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-flash-preview -o text \"Analyze potential breaking changes for: {PACKAGE_NAME} upgrade from {OLD_VERSION} to {NEW_VERSION}. Search the codebase for: import statements, API calls, type definitions, configuration files. Report files using this dependency, potential breaking changes, and risk level (LOW/MEDIUM/HIGH).\"

Report back:
- Files using this dependency and HOW they use it
- Potential breaking changes based on version diff
- API methods that may have changed
- Risk level: LOW (patch), MEDIUM (minor), HIGH (major with breaking changes)

Format: Bullet list of file paths with usage patterns and risk assessment."
)
```

**Agent 2 - Codex (Usage Pattern Analysis):**
```
Task(
  subagent_type="general-purpose",
  prompt="You are a conflict detection agent using OpenAI Codex.

IMMEDIATELY use the Bash tool to run this EXACT command (10 minute timeout):

codex exec -m 5.2-codex -s read-only -c model_reasoning_effort=\"low\" --skip-git-repo-check \"Find all code using {PACKAGE_NAME} and check compatibility with {NEW_VERSION}. Search for import statements, API calls, type definitions, configuration files. Report usage patterns and potential breaking changes.\"

Report back:
- Files using this dependency and HOW they use it
- Potential breaking changes based on version diff
- API methods that may have changed
- Risk level: LOW (patch), MEDIUM (minor), HIGH (major with breaking changes)

Format: Bullet list of file paths with usage patterns and risk assessment."
)
```

**Agent 3 - Claude Haiku (API Verification):**
```
Task(
  subagent_type="Explore",
  model="haiku",
  prompt="Verify API compatibility for {PACKAGE_NAME} upgrade from {OLD_VERSION} to {NEW_VERSION}. Search for: Import statements, API calls, type definitions, configuration files. Report: Files using this dependency, potential breaking changes, risk level (LOW/MEDIUM/HIGH)."
)
```

**Example agent spawning for multiple updates:**
Launch ALL agents in PARALLEL using a SINGLE message with multiple Task tool calls:
```
Task(subagent_type="general-purpose", prompt="[Gemini Flash] Check conflicts: react 17.0.2 → 18.2.0...")
Task(subagent_type="general-purpose", prompt="[Codex] Check conflicts: react 17.0.2 → 18.2.0...")
Task(subagent_type="Explore", model="haiku", prompt="Check conflicts: react 17.0.2 → 18.2.0")
Task(subagent_type="general-purpose", prompt="[Gemini Flash] Check conflicts: axios 0.27.2 → 1.6.0...")
Task(subagent_type="general-purpose", prompt="[Codex] Check conflicts: axios 0.27.2 → 1.6.0...")
Task(subagent_type="Explore", model="haiku", prompt="Check conflicts: axios 0.27.2 → 1.6.0")
```
(continue for all updates × 3 agents each)

Collect all agent results.
```

### Step 3: Categorize Updates Using Agent Results
```
For each dependency update, review results from its 3 conflict detection agents:

Consensus logic:
- 3/3 agents agree "no conflicts" → ✅ SAFE (high confidence)
- 2/3 agents agree "no conflicts" → ✅ SAFE (medium confidence)
- 3/3 agents found breaking changes → ❌ HAS_CONFLICTS (high confidence)
- 2/3 agents found breaking changes → ❌ HAS_CONFLICTS (medium confidence)
- 1/1 split → ⚠️ NEEDS_REVIEW (check manually)

For SAFE updates, note for automatic implementation.
For HAS_CONFLICTS, create detailed conflict resolution plan.

Store categorized update lists.
```

### Step 4: Establish Baseline (Pre-Update State)
```
**CRITICAL**: Before making ANY changes, establish baseline to distinguish pre-existing issues from update-caused issues.

Checkout main branch and capture baseline metrics:
git stash  # Save any uncommitted changes
git checkout main

Run verification suite on main branch:
# Frontend/Node.js projects
cd frontend && npm run lint 2>&1 | tee baseline_lint.txt
cd frontend && npx tsc --noEmit 2>&1 | tee baseline_typecheck.txt
cd frontend && npm test -- --run 2>&1 | tee baseline_test.txt
cd frontend && npm run build 2>&1 | tee baseline_build.txt

# Python projects
pylint . > baseline_lint.txt 2>&1
mypy . > baseline_typecheck.txt 2>&1
pytest > baseline_test.txt 2>&1

# Ruby projects
rubocop > baseline_lint.txt 2>&1
bundle exec rspec > baseline_test.txt 2>&1

Store baseline counts:
- Linting errors/warnings (count)
- Type errors (count)
- Test failures (count)
- Build status (pass/fail)

Return to dependency branch:
git checkout {dependabot_branch}
git stash pop  # Restore changes if any

Store baseline results for comparison.
```

### Step 5: Create Implementation Plan
```
Use TodoWrite to create tasks:

For SAFE updates:
- Establish baseline metrics
- Update dependency in package.json/requirements.txt/etc
- Install dependencies
- Run verification suite (lint, typecheck, test, build)
- Compare results with baseline
- Fix any NEW issues introduced by update
- Merge Dependabot PR or update manually

For HAS_CONFLICTS:
- Establish baseline metrics
- List specific files requiring changes
- Detail API changes needed
- Update code to match new API
- Fix configuration issues (ESLint, TypeScript, etc)
- Update tests
- Run verification suite
- Compare results with baseline
- Fix any NEW issues
- Run full test suite

Store implementation plan.
```

### Step 6: Implement All Updates
```
Process SAFE updates first:
- Update package manager files (package.json, requirements.txt, etc)
- Run package install command:
  - npm install (Node.js)
  - pip install -r requirements.txt (Python)
  - bundle install (Ruby)
- Mark todo completed

Then process HAS_CONFLICTS:
- Read files identified by agents
- Make necessary API changes
- Update deprecated method calls
- Fix configuration issues (like ESLint extends syntax)
- Fix type errors
- Mark todos completed

Collect all changes made.
```

### Step 7: Comprehensive Verification
```
Run full verification suite on updated dependencies:

**Frontend/Node.js:**
1. Linting
   cd frontend && npm run lint 2>&1 | tee updated_lint.txt
   - If linting fails, check for config issues (ESLint extends, parser, plugins)
   - Fix config issues (e.g., "plugin:@typescript-eslint/recommended" not "@typescript-eslint/recommended")
   - Remove invalid rules (e.g., non-existent @typescript-eslint rules)

2. Type Checking
   cd frontend && npx tsc --noEmit 2>&1 | tee updated_typecheck.txt
   - Count type errors
   - Identify files with errors

3. Tests
   cd frontend && npm test -- --run 2>&1 | tee updated_test.txt
   - Note test failures
   - Check if Playwright/Vitest config conflicts exist

4. Build
   cd frontend && npm run build 2>&1 | tee updated_build.txt
   - Must succeed for merge approval

**Python:**
1. pylint . > updated_lint.txt 2>&1
2. mypy . > updated_typecheck.txt 2>&1
3. pytest > updated_test.txt 2>&1

**Ruby:**
1. rubocop > updated_lint.txt 2>&1
2. bundle exec rspec > updated_test.txt 2>&1

Store verification results.
```

### Step 8: Compare Baseline vs Updated
```
For each verification type (lint, typecheck, test, build):

Compare counts:
baseline_errors = count from baseline_{type}.txt
updated_errors = count from updated_{type}.txt
new_errors = updated_errors - baseline_errors

Categorize results:
- ✅ IMPROVED: new_errors < 0 (fewer errors than baseline)
- ✅ NO_REGRESSION: new_errors == 0 (same errors as baseline)
- ❌ REGRESSION: new_errors > 0 (more errors than baseline)

For REGRESSION cases:
- Extract new error messages not in baseline
- Fix new errors introduced by dependency update
- Re-run verification
- Repeat until NO_REGRESSION achieved

Store comparison results:
{
  "lint": {"baseline": X, "updated": Y, "new": Z, "status": "NO_REGRESSION"},
  "typecheck": {"baseline": X, "updated": Y, "new": Z, "status": "NO_REGRESSION"},
  "test": {"baseline": X, "updated": Y, "new": Z, "status": "IMPROVED"},
  "build": {"baseline": "pass", "updated": "pass", "status": "NO_REGRESSION"}
}
```

### Step 9: Commit and Push
```
Clean up temporary files:
rm -f dependabot_updates.json conflict_results.json
rm -f baseline_*.txt updated_*.txt

**ONLY commit if**:
- Build succeeds
- No regressions detected (or all regressions fixed)

Commit changes with descriptive message including:
- Dependencies updated
- Config fixes applied (if any)
- Verification status

Push to remote branch.

For Dependabot PRs that pass verification:
gh pr review {pr_number} --approve --body "✅ Verified: Build passing, no regressions detected"
gh pr merge {pr_number}

Generate final report.
```

## Agent Configuration

**Conflict Detection Agents (3 per dependency update):**
1. Gemini Flash - Fast changelog and release notes analysis
2. Codex - Deep codebase usage pattern analysis
3. Claude Haiku (Native Claude Code Subagent) - Quick API compatibility check via Explore

Each agent uses different model perspective to detect potential conflicts.

## Agentic Tool Commands

```bash
# Gemini Flash - Changelog analysis (with GCP project context cleared)
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} gemini -m gemini-3-flash-preview -o text "Find breaking changes for {package} {old_version} → {new_version}. Search codebase for usage patterns and potential conflicts."

# Codex - Usage pattern analysis
codex exec -m 5.2-codex -s read-only -c model_reasoning_effort="low" --skip-git-repo-check "Find all code using {package} and check compatibility with {new_version}. Report usage patterns and breaking changes."

# Claude Haiku (Native Claude Code Subagent) - API verification
Task(
  subagent_type="Explore",
  model="haiku",
  prompt="Verify API compatibility for {package} upgrade from {old_version} to {new_version}. Search for: Import statements, API calls, type definitions, configuration files. Report: Files using this dependency, potential breaking changes, risk level (LOW/MEDIUM/HIGH)."
)
```

## Why Multi-Agent Conflict Detection

- **Context isolation**: Each agent runs in separate context, preserving main context window
- **Model diversity**: Different models (Gemini, GPT, Claude) catch different types of conflicts
- **Parallel execution**: All dependencies checked simultaneously
- **Higher confidence**: Multiple models agreeing = higher confidence in safety assessment
- **Comprehensive analysis**: Changelog + usage patterns + API checks = complete picture

## Version Update Priority

Process in this order:
1. Security patches (CRITICAL)
2. Patch updates (x.x.X) - usually safe
3. Minor updates (x.X.0) - low risk
4. Major updates (X.0.0) - high risk, requires thorough testing

## Common Issues and Fixes

### ESLint Configuration Errors

**Issue**: `ESLint couldn't find the config "@typescript-eslint/recommended" to extend from`

**Cause**: Missing `plugin:` prefix in extends array

**Fix**:
```json
// Before (incorrect)
"extends": ["@typescript-eslint/recommended"]

// After (correct)
"extends": ["plugin:@typescript-eslint/recommended"]
```

**Issue**: `Definition for rule '@typescript-eslint/prefer-async-await' was not found`

**Cause**: Invalid or non-existent ESLint rule

**Fix**: Remove the invalid rule from `.eslintrc.json` rules section

### Dependency Installation Issues

**Issue**: `removed 51 packages` during npm install

**Cause**: Dependency tree optimization or peer dependency resolution

**Fix**:
1. Check if removed packages are still needed
2. Run `npm list {package}` to verify package is still installed via dependencies
3. If legitimately missing, run `npm install {package}` explicitly

**Issue**: `node_modules/@typescript-eslint/eslint-plugin: No such file or directory`

**Cause**: Package installed in different location or workspace structure

**Fix**:
1. Check root node_modules: `ls node_modules/@typescript-eslint/eslint-plugin`
2. If in workspace, check if package is hoisted to root
3. Run `npm install` from correct directory

### TypeScript Type Errors

**Issue**: Type errors after dependency update

**Process**:
1. Check if errors exist on main branch first
2. If pre-existing, document in report but don't fix in dependency PR
3. If new errors, check changelog for breaking changes
4. Update type imports/usage according to new API

**Common Breaking Changes**:
- `@ai-sdk` packages: API method signature changes
- React: Hook return type changes
- UI libraries: Prop type changes

### Test Configuration Conflicts

**Issue**: `Playwright` vs `Vitest` configuration conflict

**Symptom**: Tests fail with "Cannot find module" or initialization errors

**Fix**:
1. Separate test configurations
2. Update `vitest.config.ts` to exclude e2e tests
3. Update `playwright.config.ts` to only run e2e tests

### Deprecated Dependencies

**Issue**: Package shows as deprecated (e.g., `@types/xlsx`)

**Check**: Verify if main package now provides own types

**Fix**:
1. Test if types work without @types package
2. If yes, remove @types dependency
3. Document in follow-up tasks for separate PR

## Report Format

```markdown
# Dependabot PR #{number} Review Summary

## Dependency Updates ({count} packages)

### By Category:
**AI/ML Libraries:**
- {package}: {old} → {new} ({notable features/fixes})

**UI/Form Libraries:**
- {package}: {old} → {new} ({notable features/fixes})

**Build Tools:**
- {package}: {old} → {new} ({notable features/fixes})

**Types:**
- {package}: {old} → {new} ({notable features/fixes})

## Conflict Detection Summary
- Updates analyzed: {count}
- Verification agents spawned: {count * 3}
- ✅ SAFE (no conflicts): {count}
- ❌ HAS_CONFLICTS (resolved): {count}
- ⚠️ NEEDS_REVIEW (manual check needed): {count}

## Verification Results

### Baseline (main branch)
- Linting: {errors} errors, {warnings} warnings
- Type Checking: {errors} errors
- Tests: {passed}/{total} passed ({failed} failed)
- Build: {status}

### After Updates (dependency branch)
- Linting: {errors} errors, {warnings} warnings ({change} vs baseline)
- Type Checking: {errors} errors ({change} vs baseline)
- Tests: {passed}/{total} passed ({failed} failed) ({change} vs baseline)
- Build: {status} ({change} vs baseline)

### Comparison
- ✅ Build: Successful
- ✅ Linting: NO_REGRESSION ({pre-existing count} issues are pre-existing)
- ✅ Type Checking: NO_REGRESSION ({pre-existing count} errors are pre-existing)
- ✅ Tests: NO_REGRESSION ({pre-existing count} failures are pre-existing)

**All issues existed on main branch - NOT introduced by dependency updates.**

## Required Changes Made

### Configuration Fixes:
- {file}: {description of fix}
  Example: Added `plugin:` prefix for TypeScript extends
  Example: Removed invalid `@typescript-eslint/prefer-async-await` rule

### Code Updates (for HAS_CONFLICTS):
- {file}: {description of API change}
- {file}: {description of type fix}

## Merge Decision

{✅ Safe to Merge | ⚠️ Needs Review | ❌ Not Ready}

**Reasoning:**
- Dependencies update cleanly without breaking changes
- Build succeeds
- No test regressions
- All conflicts resolved

## Follow-up Tasks (Separate PRs)

Issues identified but NOT caused by dependency updates:
1. {Issue description} - affects {files}
2. Remove deprecated dependency: {package} ({reason})
3. Fix {count} pre-existing linting errors
4. Address {count} pre-existing TypeScript errors
5. Fix test configuration ({specific issue})

## Dependabot PRs
- ✅ Merged: {count}
- ⚠️ Remaining for review: {count}

## Status
✅ All safe updates applied
✅ All conflicts resolved
✅ Build passing
✅ No regressions detected
✅ Changes committed and pushed
```
