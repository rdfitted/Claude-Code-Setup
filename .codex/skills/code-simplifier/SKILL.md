---
name: code-simplifier
description: Simplify and refine code for clarity, consistency, and maintainability while preserving behavior; use after recent edits or when asked to clean up, refactor, or polish code.
---

# Code Simplifier

## Overview

Simplify recently modified code while preserving exact functionality and aligning with local standards.

## Principles

- Preserve functionality: do not change what the code does.
- Apply project standards from local guidance (CLAUDE.md, AGENTS.md, CODEX.md, CONTRIBUTING.md, style guides). If standards call for it, follow patterns such as:
  - Use ES modules with sorted imports and extensions.
  - Prefer the `function` keyword over arrow functions.
  - Use explicit return type annotations for top-level functions.
  - Follow React component patterns with explicit Props types.
  - Use proper error handling patterns (avoid try/catch when possible).
  - Maintain consistent naming conventions.
- Enhance clarity: reduce nesting, remove redundant code, improve naming, consolidate related logic, remove obvious comments, avoid nested ternaries; prefer switch or if/else chains for multiple conditions; choose clarity over brevity.
- Maintain balance: avoid over-simplifying, overly clever solutions, merging too many concerns, or removing helpful abstractions.
- Focus scope: refine only recently modified code unless explicitly asked to widen scope.

## Workflow

1. Identify recently modified sections or files.
2. Review for simplification opportunities and standard alignment.
3. Apply minimal, safe refactors and keep interfaces stable.
4. Verify behavior is unchanged; run tests if practical.
5. Report only significant readability changes.

## Notes

- Operate proactively after code changes.
- Leave code unchanged and explain why if a simplification risks behavior changes.
