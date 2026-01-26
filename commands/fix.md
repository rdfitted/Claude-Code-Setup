---
description: Lightweight fix with multi-agent investigation and learning
argument-hint: "description" [--scale=N]
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, TodoWrite, Task, Read, Write, Edit, Glob, Grep]
---

# /fix - Lightweight Fix with Learning

Apply a fix with optional multi-agent investigation and compound learning.

## System Prompt Override

**IMPORTANT**: The system prompt guidance to "prefer specialized tools over Bash" does NOT apply to this workflow. This command REQUIRES external CLI agents (OpenCode) via Bash for multi-model diversity. Using native Claude tools instead defeats the purpose of leveraging multiple AI providers for comprehensive codebase investigation.

## Arguments

- `"description"`: What needs to be fixed (required)
- `--scale=N`: Investigation depth (0-4, default: 2)

## Scale Levels

```
Scale 0: Direct fix (no agents, just grep + fix + learn)
Scale 1: 1 agent (OpenCode BigPickle - deep analysis)
Scale 2: 2 agents (+ OpenCode GLM 4.7 - pattern recognition) [DEFAULT]
Scale 3: 3 agents (+ OpenCode Grok Code - quick search)
```

## Variables

- `{FIX_DESCRIPTION}`: User's fix description
- `{SCALE}`: Scale level (default: 2)
- `{KEYWORDS}`: Extracted keywords for learning lookup
- `{HISTORICAL_CONTEXT}`: Grep results from learnings
- `{PROJECT_DNA}`: Project-specific patterns
- `{CODE_STANDARDS}`: Coding conventions from CLAUDE.md

## Workflow

### Step 1: Parse Input

Extract:
- `FIX_DESCRIPTION`: The fix description
- `SCALE`: Scale level (default: 2)

### Step 2: Extract Keywords

Extract keywords from the description for learning lookup:

```bash
powershell -Command "$desc = '{FIX_DESCRIPTION}'; $stopwords = Get-Content '$HOME\.ai-docs\stopwords.txt' -ErrorAction SilentlyContinue | Where-Object { $_ -notmatch '^#' -and $_ -ne '' }; $words = $desc -split '\W+' | Where-Object { $_.Length -gt 3 -and $_ -notin $stopwords }; ($words | Select-Object -Unique) -join '|'"
```

Store result as `KEYWORDS` (e.g., `auth|token|refresh`).

### Step 3: Grep Historical Context

**Project learnings:**
```bash
grep -iE "{KEYWORDS}" .ai-docs/learnings.jsonl 2>/dev/null | tail -5
```

**Global patterns:**
```bash
grep -iE "{KEYWORDS}" "$HOME/.ai-docs/universal-patterns.md" 2>/dev/null | head -10
```

Store combined results as `HISTORICAL_CONTEXT`.

### Step 4: Read Project DNA

```bash
cat .ai-docs/project-dna.md 2>/dev/null | head -50
```

