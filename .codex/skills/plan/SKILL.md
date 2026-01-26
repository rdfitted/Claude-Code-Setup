---
name: plan
description: Produce an implementation plan and write it to a plan file; use when the user asks for a plan before coding.
---

# Plan

## Overview

Use CLI subagents to create a multi-perspective implementation plan, then synthesize into a single plan file under `plans/`.

## Inputs

- Feature description
- Optional constraints

## Workflow

1. Ensure `plans/` and `plans/context/` exist.
2. Run the planning subagent commands below.
3. Synthesize the best elements into one plan.
4. Save to `plans/<kebab-case-name>.md`.

## Planning Subagent Commands

### Codex (detailed plan)

```bash
codex exec -m gpt-5.2 -c model_reasoning_effort="high" -c thinking="enabled" --skip-git-repo-check \
  "Create a detailed implementation plan for: {FEATURE_DESC}. Include steps, files, and tests."
```

### Gemini (architecture and risks)

```bash
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} \
  gemini -m gemini-3-pro-preview -o text "Create a detailed plan for: {FEATURE_DESC}. Include architecture, steps, and risks."
```

### Claude (tradeoffs)

```bash
claude --model opus -p "Create a detailed plan for: {FEATURE_DESC}. Focus on tradeoffs, risks, and testing."
```

## Plan Template

```markdown
# {Feature Name}

## Overview

## Requirements

## Architecture

## Implementation Steps

## Testing Strategy

## Risks and Considerations
```

## Output

- Plan file path and a short synthesis summary
