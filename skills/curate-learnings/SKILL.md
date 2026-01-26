# Curate Learnings

Periodically curate and summarize learnings from `.ai-docs/learnings.jsonl` into `project-dna.md` and `bug-patterns.md`.

## When to Use

- **Auto-triggered**: Called inline by `/fix`, `/fix-hive`, and other learning commands when threshold (5+) is met
- When `learnings.jsonl` has grown large (20+ entries)
- After major project milestones
- When you notice repeated patterns in learnings
- Periodically (weekly/monthly) for active projects

## Invocation

This skill is typically invoked **inline** by other commands (not directly by user):
- `/fix` → Step 9 auto-curates if 5+ learnings
- `/fix-hive` → Queen auto-curates in Phase 4 if 5+ learnings
- `/hive` → Queen curates in Phase 4

Can also be invoked directly: `/curate-learnings`

## What This Skill Does

1. **Reads** `learnings.jsonl` (all entries)
2. **Groups** entries by keywords and themes
3. **Identifies** top patterns (frequency + recency weighted)
4. **Updates** `project-dna.md` with curated insights
5. **Updates** `bug-patterns.md` with bug → fix patterns
6. **Optionally archives** old entries to `learnings-archive.jsonl`

## Workflow

### Step 1: Check Prerequisites

```bash
# Verify .ai-docs exists
powershell -Command "if (Test-Path '.ai-docs/learnings.jsonl') { Write-Host 'READY' } else { Write-Host 'NO_LEARNINGS' }"
```

If `NO_LEARNINGS`: Tell user to run `/init-project-dna` or use `/fix` commands first.

### Step 2: Count Entries

```bash
powershell -Command "(Get-Content '.ai-docs/learnings.jsonl' | Measure-Object -Line).Lines"
```

Report count to user. **If < 5 entries, STOP and output**: "Only {N} learnings recorded. Curation requires 5+ entries."

### Step 3: Extract and Analyze Learnings

Read `.ai-docs/learnings.jsonl` and analyze:

```bash
# Get all learnings
cat .ai-docs/learnings.jsonl
```

For each entry, extract:
- `keywords` - for grouping
- `insight` - the actual learning
- `outcome` - success/partial/failed
- `date` - for recency weighting

### Step 4: Group by Theme

Group learnings into categories:
- **Authentication & Security**
- **Error Handling**
- **Testing**
- **Performance**
- **UI/Frontend**
- **Backend/API**
- **Database**
- **Integration**
- **Other**

### Step 5: Identify Top Patterns

Score patterns by:
- **Frequency**: How often similar insights appear
- **Recency**: Recent insights weighted higher
- **Outcome**: Successful patterns prioritized

Select top 10-15 patterns for curation.

### Step 5b: Analyze Hot Spots (Frequently Modified Files)

Extract `files_touched` from all entries and count frequency:

```powershell
# Count file modification frequency
$learnings = Get-Content '.ai-docs/learnings.jsonl' | ForEach-Object { $_ | ConvertFrom-Json }
$fileFreq = @{}
$learnings | ForEach-Object {
  $_.files_touched | ForEach-Object {
    if ($_) { $fileFreq[$_] = ($fileFreq[$_] ?? 0) + 1 }
  }
}
$fileFreq.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10
```

Identify:
- **High-churn files**: Modified in 3+ sessions (likely complex or problematic)
- **Stable files**: Rarely touched (well-designed or unused)
- **Correlation**: Files often modified together

### Step 5c: Build Keyword Clusters

Group related keywords that appear together:

```powershell
# Extract keyword co-occurrence
$learnings = Get-Content '.ai-docs/learnings.jsonl' | ForEach-Object { $_ | ConvertFrom-Json }
$keywordSets = $learnings | ForEach-Object { $_.keywords -join ',' }
# Analyze which keywords frequently appear together
```

Create clusters like:
- **Auth cluster**: auth, token, session, login, jwt
- **API cluster**: endpoint, request, response, error, status
- **UI cluster**: component, render, state, props, style

### Step 6: Update project-dna.md

Read current `project-dna.md` and **regenerate** with this structure:

```markdown
# Project DNA

*Last curated: {YYYY-MM-DD}*
*Based on: {N} session learnings*

## Core Patterns

### What Works
- {Pattern 1} - Used in {N} sessions with success
- {Pattern 2} - Consistent positive outcomes

### What Doesn't Work
- {Anti-pattern 1} - Failed in {N} sessions
- {Anti-pattern 2} - Partial success, better alternatives exist

## Hot Spots (Frequently Modified Files)

| File | Touch Count | Common Reason |
|------|-------------|---------------|
| {file1} | {N} | {reason from insights} |
| {file2} | {N} | {reason} |

*Files touched 3+ times may need refactoring or better abstractions.*

## Keyword Clusters

| Cluster | Keywords | Sessions |
|---------|----------|----------|
| {cluster1} | {kw1, kw2, kw3} | {N} |
| {cluster2} | {kw1, kw2} | {N} |

## Session Insights (Deduplicated)

{Merged, unique insights from all sessions - remove duplicates, combine similar}

## Model Performance Notes

- {model}: {what it's good at in this project}

## Curated Guidelines

Based on the above patterns, future sessions should:

1. {Guideline derived from success patterns}
2. {Guideline to avoid anti-patterns}
3. {Guideline for hot spot files}

---
*Curated from {N} sessions spanning {date_range}*
```