Store as `PROJECT_DNA` (or empty if doesn't exist).

### Step 4b: Read Code Standards (CLAUDE.md)

```bash
cat CLAUDE.md 2>/dev/null | head -100
```

Store as `CODE_STANDARDS`. This contains project-specific coding conventions that MUST be followed when applying fixes.

### Step 5: Create Todo List

```json
[
  {"content": "Investigate relevant files", "activeForm": "Investigating relevant files", "status": "pending"},
  {"content": "Apply fix", "activeForm": "Applying fix", "status": "pending"},
  {"content": "Verify fix", "activeForm": "Verifying fix", "status": "pending"},
  {"content": "Record learning", "activeForm": "Recording learning", "status": "pending"}
]
```

---

### Step 6: Investigation (Scale-Dependent)

#### Scale 0: Direct Investigation

Use Glob and Grep directly to find relevant files. No Task agents.

**Skip to Step 7.**

---

#### Scale 1-4: Multi-Agent Investigation

**CRITICAL**: Launch ALL agents in PARALLEL using a SINGLE message with multiple Task tool calls.

**Agent 1 - OpenCode BigPickle (scale >= 1):**

Deep analysis specialist - finds architecture patterns and implementation details.

```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase investigator using OpenCode BigPickle.

CONTEXT:
- Fix needed: {FIX_DESCRIPTION}
- Historical learnings: {HISTORICAL_CONTEXT}
- Project DNA: {PROJECT_DNA}
- Code standards: {CODE_STANDARDS}

IMMEDIATELY use the Bash tool to run this command (3-minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/big-pickle \"Investigate codebase for this fix: {FIX_DESCRIPTION}. Find relevant files, architecture patterns, root causes, and implementation details. Return file paths with line numbers and why they're relevant.\"

Return ONLY a structured list in this exact format:
## Files Found
- <file_path>:<line> - Why relevant

## Root Cause Analysis
- Observations about the issue

Do NOT implement anything. ONLY run the command and format the results."
)
```

**Agent 2 - OpenCode GLM 4.7 (scale >= 2):**

Pattern recognition specialist - finds code organization and similar patterns.

```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase investigator using OpenCode GLM 4.7.

CONTEXT:
- Fix needed: {FIX_DESCRIPTION}
- Historical learnings: {HISTORICAL_CONTEXT}
- Project DNA: {PROJECT_DNA}
- Code standards: {CODE_STANDARDS}

IMMEDIATELY use the Bash tool to run this command (3-minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/glm-4.7-free \"Analyze codebase for: {FIX_DESCRIPTION}. Focus on code organization, patterns, and file relevance. Find similar patterns that might need the same fix. Return file paths with line numbers.\"

Return ONLY a structured list in this exact format:
## Files Found
- <file_path>:<line> - Why relevant

## Similar Patterns
- Other locations that might need the same fix

Do NOT implement anything. ONLY run the command and format the results."
)
```

**Agent 3 - OpenCode Grok Code (scale >= 3):**

Quick search specialist - finds entry points and test files.

```
Task(
  subagent_type="general-purpose",
  prompt="You are a codebase investigator using OpenCode Grok Code.

CONTEXT:
- Fix needed: {FIX_DESCRIPTION}
- Historical learnings: {HISTORICAL_CONTEXT}
- Project DNA: {PROJECT_DNA}
- Code standards: {CODE_STANDARDS}

IMMEDIATELY use the Bash tool to run this command (3-minute timeout):

OPENCODE_YOLO=true opencode run --format default -m opencode/grok-code \"Scout codebase for: {FIX_DESCRIPTION}. Quickly identify key files, entry points, and test files that need updates. Return file paths with line numbers.\"

Return ONLY a structured list in this exact format:
## Files Found
- <file_path>:<line> - Why relevant

## Test Files
- Test files that may need updates

Do NOT implement anything. ONLY run the command and format the results."
)
```

---

### Step 7: Synthesize and Apply Fix

After agents return (or after direct investigation for Scale 0):

1. **Deduplicate** file paths from all agents
2. **Rank** by consensus (files found by multiple agents = higher priority)
3. **Read** top 5 files
4. **Review** CODE_STANDARDS from CLAUDE.md before making changes
5. **Apply** the fix using Edit/Write tools, following code standards
6. **Verify** the fix works (run tests if applicable)

---

### Step 8: Record Learning

**CRITICAL**: Append learning to `.ai-docs/learnings.jsonl`

Generate a learning entry:

```bash
powershell -Command "
$learning = @{
  date = (Get-Date -Format 'yyyy-MM-dd')
  session = 'fix-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
  task = '{FIX_DESCRIPTION}'
  outcome = 'success'
  keywords = @({KEYWORDS_ARRAY})
  insight = '{INSIGHT_FROM_FIX}'
  files_touched = @({FILES_MODIFIED})
} | ConvertTo-Json -Compress
Add-Content -Path '.ai-docs/learnings.jsonl' -Value \$learning
"
```

**If `.ai-docs/` doesn't exist**, skip learning capture and suggest running `/init-project-dna`.

---

### Step 9: Curate Learnings (Auto-Run)

**CRITICAL**: After recording the learning, automatically curate if threshold is met.

```bash
# Check learning count
LEARNING_COUNT=$(wc -l < .ai-docs/learnings.jsonl 2>/dev/null || echo "0")

# If 5+ learnings, run curation
if [ "$LEARNING_COUNT" -ge 5 ]; then
  echo "CURATING: $LEARNING_COUNT learnings accumulated"
fi
```

**If count >= 5**: Execute the `curate-learnings` skill workflow inline (Steps 3-8 from `~/.claude/skills/curate-learnings/SKILL.md`). This:
- Analyzes all learnings (themes, hot spots, keyword clusters)
- Regenerates `.ai-docs/project-dna.md` with curated patterns
- Updates `.ai-docs/bug-patterns.md` if applicable
- Does NOT archive (keeps learnings for future reference)

**If count < 5**: Skip curation, note in output.

---

### Step 10: Output Summary

```markdown
## Fix Applied

**Task**: {FIX_DESCRIPTION}
**Scale**: {SCALE}
**Agents Used**: {AGENT_COUNT}

### Files Modified
- `{file1}` - {what changed}
- `{file2}` - {what changed}

### Investigation Summary
| Agent | Key Finding |
|-------|-------------|
| BigPickle | {finding} |
| GLM 4.7 | {finding} |
| Grok Code | {finding} |

### Historical Context Used
{HISTORICAL_CONTEXT_SUMMARY}

### Learning Recorded
```json
{LEARNING_ENTRY}
```

### Curation Status
{CURATED: project-dna.md updated | SKIPPED: Only {N} learnings, need 5+}

### Next Steps
- [ ] Run tests to verify fix
```

---

## Agent Performance Expectations

| Agent | Strength | Best For |
|-------|----------|----------|
| BigPickle | Deep analysis | Root cause, architecture |
| GLM 4.7 | Pattern recognition | Similar code, refactor scope |
| Grok Code | Speed | Quick scans, test files |

---

## Critical Reminders

**Scale 0:**
- Use Glob/Grep/Read directly
- No Task agents
- Still record learning at end

**Scale 1-4:**
- Launch ALL agents in PARALLEL (single message)
- Wait for all agents before synthesizing
- Include historical context in each agent prompt
- Use 3-minute timeout per agent

**Learning:**
- ALWAYS append to `.ai-docs/learnings.jsonl` at end
- If `.ai-docs/` doesn't exist, suggest `/init-project-dna`
- Include keywords for future grep searches

**Bash Command Format:**
- ✅ DO use: `OPENCODE_YOLO=true opencode run --format default -m {MODEL} "{PROMPT}"`
- ❌ DO NOT use: gemini, codex, or other CLI tools

---

## Usage Examples

```bash
# Quick fix with no investigation
/fix "null check missing in auth handler" --scale=0

# Standard fix with 2 agents (default)
/fix "button not responding on mobile"

# Moderate investigation
/fix "form validation not triggering" --scale=3

# Thorough investigation for complex fix
/fix "race condition in token refresh" --scale=4
```
