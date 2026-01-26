# Swarm Role Hierarchy

This document defines the strict 3-tier hierarchy for swarm operations.

---

## Tier Structure

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: QUEEN                                              │
│  - One per session                                          │
│  - Top-level orchestrator                                   │
│  - Spawns PLANNERS only                                     │
│  - Owns: branch, commits, PR, integration                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ spawns
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: PLANNERS (A-J)                                     │
│  - 1-10 per session (waves in long-horizon)                 │
│  - Domain/issue orchestrators                               │
│  - Spawns WORKERS only                                      │
│  - Owns: task files, worker coordination, review cycle      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ spawns
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: WORKERS                                            │
│  - 2-4 per Planner                                          │
│  - Implementation executors                                 │
│  - Spawns NOTHING                                           │
│  - Owns: code changes within assigned files                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Queen Responsibilities

### MUST DO:
- Create feature branch
- Write Planner prompt files (`planner-{X}-prompt.md`)
- Spawn Planners via mprocs
- Monitor wave progress via logs
- Update `state/wave-status.md`
- Plan future waves based on discoveries
- Run integration cycle (Phase 4)
- Commit all changes
- Create and push PR

### MUST NOT:
- Spawn Workers directly
- Write Worker task files
- Implement code changes
- Modify files outside `.swarm/` during orchestration

---

---

## ⏱️ Model Timing - PATIENCE REQUIRED

Different worker models have vastly different startup times. **This is normal behavior, not a failure.**

| Worker Model | CLI | Startup Time | Be Patient For |
|--------------|-----|--------------|----------------|
| Cursor/Opus | Cursor CLI | 30-60s | 5 minutes |
| **Gemini 3 Pro** | Gemini | **60-90s** | **8 minutes** |
| Grok Code | OpenCode | 10s | 3 minutes |
| **Codex GPT-5.2** | Codex | **90-120s** | **12 minutes** |

**Gemini** initializes slowly. No log activity for 2 minutes is NORMAL.
**Codex** is **slow throughout its entire execution**, not just startup. It's extremely deliberate and methodical. Log updates may be 2-3 minutes apart even during active work. This is normal - Codex is thinking, not stuck.

**DO NOT respawn** workers just because they're quiet. Check the times above first.

---

## Planner Responsibilities

### MUST DO:
- Read assigned domain/concerns from `responsibility-matrix.md`
- Break work into 2-4 Worker tasks
- Write Worker task files (`tasks/planner-{X}/worker-*-task.md`)
- Spawn Workers sequentially
- Monitor Worker completion
- Spawn Reviewer + Tester
- Address review issues
- Signal `PLANNER_COMPLETE` to Queen

### MUST NOT:
- Spawn other Planners
- Work outside assigned domain
- Implement code directly (delegate to Workers)
- Modify `state/wave-status.md` (Queen's responsibility)
- Signal complete before review cycle finishes

---

## Worker Responsibilities

### MUST DO:
- Read task file for instructions
- Implement assigned changes
- Stay within assigned file boundaries
- Signal completion via log

### MUST NOT:
- Spawn any agents
- Modify files outside assignment
- Make architectural decisions
- Communicate with other Workers directly

---

## Spawn Rules Summary

| Agent | Can Spawn | Cannot Spawn |
|-------|-----------|--------------|
| Queen | Planners, Integration Team | Workers |
| Planner | Workers, Reviewer, Tester | Planners, Integration Team |
| Worker | Nothing | Everything |

---

## Communication Channels

| From | To | Channel |
|------|-----|---------|
| Queen → Planner | `coordination.log` with `[DIRECTIVE]` |
| Planner → Queen | `coordination.log` with `[STATUS]` |
| Planner → Worker | Task file |
| Worker → Planner | `planner-{X}.log` |

---

## Long-Horizon Specific Rules

In `/resolve-swarm-issue-long`:

1. **Queen deploys Planners in waves** (1-2 at a time)
2. **Later waves benefit from earlier discoveries**
3. **Max 10 Planners total** (A through J)
4. **Queen adapts domain assignments between waves**

Wave progression:
```
Wave 1: Planner A (foundational)
   ↓ wait for PLANNER_COMPLETE
Wave 2: Planner B, C (dependent on Wave 1)
   ↓ wait for PLANNER_COMPLETE
Wave 3: Planner D (dependent on Wave 2)
   ↓ ...
Integration Cycle (after all waves)
```