**IMPORTANT**: Regenerate the entire file each curation (don't just append). This keeps it clean and deduplicated.

### Step 6b: Update bug-patterns.md

Identify entries related to bugs (look for keywords like: bug, fix, error, issue, crash, failure, broken).

Read current `bug-patterns.md` (or create if missing):

```bash
# Check if bug-patterns.md exists
powershell -Command "if (Test-Path '.ai-docs/bug-patterns.md') { Get-Content '.ai-docs/bug-patterns.md' } else { Write-Host 'FILE_MISSING' }"
```

If missing, create with template:

```markdown
# Bug Patterns

Common bug patterns and their fixes for this project.

## Pattern Template

| Bug Type | Symptom | Root Cause | Fix Pattern |
|----------|---------|------------|-------------|

## Patterns

### [Category]

**Bug**: [description]
**Symptom**: [how it manifests]
**Root Cause**: [why it happens]
**Fix**: [how to fix]
**Learned**: [session_id, date]

---

*Last updated: YYYY-MM-DD*
```

Add new bug patterns from learnings:
- Extract entries where `outcome` = "failed" initially then "success"
- Extract entries with bug-related keywords
- Format as: Bug → Symptom → Root Cause → Fix Pattern

Update "Last updated" timestamp.

### Step 7: Optional - Archive Old Entries

If user confirms, move entries older than 30 days to `learnings-archive.jsonl`:

```bash
# Archive entries (keep recent 30 days in main file)
powershell -Command "
$cutoff = (Get-Date).AddDays(-30).ToString('yyyy-MM-dd')
$all = Get-Content '.ai-docs/learnings.jsonl' | ForEach-Object {
  $obj = $_ | ConvertFrom-Json
  [PSCustomObject]@{Line=$_; Date=$obj.date}
}
$old = $all | Where-Object { $_.Date -lt $cutoff }
$recent = $all | Where-Object { $_.Date -ge $cutoff }
if ($old) { $old.Line | Add-Content '.ai-docs/learnings-archive.jsonl' }
$recent.Line | Set-Content '.ai-docs/learnings.jsonl'
Write-Host \"Archived $($old.Count) entries, kept $($recent.Count) recent entries\"
"
```

### Step 8: Output Summary

```markdown
## Learnings Curated

**Entries Processed**: {count}
**Date Range**: {oldest} to {newest}
**Themes Identified**: {theme_count}

### Analysis Results

| Metric | Count |
|--------|-------|
| Patterns (success) | {N} |
| Anti-patterns (failed) | {N} |
| Hot spot files | {N} |
| Keyword clusters | {N} |

### Top Hot Spots

| File | Touches | Action Needed |
|------|---------|---------------|
| {file1} | {N} | {suggestion} |
| {file2} | {N} | {suggestion} |

### Keyword Clusters Found

- **{cluster1}**: {keywords} ({N} sessions)
- **{cluster2}**: {keywords} ({N} sessions)

### Files Updated

| File | Status |
|------|--------|
| `project-dna.md` | Regenerated |
| `bug-patterns.md` | {Updated / Created / Unchanged} |
| `learnings-archive.jsonl` | {N entries archived / Skipped} |

### Curated Guidelines Generated

1. {guideline1}
2. {guideline2}
3. {guideline3}

### Next Curation
Auto-triggers when learnings.jsonl reaches 5+ new entries after this curation.
```

## Usage

```bash
# Direct invocation (rare - usually auto-triggered)
/curate-learnings

# Auto-triggered by:
# - /fix (Step 9, if 5+ learnings)
# - /fix-hive (Queen Phase 4, if 5+ learnings)
# - /hive (Queen Phase 4)
```

## Tips

- **Usually auto-triggered**: You rarely need to run this manually
- **Threshold is 5**: Curation runs when 5+ learnings accumulated
- **Review before archiving**: Make sure important learnings are in DNA first
- **Keywords matter**: Good keywords in learnings = better curation grouping
- **Hot spots reveal problems**: Files touched 3+ times may need refactoring
- **Manual edits OK**: Feel free to manually edit project-dna.md for clarity

## Files Affected

| File | Action |
|------|--------|
| `.ai-docs/learnings.jsonl` | Read, optionally trim |
| `.ai-docs/project-dna.md` | Updated with patterns |
| `.ai-docs/bug-patterns.md` | Updated with bug → fix patterns |
| `.ai-docs/learnings-archive.jsonl` | Created if archiving |
