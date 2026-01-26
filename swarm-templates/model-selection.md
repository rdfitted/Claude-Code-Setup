# Model Selection Guide

## Agent → Model Mapping

### Orchestration (Claude Code)
| Role | Model | CLI | Specialty |
|------|-------|-----|-----------|
| Queen | Opus 4.5 | Claude Code | Orchestration, final review, PRs |
| Planner | Opus 4.5 | Claude Code | Task breakdown, team coordination |

### Workers (Cursor CLI / Mixed)
| Role | Model | CLI | Specialty |
|------|-------|-----|-----------|
| Worker 1 (Backend) | Opus 4.5 | **Cursor CLI** | Architecture, APIs, business logic |
| Worker 2 (Frontend) | Gemini 3 Pro | Gemini | UI, styling, components |
| Worker 3 (Coherence) | Grok Code | OpenCode | Cross-file consistency |
| Worker 4 (Simplify) | Codex GPT-5.2 | Codex | Code cleanup, simplification |

### Review & Resolution (Cursor CLI / Mixed)
| Role | Model | CLI | Specialty |
|------|-------|-----|-----------|
| Reviewer | BigPickle | OpenCode | Code review, security, quality |
| Resolver | Opus 4.5 | **Cursor CLI** | Fix review findings |
| Tester | Codex GPT-5.2 | Codex | Test execution, coverage |
| Code Quality | Opus 4.5 | **Cursor CLI** | PR comment resolution |

### Integration Phase (Cursor CLI / Mixed)
| Role | Model | CLI | Specialty |
|------|-------|-----|-----------|
| Integration Reviewer | BigPickle | OpenCode | Cross-domain review |
| Integration Tester | Codex GPT-5.2 | Codex | Full test suite |
| Integration Resolver | Opus 4.5 | **Cursor CLI** | Cross-domain fixes |

---

## Cursor CLI Spawn Pattern

Worker 1, Resolver, Code Quality, and Integration Resolver use Cursor CLI via `.bat` files:

```batch
@echo off
mprocs --server 127.0.0.1:{PORT} --ctl "{\"c\": \"add-proc\", \"cmd\": \"cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \\\"PROMPT\\\"\", \"name\": \"agent-name\", \"cwd\": \"{PROJECT_ROOT_FORWARD_SLASH}\"}"
```

**Note**: Cursor CLI uses a global model setting (Opus 4.5). All Cursor windows share the same model.

---

## Pre-Scan Agents (Phase 0)

| Role | Model | Purpose |
|------|-------|---------|
| Architecture Scanner | BigPickle | Main architecture patterns |
| Organization Scanner | GLM 4.7 | Code organization, coupling |
| Entry Points Scanner | Grok Code | Entry points, test files |
| File Scout (per domain) | GLM 4.7 + Grok Code | File ownership mapping |
| Learning Scout | GLM 4.7 | Extract learnings from .ai-docs |
| Validation Agent | BigPickle/GLM/Grok | Concern validation (3 per concern) |

---

## ⏱️ Model Timing Characteristics

**CRITICAL**: Different models have vastly different startup and execution times. Planners MUST account for this.

| Model | CLI | Startup | Execution | Total Expected |
|-------|-----|---------|-----------|----------------|
| Opus 4.5 | Claude Code | Fast (5-10s) | Fast | 1-3 min |
| Opus 4.5 | Cursor CLI | Slow (30-60s) | Fast | 2-5 min |
| **Gemini 3 Pro** | Gemini | **SLOW (60-90s)** | Medium | **3-8 min** |
| Grok Code | OpenCode | Fast (10s) | Fast | 1-3 min |
| **Codex GPT-5.2** | Codex | **VERY SLOW (90-120s)** | Slow | **5-15 min** |
| BigPickle | OpenCode | Medium (20s) | Medium | 2-5 min |
| GLM 4.7 | OpenCode | Fast (10s) | Fast | 1-2 min |

### Patience Requirements

**Gemini (Worker 2)**:
- Takes 60-90 seconds just to initialize
- May appear "stuck" during startup - this is NORMAL
- First log entry may take 2+ minutes
- Do NOT respawn if no activity in first 2 minutes

**Codex (Worker 4, Tester)**:
- Slowest model in the swarm - **slow throughout, not just startup**
- Takes 90-120 seconds to initialize
- Execution is **extremely methodical and deliberate**
- Log updates are INFREQUENT - may go 2-3 minutes between updates
- This is Codex being thorough, NOT being stuck
- May take 10-15 minutes for complex tasks
- Do NOT respawn if log updates are sparse - this is normal Codex behavior

### Polling Intervals

When monitoring worker completion:

```
Gemini workers:  Poll every 60 seconds, wait up to 10 minutes
Codex workers:   Poll every 90 seconds, wait up to 15 minutes
Other workers:   Poll every 30 seconds, wait up to 5 minutes
```

### Wait Before Declaring Failure

| Model | Min Wait Before Respawn |
|-------|------------------------|
| Opus 4.5 | 5 minutes |
| Gemini | 8 minutes |
| Codex | 12 minutes |
| Others | 5 minutes |

---

## When to Use Each Model

### Opus 4.5 (Claude Code or Cursor CLI)
- Complex reasoning and architecture decisions
- Multi-step planning and orchestration
- Code requiring deep understanding
- Coordination and conflict resolution

### Gemini 3 Pro
- Frontend/UI implementation
- Visual components and styling
- Layout and user experience
- React/Vue/Svelte components

### Grok Code (OpenCode)
- Quick coherence checks
- Pattern matching across files
- Consistency verification
- Fast file scanning

### Codex GPT-5.2
- Code execution and testing
- Simplification tasks
- Straightforward implementations
- Test suite execution

### BigPickle (OpenCode)
- Deep code review
- Security analysis
- Quality assessment
- Architecture review

### GLM 4.7 (OpenCode)
- Learning extraction
- Pattern recognition
- File organization analysis
- Documentation scanning

---

## CLI Auto-Approve Flags

| CLI | Flag | Purpose |
|-----|------|---------|
| Claude Code | `--dangerously-skip-permissions` | Skip all approval prompts |
| Cursor CLI | `--force` | Force allow commands |
| Gemini | `-y` | Auto-approve |
| OpenCode | env `OPENCODE_YOLO=true` | Skip approvals |
| Codex | `--dangerously-bypass-approvals-and-sandbox` | Full bypass |
