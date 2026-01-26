# Curate Learnings

Summarize accumulated learnings into `project-dna.md` with two-threshold system:
- **Curation threshold** (default 5): Synthesize new entries into project-dna.md
- **Archive threshold** (default 50): Move all entries to archive, clear file

## Arguments

- `[curation-threshold]`: Minimum NEW learnings to trigger synthesis (default: 5)
- `[--archive-threshold N]`: When total entries >= N, archive and clear (default: 50)
- `[--force]`: Force curation regardless of threshold

---

## Step 1: Check for .ai-docs Directory

```bash
ls .ai-docs/learnings.jsonl
```

If not found: "No learnings file found. Run sessions that append learnings first." - STOP.

## Step 2: Read Curation State

Check for state file at `.ai-docs/curation-state.json`:

```json
{
  "last_curated_at": "2026-01-20T10:30:00Z",
  "last_curated_line": 35,
  "total_curated": 127,
  "curation_history": [
    {
      "date": "2026-01-15",
      "entries_processed": 12,
      "type": "curation"
    },
    {
      "date": "2026-01-20",
      "entries_processed": 50,
      "type": "archive",
      "archive_file": "learnings-20260120-103000.jsonl"
    }
  ]
}
```

If file doesn't exist, initialize with:
```json
{
  "last_curated_at": null,
  "last_curated_line": 0,
  "total_curated": 0,
  "curation_history": []
}
```

## Step 3: Count Entries

```powershell
# Count total lines and pending (uncurated) lines
$total = (Get-Content .ai-docs/learnings.jsonl -ErrorAction SilentlyContinue | Where-Object { $_.Trim() -ne '' } | Measure-Object).Count
$lastCurated = {LAST_CURATED_LINE}  # from state file
$pending = $total - $lastCurated

Write-Host "Total in file: $total"
Write-Host "Already curated: $lastCurated"
Write-Host "Pending curation: $pending"
```

## Step 4: Check Thresholds

### Curation Check
- If `pending < curation_threshold` AND not `--force`:
  - Output: "Only {pending} new learnings (threshold: {curation_threshold}). Use --force to curate anyway."
  - STOP

### Archive Check (after curation)
- If `total >= archive_threshold`:
  - Flag for archiving after synthesis

## Step 5: Read Pending Learnings

```powershell
# Read only uncurated entries (from last_curated_line+1 to end)
Get-Content .ai-docs/learnings.jsonl | Select-Object -Skip {LAST_CURATED_LINE}
```

Parse each JSON line and group by:
- **keywords** - Common themes
- **outcome** - success vs partial vs failed
- **files_touched** - Frequently modified files

## Step 6: Synthesize Insights

From the pending learnings, extract:

### Patterns
- What approaches consistently worked?
- What files are hot spots?
- What keywords cluster together?

### Anti-Patterns
- What led to partial/failed outcomes?
- What should be avoided?

### Project DNA Updates
- New conventions discovered
- New gotchas to document
- New file purposes identified

## Step 7: Update project-dna.md

Read existing `.ai-docs/project-dna.md` (or create if missing).

Append/merge new insights under appropriate sections:

```markdown
## Patterns (Updated {DATE})

### {Pattern Name}
- **Context**: When this applies
- **Approach**: What to do
- **Learned from**: Session {SESSION_ID}

## Anti-Patterns

### {Anti-Pattern Name}
- **Symptom**: What goes wrong
- **Root cause**: Why it fails
- **Alternative**: What to do instead

## Hot Files
Files frequently modified - pay extra attention:
- `path/to/file.ts` - {why it's touched often}

## Keywords → Files Mapping
Quick lookup for common tasks:
- **auth**: `src/auth/`, `middleware/auth.ts`
- **api**: `src/routes/`, `src/controllers/`
```

## Step 8: Update Curation State (No Archive)

If total < archive_threshold, just update the curated line:

```json
{
  "last_curated_at": "{CURRENT_ISO_TIMESTAMP}",
  "last_curated_line": {TOTAL_LINES},
  "total_curated": {PREVIOUS_TOTAL + PENDING_COUNT},
  "curation_history": [
    ...existing,
    {
      "date": "{TODAY}",
      "entries_processed": {PENDING_COUNT},
      "type": "curation"
    }
  ]
}
```

## Step 9: Archive (If Threshold Met)

If `total >= archive_threshold`:

```powershell
# Ensure archive directory exists
New-Item -ItemType Directory -Path '.ai-docs/archive' -Force | Out-Null

# Archive ALL entries
$archiveFile = ".ai-docs/archive/learnings-$(Get-Date -Format 'yyyyMMdd-HHmmss').jsonl"
Copy-Item .ai-docs/learnings.jsonl $archiveFile

# Clear learnings.jsonl
Set-Content .ai-docs/learnings.jsonl -Value $null

Write-Host "Archived $total entries to $archiveFile"
```

Update state with reset:

```json
{
  "last_curated_at": "{CURRENT_ISO_TIMESTAMP}",
  "last_curated_line": 0,
  "total_curated": {PREVIOUS_TOTAL + PENDING_COUNT},
  "curation_history": [
    ...existing,
    {
      "date": "{TODAY}",
      "entries_processed": {PENDING_COUNT},
      "type": "curation"
    },
    {
      "date": "{TODAY}",
      "entries_archived": {TOTAL_LINES},
      "type": "archive",
      "archive_file": "learnings-{TIMESTAMP}.jsonl"
    }
  ]
}
```

## Step 10: Output Summary

```markdown
## Curation Complete

**Processed**: {PENDING_COUNT} new learnings
**Updated**: project-dna.md
**Archived**: {YES/NO} ({TOTAL} entries → archive/learnings-{TIMESTAMP}.jsonl)

### Key Findings
- {Top 3 insights extracted}

### Stats
- Total learnings curated (all-time): {CUMULATIVE_TOTAL}
- Current file: {NEW_TOTAL} entries ({ARCHIVE_THRESHOLD - NEW_TOTAL} until next archive)
```

---

## Usage

```bash
/curate-learnings                    # Curate if 5+ pending, archive at 50
/curate-learnings 10                 # Curate if 10+ pending
/curate-learnings --archive-threshold 100   # Archive at 100 instead of 50
/curate-learnings --force            # Curate regardless of count
```

## Data Flow

```
Sessions append → learnings.jsonl (accumulates)
                       ↓
         ┌─────────────┴─────────────┐
         ↓                           ↓
    5+ pending?                  50+ total?
         ↓                           ↓
  Synthesize to               Archive to
  project-dna.md              archive/learnings-{ts}.jsonl
         ↓                           ↓
  Update last_curated_line    Clear file, reset line to 0
```

**Example lifecycle:**
```
Session 1: +3 entries  → total: 3,  pending: 3  (no curation)
Session 2: +4 entries  → total: 7,  pending: 7  (curate! pending→0, last_curated_line→7)
Session 3: +2 entries  → total: 9,  pending: 2  (no curation)
Session 4: +6 entries  → total: 15, pending: 8  (curate! pending→0, last_curated_line→15)
...
Session N: +5 entries  → total: 52, pending: 5  (curate + ARCHIVE! file cleared, line→0)
```

## State File

`.ai-docs/curation-state.json` tracks:
- `last_curated_line`: Which entries have been synthesized
- `total_curated`: All-time count
- `curation_history`: Log of curations and archives
