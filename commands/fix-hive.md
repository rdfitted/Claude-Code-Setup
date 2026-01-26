---
description: Full hive multi-agent fix with compound learning
argument-hint: "fix-description" [worker-count]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob]
---

# /fix-hive - Hive Fix with Compound Learning

Launch a full Hive multi-agent session to apply a fix, with compound learning baked in.

This is `/hive` enhanced with:
- Pre-session grep of historical learnings
- Historical context injected into Queen prompt
- Queen MUST append learning before session ends

## Arguments

- `"fix-description"`: What needs to be fixed (required)
- `[worker-count]`: Number of workers (1-4, default: 4)

## Workflow

This follows the same workflow as `/hive` with these additions:

---

### Step 0a: Extract Keywords and Historical Context (BEFORE Pre-Scan)

**Extract keywords from fix description:**
```bash
powershell -Command "$desc = '{FIX_DESCRIPTION}'; $stopwords = Get-Content '$HOME\.ai-docs\stopwords.txt' -ErrorAction SilentlyContinue | Where-Object { $_ -notmatch '^#' -and $_ -ne '' }; $words = $desc -split '\W+' | Where-Object { $_.Length -gt 3 -and $_ -notin $stopwords }; ($words | Select-Object -Unique) -join '|'"
```

Store as `KEYWORDS`.

**Grep project learnings:**
```bash
grep -iE "{KEYWORDS}" .ai-docs/learnings.jsonl 2>/dev/null | tail -10
```

**Grep global patterns:**
```bash
grep -iE "{KEYWORDS}" "$HOME/.ai-docs/universal-patterns.md" 2>/dev/null | head -10
grep -iE "{KEYWORDS}" "$HOME/.ai-docs/model-insights.md" 2>/dev/null | head -5
```

**Read project DNA:**
```bash
cat .ai-docs/project-dna.md 2>/dev/null | head -50
```

Combine all results as `HISTORICAL_CONTEXT`.

---

### Step 0b-0c: Pre-Scan (Same as /hive)

Run the standard 4-agent pre-scan from `/hive`:
- Agent 1: Architecture Scanner (OpenCode BigPickle)
- Agent 2: Code Organization Scanner (OpenCode GLM 4.7)
- Agent 3: Entry Points Scanner (OpenCode Grok Code)

**Launch all 4 in PARALLEL using Task tool with Bash calls to OpenCode CLI.**

Store results in `.hive/sessions/{SESSION_ID}/prescan-results.md`.

---

### Modified Queen Prompt (Step 6)

Add these sections to the Queen prompt AFTER "## Your Role":

```markdown
## Log Protocol (CRITICAL)

**APPEND-ONLY**: All logs are append-only. NEVER overwrite, ALWAYS add.

### Writing to Your Log

Use append mode (`>>` or `Add-Content`):
```powershell
# CORRECT - Append
Add-Content -Path ".hive/sessions/{SESSION_ID}/queen.log" -Value "[$(Get-Date -Format 'HH:mm:ss')] Message here"

# WRONG - Overwrites
Set-Content -Path ".hive/sessions/{SESSION_ID}/queen.log" -Value "Message"
```

### Log Entry Format

```
[HH:MM:SS] AGENT_ID: ACTION - Details
```

### Reading Other Agents' Logs

**Check what others have done** by reading the last 20 lines of their logs:
```powershell
Get-Content ".hive/sessions/{SESSION_ID}/worker-1.log" -Tail 20
```

## Historical Context (Compound Learning)

Previous sessions and patterns relevant to this fix:

{HISTORICAL_CONTEXT}

**Use this context to:**
- Avoid approaches that failed before
- Apply patterns that worked before
- Build on previous learnings

## Learning Responsibility (CRITICAL)

**Before setting `session_status: complete`, you MUST:**

1. Summarize what was learned in this session
2. Append learning to `.ai-docs/learnings.jsonl`:

```bash
powershell -Command "
$learning = @{
  date = (Get-Date -Format 'yyyy-MM-dd')
  session = '{SESSION_ID}'
  task = '{FIX_DESCRIPTION}'
  outcome = '{success|partial|failed}'
  keywords = @('{KEYWORDS_ARRAY}')
  insight = 'FILL_IN: What did we learn?'
  files_touched = @('FILL_IN: files modified')
  worker_contributions = @{
    worker1 = 'FILL_IN'
    worker2 = 'FILL_IN'
  }
} | ConvertTo-Json -Compress
Add-Content -Path '.ai-docs/learnings.jsonl' -Value `$learning
"
```

**If `.ai-docs/` doesn't exist**, note in results.md that `/init-project-dna` should be run.

3. If a notable pattern was discovered, append to `.ai-docs/project-dna.md`:
```bash
echo "- {PATTERN} (learned: {SESSION_ID})" >> .ai-docs/project-dna.md
```

4. **Auto-Curate Learnings** (if threshold met):

