---
description: Initialize .ai-docs/ structure for Compound Engineering in current project
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Write, Read]
---

# Initialize Project DNA

Create the `.ai-docs/` directory structure for Compound Engineering in the current project.

## Workflow

### Step 1: Check if .ai-docs Already Exists

```bash
powershell -Command "if (Test-Path '.ai-docs') { Write-Host 'EXISTS' } else { Write-Host 'NOT_EXISTS' }"
```

**If EXISTS**: Ask user if they want to reset (this will clear learnings).

### Step 2: Create Directory Structure

```bash
powershell -Command "New-Item -ItemType Directory -Path '.ai-docs' -Force"
```

### Step 3: Create learnings.jsonl (Empty)

Write to `.ai-docs/learnings.jsonl`:
```
```
(Empty file - learnings will be appended by sessions)

### Step 3b: Create curation-state.json

Write to `.ai-docs/curation-state.json`:

```json
{
  "last_curated_at": null,
  "last_curated_line": 0,
  "total_curated": 0,
  "curation_history": []
}
```
(Tracks curation state across sessions - ensures accumulated learnings are properly curated)

### Step 3c: Create archive Directory

```bash
powershell -Command "New-Item -ItemType Directory -Path '.ai-docs/archive' -Force"
```
(For archived learnings after curation)

### Step 4: Create project-dna.md

Write to `.ai-docs/project-dna.md`:

```markdown
# Project DNA

How we do things in this project. Updated by AI sessions.

## Patterns That Work
<!-- Successful approaches discovered by sessions -->

## Patterns That Failed
<!-- Approaches that didn't work - avoid repeating -->

## Code Conventions
<!-- Project-specific conventions learned from codebase -->

## Architecture Notes
<!-- Key architectural patterns in this project -->

## Model Performance Notes
<!-- Which models worked best for this project's tasks -->

---
*Curated from learnings.jsonl by /curate-learnings skill*
*Last updated: (never)*
```

### Step 5: Create bug-patterns.md

Write to `.ai-docs/bug-patterns.md`:

```markdown
# Bug Patterns

Bugs fixed in this project and their patterns. Helps prevent regressions.

## Template

```
## BUG-YYYY-NNN: Short description
- **Symptom**: What the user saw
- **Root Cause**: Why it happened
- **Fix**: What was changed
- **Pattern**: Generalizable lesson
- **Keywords**: searchable, terms, here
- **Files**: affected-file.ts
```

## Bugs

<!-- Populated by /fix, /resolve* commands -->

---
*Search with: `grep -i "keyword" .ai-docs/bug-patterns.md`*
```

### Step 6: Output Confirmation

```markdown
## Project DNA Initialized

Created `.ai-docs/` with:
- `learnings.jsonl` - Append-only session learnings (empty)
- `curation-state.json` - Tracks curation progress across sessions
- `project-dna.md` - Curated patterns (template)
- `bug-patterns.md` - Bug fix patterns (template)
- `archive/` - Directory for archived learnings

### Next Steps

1. Run any command - hooks automatically capture learnings and inject context
2. Periodically run `/curate-learnings` to summarize into project-dna.md
3. Manually add to project-dna.md when you discover important patterns

### How It Works

**Pre-session**: `user_prompt_submit.py` hook greps `learnings.jsonl` for relevant history
**Post-session**: `learning_capture.py` hook appends new learnings

This compounds over time - AI gets better at this specific project.
```
