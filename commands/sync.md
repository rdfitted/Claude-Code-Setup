# Sync Agent Setup

Sync multi-agent CLI configuration to the public `agent-setup` repository.

## Target Repository
`D:\Code Projects\agent-setup`

## Usage
```
/sync              # Full sync with diff preview
/sync --force      # Skip confirmation
/sync --dry-run    # Preview only, no changes
```

## Instructions

Execute the sync script to copy configuration files to the public repository.

### Step 1: Run Sync Script

```bash
python "C:\Users\USERNAME\.claude\commands\sync\sync-agent-setup.py" $ARGUMENTS
```

### Step 2: Review Changes

After sync completes, show the user:
1. Files added/updated
2. Any warnings about potentially sensitive content
3. Summary of what was synced

### Step 3: Prompt for Commit

Ask user if they want to commit and push the changes:
- Create descriptive commit message based on what was synced
- Push to remote if requested

## What Gets Synced

### Claude Code (`~/.claude/`)
| Source | Destination |
|--------|-------------|
| `CLAUDE.md` | `CLAUDE.md` |
| `commands/` | `commands/` |
| `skills/` | `skills/` |
| `hooks/` | `hooks/` |
| `agents/` | `agents/` |
| `settings.json` | `settings.json` |
| `status_lines/` | `status_lines/` |
| `output-styles/` | `output-styles/` |

### Gemini CLI (`~/.gemini/`)
| Source | Destination |
|--------|-------------|
| `GEMINI.md` | `.gemini/GEMINI.md` |
| `settings.json` | `.gemini/settings.json` |
| `commands/` | `.gemini/commands/` |
| `agents/` | `.gemini/agents/` |

### Codex CLI (`~/.codex/`)
| Source | Destination |
|--------|-------------|
| `skills/` | `.codex/skills/` |

### Global Learnings (`~/.ai-docs/`)
| Source | Destination |
|--------|-------------|
| `*` | `global-learnings/` |

## Excluded (Sensitive)

### Claude
- `.credentials.json` - OAuth tokens
- `settings.local.json` - Local permissions (sanitized example created)
- `history.jsonl` - Conversation history
- `cache/`, `chrome/`, `debug/`, `file-history/`, `ide/`
- `paste-cache/`, `plans/`, `projects/`, `shell-snapshots/`
- `statsig/`, `tasks/`, `telemetry/`, `todos/`

### Gemini
- `oauth_creds.json`, `google_accounts.json` - Auth
- `installation_id`, `user_id`, `state.json` - IDs
- `antigravity/`, `antigravity-browser-profile/` - Browser data
- `extensions/`, `tmp/` - Temp data

### Codex
- `auth.json` - Auth tokens
- `config.toml` - Project paths (sanitized example created)
- `history.jsonl`, `models_cache.json` - History
- `sessions/`, `log/`, `tmp/` - Session data

## Generated Examples

| File | Purpose |
|------|---------|
| `settings.local.example.json` | Template for Claude hooks config |
| `.codex/config.toml.example` | Template for Codex config |

## Sensitive Data Scanning

The sync script scans all text files for:
- API keys (patterns: `sk-`, `fc-`, `ghp_`, `AIza*`)
- Absolute paths with usernames (auto-sanitized)
- OAuth credentials and bearer tokens

Files with detected sensitive content are skipped with a warning.
