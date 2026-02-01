# Claude Code Configuration

## Thread Types Framework

Use the appropriate thread type based on task complexity and requirements:

| Type | Pattern | When to Use | Commands |
|------|---------|-------------|----------|
| **Base** | 1 agent, 1 task | Simple tasks, quick queries | Direct execution |
| **P-Thread** | Parallel agents | Scale throughput, independent subtasks | `/scout`, `/plan` |
| **C-Thread** | Chained phases | Sequential workflows, build pipelines | `/scout_plan_build_test` |
| **F-Thread** | Fusion (best-of-N) | Compare approaches, pick winner | `/fusion-*` commands |
| **B-Thread** | Hierarchical hive | Complex coordination, divide & conquer | `/hive`, `/hive-*` |
| **S-Thread** | Swarm (multi-hive) | Large-scale parallel domains, mini-queens | `/swarm` |
| **L-Thread** | Long-running | Extended autonomous work | `/resolve*` commands |

### F-Thread Commands (Competing Implementations)
- `/fusion-algorithm` - Algorithm implementations
- `/fusion-refactor` - Refactoring strategies
- `/fusion-ui` - UI component designs
- `/fusion-bugfix` - Bug investigation hypotheses
- `/fusion-api` - API design philosophies
- `/fusion-perf` - Performance optimizations
- `/fusion-datamodel` - Data model philosophies
- `/fusion-test` - Testing strategies
- `/fusion-arch` - Architecture patterns

### B-Thread Commands (Hive Coordination)
- `/hive` - Generic multi-agent (1-4 workers)
- `/hive-refactor` - 9-agent large-scale refactoring
- `/hive-dependabot` - Dynamic agents per Dependabot PR

### S-Thread Commands (Swarm - Multi-Hive)

Swarm commands use **thin prompts + transparent documentation**:
- Templates in `~/.claude/swarm-templates/`
- Session docs in `.swarm/sessions/{ID}/docs/` and `phases/`
- Agents read phase files just-in-time (reduces context usage)

| Command | Planners | Mode | Use Case |
|---------|----------|------|----------|
| `/swarm` | 2-4 | Parallel | Multi-domain tasks |
| `/resolve-swarm-issue` | 2-4 | Parallel | Multi-domain GitHub issues |
| `/resolve-swarm-issue-long` | Up to 10 | **Sequential waves** | Complex long-horizon issues |

**Architecture:**
- Queen (Opus) → Planners (Opus) → Workers (mixed models)
- `coordination.log` for Queen ↔ Planners communication
- File ownership matrix prevents mid-flight conflicts
- Integration review cycle after all Planners complete

**Long-Horizon (`/resolve-swarm-issue-long`):**
- Deploys 1-2 Planners per wave
- Later Planners benefit from earlier discoveries
- Queen adapts domain assignments between waves

## Paths

| Item | Location |
|------|----------|
| API Keys | `C:\Users\USERNAME\env` |
| Settings | `C:\Users\USERNAME\.claude\settings.json` |
| MCP Config | `C:\Users\USERNAME\.mcp.json` |
| Commands | `C:\Users\USERNAME\.claude\commands\` |
| Skills | `C:\Users\USERNAME\.claude\skills\` |
| Swarm Templates | `C:\Users\USERNAME\.claude\swarm-templates\` |
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

**Notes**:
- `/hive` sessions: `.hive/sessions/{SESSION_ID}/`
- `/swarm` sessions: `.swarm/sessions/{SESSION_ID}/` (includes `docs/`, `phases/`, `state/`, `tasks/`, `logs/`)

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

**Pre-Session** (commands inject historical context):
```bash
# Grep learnings for task-related keywords
grep -iE "keyword1|keyword2" .ai-docs/learnings.jsonl | tail -10
```

**Post-Session** (agents append learnings):
```json
{"date":"YYYY-MM-DD","session":"session-id","task":"description","outcome":"success|partial|failed","keywords":["kw1","kw2"],"insight":"What was learned","files_touched":["file1.ts"]}
```

### Commands That Learn

| Command | Pre-Session | Post-Session |
|---------|-------------|--------------|
| `/fix` | Grep learnings | Append learning |
| `/fix-hive` | Grep learnings | Queen appends |
| `/hive` | Pre-scan greps | Queen appends |
| `/resolve-hive-issue` | Pre-scan greps | Queen appends |
| `/swarm` | Learning scout | Queen appends (Phase 5) |
| `/resolve-swarm-issue` | Validation + learning scout | Queen appends (Phase 5) |
| `/resolve-swarm-issue-long` | Validation + learning scout | Queen appends (Phase 5) |
| `/resolvegitissue` | Grep learnings | Append learning |

### Keyword Extraction

Use `~/.ai-docs/stopwords.txt` to filter common words:
```powershell
# Extract keywords from task description
# Filter stopwords, keep words > 3 chars
# Join with | for grep -iE pattern
```

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
