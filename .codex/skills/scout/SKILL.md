---
name: scout
description: Search the codebase for relevant files and context; use when asked to locate files or understand where to work.
---

# Scout

## Overview

Use CLI subagents to find relevant files and optionally gather documentation.

## Inputs

- Search query
- Scale (1-6, default 2)

## Scale Map

- 1: Gemini Flash
- 2: + Gemini Lite
- 3: + Codex
- 4: + Claude Haiku
- 5: + 2x Gemini Flash doc scouts
- 6: + 2x Codex doc scouts

## Workflow

1. Parse query and scale.
2. Run the subagent commands for the chosen scale (parallel if possible).
3. Collect outputs, dedupe, and rank files by consensus.
4. If scale >= 5, save docs under `aidocs/` and `aidocs/context/`.

## Subagent Commands

### Gemini Flash (codebase)

```bash
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} \
  gemini -m gemini-3-flash-preview -o text "Search the codebase for files related to: {QUERY}. Return file paths with line ranges."
```

### Gemini Lite (codebase)

```bash
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} \
  gemini -m gemini-2.5-flash-lite -o text "Quickly identify files for: {QUERY}. List file paths with line ranges."
```

### Codex (codebase)

```bash
codex exec -m gpt-5.2 -s read-only -c model_reasoning_effort="low" --skip-git-repo-check \
  "Locate files for: {QUERY}. Output file paths with line numbers."
```

### Claude Haiku (codebase)

```bash
claude --model haiku -p "Find files for: {QUERY}. Return file paths with line ranges only."
```

### Gemini Flash (docs 1)

```bash
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} \
  gemini -m gemini-3-flash-preview -o text "Search the internet for official documentation related to: {QUERY}. Return URLs and short summaries."
```

### Gemini Flash (docs 2)

```bash
CLOUDSDK_CORE_PROJECT="" GOOGLE_CLOUD_PROJECT="" GCLOUD_PROJECT="" GEMINI_API_KEY=${GEMINI_API_KEY} \
  gemini -m gemini-3-flash-preview -o text "Find tutorials and best practices for: {QUERY}. Return URLs and short summaries."
```

### Codex (docs 1)

```bash
codex exec -m gpt-5.2 -c model_reasoning_effort="low" --skip-git-repo-check \
  "Search online docs for: {QUERY}. Return URLs and summaries."
```

### Codex (docs 2)

```bash
codex exec -m gpt-5.2 -c model_reasoning_effort="low" --skip-git-repo-check \
  "Find code examples and guides for: {QUERY}. Return URLs and summaries."
```

## Docs Saving (scale >= 5)

```bash
mkdir aidocs
mkdir aidocs\context
```

Save results to `aidocs/<query-slug>-docs.md` with URLs and key findings.

## Output

- Ranked file list with brief notes
- Optional docs summary file path
