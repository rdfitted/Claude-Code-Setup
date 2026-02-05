# Claude Code Configuration

## Thread Types Framework

Use the appropriate thread type based on task complexity and requirements:

| Type | Pattern | When to Use | Commands |
|------|---------|-------------|----------|
| **Base** | 1 agent, 1 task | Simple tasks, quick queries | Direct execution |
| **P-Thread** | Parallel agents | Scale throughput, independent subtasks | `/scout`, `/plan` |
| **C-Thread** | Chained phases | Sequential workflows, build pipelines | `/scout_plan_build_test` |
| **L-Thread** | Long-running | Extended autonomous work | `/resolve*` commands |

> **Note**: Hive, swarm, and fusion commands have been migrated to `D:\Code Projects\hive-manager`.

## Paths

| Item | Location |
|------|----------|
| API Keys | `C:\Users\USERNAME\env` |
| Settings | `C:\Users\USERNAME\.claude\settings.json` |
| MCP Config | `C:\Users\USERNAME\.mcp.json` |
| Commands | `C:\Users\USERNAME\.claude\commands\` |
| Skills | `C:\Users\USERNAME\.claude\skills\` |
| Hooks | `C:\Users\USERNAME\.claude\hooks\` |
| Hook Logs | `C:\Users\USERNAME\.claude\hooks\logs\` |
| Global Learnings | `C:\Users\USERNAME\.ai-docs\` |

## Project Locations

Coding projects are stored in these directories:
- `C:\Users\USERNAME\Code Projects\`
- `D:\Code Projects\`

## AI Documentation Folder

Projects may have an `.ai-docs/` folder at the root for persistent AI-generated documentation.

| File | Purpose |
|------|---------|
| `.ai-docs/architecture.md` | AI-analyzed architecture overview |
| `.ai-docs/file-index.md` | Key files and their purposes |
| `.ai-docs/decisions.md` | Architectural decisions and rationale |

## Hook Infrastructure

Programmatic hooks enforce safety, track state, and inject context automatically.

| Hook | Event | Purpose | Exit Code |
|------|-------|---------|-----------|
| `pre_tool_use.py` | PreToolUse | Branch protection, destructive blocking, .env protection, audit log | 0=allow, 2=block |
| `post_tool_use.py` | PostToolUse | File tracker, tool counter, session warnings | Always 0 |
| `user_prompt_submit.py` | UserPromptSubmit | Auto-inject learnings, project DNA, universal patterns | Always 0 |
| `learning_capture.py` | Stop | Capture session learnings to `.ai-docs/learnings.jsonl` | Always 0 |
| `validate_file_contains.py` | Stop (per-command) | Validate output files contain required sections | 0=pass, 1=retry |
| `run-checks.py` | PreToolUse (git commit) | Pre-commit lint/type/secret checks | 0=pass |
| `stop-hook.ps1` | Stop | Ralph loop for `/resolvegitissue` | 0=done, 1=continue |

**Design**: All hooks fail open (exit 0 on error) to avoid blocking Claude. Security hooks (`pre_tool_use.py`) exit 2 to block dangerous operations.

## Compound Engineering (Learning System)

AI agents learn from past sessions to compound their effectiveness over time.

### File Structure

**Global** (`~/.ai-docs/`) - Cross-project patterns:
| File | Purpose |
|------|---------|
| `universal-patterns.md` | Auth, testing, error handling patterns |
| `model-insights.md` | What each AI model excels at |
| `workflow-learnings.md` | Which thread types work best |
| `stopwords.txt` | Keywords to filter when searching |

**Per-Project** (`.ai-docs/`) - Project-specific:
| File | Purpose |
|------|---------|
| `learnings.jsonl` | Append-only session learnings (one JSON per line) |
| `curation-state.json` | Tracks last curation line/timestamp for threshold logic |
| `project-dna.md` | Curated "how we do things here" |
| `bug-patterns.md` | Bug → fix patterns for this project |
| `archive/` | Archived learnings after curation |

### Learning Protocol

**Pre-Session** (automatic via `user_prompt_submit.py` hook):
- Extracts keywords from the user's prompt
- Greps `learnings.jsonl` for relevant past insights
- Reads `project-dna.md` for project patterns
- Greps `universal-patterns.md` for cross-project patterns
- Injects all context as `additionalContext` — no manual steps needed

**Post-Session** (automatic via `learning_capture.py` hook):
- Reads `session_files.jsonl` for files touched during session
- Generates learning entry with keywords and file list
- Appends to `.ai-docs/learnings.jsonl`
- Checks curation threshold and recommends `/curate-learnings` if needed

### Commands That Learn

All commands benefit from automatic hook-based learning:

| Command | Pre-Session | Post-Session |
|---------|-------------|--------------|
| All commands | `user_prompt_submit.py` auto-injects context | `learning_capture.py` auto-captures |
| `/fix` | Auto-injected | Auto-captured |
| `/fix-comment` | Auto-injected | Auto-captured |
| `/resolveprcomments` | Auto-injected | Auto-captured |
| `/resolvegitissue` | Auto-injected | Auto-captured |

### Bootstrap New Projects

Run `/init-project-dna` to create `.ai-docs/` structure in a new project.

### Curate Learnings

Run `/curate-learnings` to summarize accumulated learnings. Uses two thresholds:

| Threshold | Default | Action |
|-----------|---------|--------|
| Curation | 5 | Synthesize new entries → `project-dna.md` |
| Archive | 50 | Move all entries → `archive/`, clear file |

```bash
/curate-learnings                        # Curate at 5+, archive at 50+
/curate-learnings 10                     # Curate at 10+
/curate-learnings --archive-threshold 100  # Archive at 100+
/curate-learnings --force                # Curate regardless
```

**State Management** (`curation-state.json`):
- `last_curated_line` - Which entries have been synthesized
- `total_curated` - All-time count
- `curation_history` - Log of curations and archives

**Lifecycle example:**
```
+3 entries → total: 3  (no curation)
+4 entries → total: 7  (curate! synthesize 7, mark curated)
+6 entries → total: 13 (curate! synthesize 6 new)
...
+5 entries → total: 52 (curate + ARCHIVE! clear file)
```

## Git Workflow

**All PRs target `staging`, not `main`.**

```bash
gh pr create --base staging --title "feat: My feature"
```

## QuickBooks Queries

Always include WHERE clause:
```sql
SELECT * FROM Invoice WHERE Id > '0' MAXRESULTS 10
SELECT * FROM Invoice WHERE Balance > '0' MAXRESULTS 10
```

Entities: Invoice, Customer, Item, Vendor, Purchase, TimeActivity, Bill, Payment, Estimate

## LinkedIn Lead Generation

Endpoint: `https://api.apify.com/v2/acts/nFJndFXA5zjCTuudP/run-sync-get-dataset-items`

```json
{
  "queries": "[PROFESSION]" ("[LOCATION]") "gmail.com" OR "outlook.com",
  "resultsPerPage": [COUNT],
  "site": "linkedin.com"
}
```

## Search Tools

| Need | Tool |
|------|------|
| Current news/research | Metaphor (`mcp__pd-metaphor__metaphor-search`) |
| Web scraping | Firecrawl (`mcp__firecrawl__firecrawl_scrape`) |
| Site structure | Firecrawl (`mcp__firecrawl__firecrawl_map`) |
| Structured extraction | Firecrawl (`mcp__firecrawl__firecrawl_extract`) |
