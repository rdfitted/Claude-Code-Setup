---
name: build
description: Implement a feature or fix from a plan or short description; use when the user asks to build or implement.
---

# Build

## Overview

Use CLI subagents to draft implementation guidance, then apply changes in the working tree.

## Inputs

- Plan file path or feature description

## Workflow

1. Check git status and branch; if on main/master/staging, create a feature or fix branch.
2. Load the plan (if provided) or create a short checklist.
3. Run implementation subagents using the commands below.
4. Apply changes in the repo and add or update tests.
5. Run relevant tests or validation commands.
6. Summarize changes and current branch.

## Implementation Subagent Commands

### Codex (implementation draft)

```bash
codex exec -m gpt-5.2 -c model_reasoning_effort="medium" --skip-git-repo-check \
  "Implement this feature in the current repo. Use the plan if provided. Feature: {FEATURE_DESC}. Plan: {PLAN_TEXT}. Return a step-by-step change list with file paths."
```

### Gemini (review and risk scan)

```bash
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} \
  gemini -m gemini-3-pro-preview -o text "Review the implementation approach for: {FEATURE_DESC}. Identify risks and test gaps."
```

## Output

- Implementation summary, files changed, tests run