```powershell
# Check learning count
$learningCount = (Get-Content ".ai-docs/learnings.jsonl" -ErrorAction SilentlyContinue | Measure-Object -Line).Lines

if ($learningCount -ge 5) {
    Add-Content -Path ".hive/sessions/{SESSION_ID}/queen.log" -Value "[$(Get-Date -Format 'HH:mm:ss')] QUEEN: CURATING - $learningCount learnings accumulated"

    # Execute inline curation:
    # 1. Read all learnings
    # 2. Analyze patterns, keywords, outcomes
    # 3. Regenerate project-dna.md with updated insights
    # 4. Update bug-patterns.md if applicable
    # 5. Log completion

    Add-Content -Path ".hive/sessions/{SESSION_ID}/queen.log" -Value "[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Curation complete - project-dna.md updated"
} else {
    Add-Content -Path ".hive/sessions/{SESSION_ID}/queen.log" -Value "[$(Get-Date -Format 'HH:mm:ss')] QUEEN: Curation skipped - only $learningCount learnings (need 5+)"
}
```

**Curation Process** (inline, from `~/.claude/skills/curate-learnings/SKILL.md`):
- Analyze keyword frequency and build keyword clusters
- Identify success patterns vs anti-patterns
- Find hot spot files (frequently modified)
- Merge duplicate insights
- Regenerate `project-dna.md` with curated guidelines
- Update `bug-patterns.md` if applicable
```

---

### Rest of Workflow (Same as /hive)

Continue with the standard `/hive` workflow:

**Setup & Generation:**
- Step 1: Check mprocs installation
- Step 2: Parse arguments
- Step 3: Classify task & select Gemini model
- Step 4: Generate session variables (TIMESTAMP, SESSION_ID, MPROCS_PORT)
- Step 5: Create session directory

**Spawn-on-Demand Architecture:**
- Step 6: Generate Queen Prompt (with Log Protocol + learning additions above)
- Step 7: Generate Worker Task Files (all 7: worker-1 through worker-4, reviewer-bigpickle, reviewer-grok, tester-1)
- Step 8: Generate Code Quality Task Template (for Phase 6 loop)
- Step 9: Generate mprocs.yaml (spawn-on-demand - only Queen starts, workers spawned dynamically)
- Step 10: Create empty log files and session-guidelines.md
- Step 11: Launch mprocs in new terminal

**Queen Orchestration Phases (executed by Queen after launch):**
- Phase 1: Spawn workers (worker-1 + worker-2 parallel, then worker-3, then worker-4)
- Phase 2: Spawn reviewers (bigpickle + grok)
- Phase 3: Spawn tester
- Phase 4: Curate learnings (with /fix-hive additions above)
- Phase 5: Commit & push
- Phase 6: Code Quality Loop (automated PR comment resolution - up to 5 iterations)

**CRITICAL**:
- All agents use append-only logging (`Add-Content` in PowerShell)
- Workers read other agents' logs before starting dependent tasks
- Queen spawns workers via mprocs TCP server commands
- Phase 6 is MANDATORY - Queen must wait 10 minutes for external reviewers and resolve comments

---

### Modified Output Status (Step 11)

Add to the output:

```markdown
### Compound Learning

**Historical Context Injected**: {CONTEXT_LINE_COUNT} lines from past sessions
**Keywords Used**: {KEYWORDS}

**Queen will:**
1. Record learning before session ends
2. Auto-curate if 5+ learnings accumulated

To verify:
```bash
# Check learning was captured
tail -1 .ai-docs/learnings.jsonl

# Check if curation ran
grep "CURATING\|Curation" .hive/sessions/{SESSION_ID}/queen.log
```
```

---

## Key Differences from /hive

| Aspect | /hive | /fix-hive |
|--------|-------|-----------|
| Pre-session | Pre-scan + Learning Scout | Grep learnings + pre-scan (lightweight) |
| Queen prompt | Standard | Includes historical context injection |
| Phase 4 | Curate learnings (optional) | Record learning + auto-curate (MANDATORY) |
| Session end | Set complete | Record → curate → complete |
| Focus | General tasks | Fixes with compound learning |

**What's the same:**
- Spawn-on-demand architecture
- 3 pre-scan agents (BigPickle, GLM 4.7, Grok Code)
- Worker team (Opus, Gemini, GLM 4.7, Codex)
- Reviewers (BigPickle, Grok)
- Tester (Codex)
- Phase 6 code quality loop
- Append-only logging protocol

---

## Usage Examples

```bash
# Full hive fix with learning
/fix-hive "authentication token not refreshing correctly"

# Smaller team for simpler fix
/fix-hive "null pointer in user service" 2
```

---

## Critical Reminders

1. **Always grep before pre-scan** - Historical context helps agents
2. **Pre-scan uses 3 agents** - BigPickle, GLM 4.7, Grok Code (same as /hive)
3. **Spawn-on-demand** - Only Queen starts in mprocs, workers spawned via TCP commands
4. **Queen MUST record learning** - This is mandatory, not optional
5. **Queen MUST auto-curate** - If 5+ learnings, curate before marking complete
6. **Phase 6 is MANDATORY** - Wait 10 min for external reviewers, resolve all PR comments
7. **Keywords matter** - Good keywords = better future lookups
8. **Run `/init-project-dna` first** if `.ai-docs/` doesn't exist
9. **All logs are APPEND-ONLY** - Never overwrite, always add
10. **Agents read each other's logs** - Before starting dependent tasks, check what others have done
