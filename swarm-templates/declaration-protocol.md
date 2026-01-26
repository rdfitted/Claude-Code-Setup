# Declaration Protocol

**MANDATORY**: Before EVERY spawn or major action, you MUST declare your intent using this exact format.

---

## Declaration Format

```
DECLARATION: I will [ACTION] using [CLI] with model [MODEL].
Command: [EXACT COMMAND TO EXECUTE]
```

---

## Examples

### Spawning Workers

```
DECLARATION: I will spawn Worker 1A using Cursor CLI with model Opus 4.5.
Command: mprocs --server 127.0.0.1:{PORT} --ctl '{"c": "add-proc", "cmd": "cmd /c wsl -d Ubuntu /root/.local/bin/agent --force \"Read {PATH}/worker-1a-task.md and execute.\"", "name": "worker-1a", "cwd": "{PROJECT_ROOT}"}'
```

```
DECLARATION: I will spawn Worker 2A using Gemini CLI with model gemini-3-pro-preview.
Command: mprocs --server 127.0.0.1:{PORT} --ctl '{"c": "add-proc", "cmd": "gemini -m gemini-3-pro-preview -y -i \"Read {PATH}/worker-2a-task.md and execute.\"", "name": "worker-2a", "cwd": "{PROJECT_ROOT}"}'
```

```
DECLARATION: I will spawn Worker 3A using OpenCode CLI with model grok-code.
Command: mprocs --server 127.0.0.1:{PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/grok-code --prompt \"Read {PATH}/worker-3a-task.md and execute.\"", "name": "worker-3a", "cwd": "{PROJECT_ROOT}", "env": {"OPENCODE_YOLO": "true"}}'
```

```
DECLARATION: I will spawn Worker 4A using Codex CLI with model gpt-5.2.
Command: mprocs --server 127.0.0.1:{PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read {PATH}/worker-4a-task.md and execute.\"", "name": "worker-4a", "cwd": "{PROJECT_ROOT}"}'
```

### Spawning Reviewers

```
DECLARATION: I will spawn Reviewer using OpenCode CLI with model big-pickle.
Command: mprocs --server 127.0.0.1:{PORT} --ctl '{"c": "add-proc", "cmd": "opencode -m opencode/big-pickle --prompt \"Read {PATH}/reviewer-task.md and execute.\"", "name": "reviewer-a", "cwd": "{PROJECT_ROOT}", "env": {"OPENCODE_YOLO": "true"}}'
```

```
DECLARATION: I will spawn Tester using Codex CLI with model gpt-5.2.
Command: mprocs --server 127.0.0.1:{PORT} --ctl '{"c": "add-proc", "cmd": "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 \"Read {PATH}/tester-task.md and execute.\"", "name": "tester-a", "cwd": "{PROJECT_ROOT}"}'
```

---

## Why This Matters

1. **Self-correction**: If your declaration doesn't match `config.json`, you catch the error BEFORE executing
2. **Token savings**: Wrong spawns waste 1000+ tokens. Catching drift early saves everything downstream
3. **Auditability**: Logs show exactly what was intended vs executed
4. **Consistency**: Every agent follows the same pattern

---

## Validation Checklist

Before executing any spawn command, verify:

- [ ] Model matches `config.json` for this worker role
- [ ] CLI tool matches `config.json` for this worker role
- [ ] Command flags match `config.json` command_template
- [ ] Worker number matches role (1=backend, 2=frontend, 3=coherence, 4=simplify)

---

## DO NOT

- ❌ Do NOT improvise model assignments based on task content
- ❌ Do NOT change CLI tools based on personal preference
- ❌ Do NOT skip the declaration before spawning
- ❌ Do NOT use models not in `config.json`

---

## Log Format

After declaration and execution, log:

```
[HH:MM:SS] PLANNER-X: SPAWNED Worker {N}{X} | CLI: {cli} | Model: {model} | Task: {description}
```

Example:
```
[14:32:15] PLANNER-A: SPAWNED Worker 1A | CLI: cursor | Model: opus | Task: Backend models/schemas/CRUD/routes
[14:35:22] PLANNER-A: SPAWNED Worker 2A | CLI: gemini | Model: gemini-3-pro-preview | Task: Frontend types/components
```
