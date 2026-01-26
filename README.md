# Agent Setup

Portable multi-agent configuration for Claude Code, Gemini CLI, OpenCode, and Codex. Includes skills, commands, and specialized agents for orchestrated AI workflows.

## Prerequisites

### Runtime Requirements

| Requirement | Windows | macOS | Linux |
|-------------|---------|-------|-------|
| **Node.js 18+** | `winget install OpenJS.NodeJS.LTS` | `brew install node` | `sudo apt install nodejs` |
| **Python 3.11+** | `winget install Python.Python.3.11` | `brew install python@3.11` | `sudo apt install python3.11` |
| **Go 1.21+** | `winget install GoLang.Go` | `brew install go` | `sudo apt install golang-go` |
| **uv** (Python package manager) | `pip install uv` | `brew install uv` | `pip install uv` |

---

## AI Agent Platforms

### Claude Code (Anthropic)

Primary orchestrator for all commands and skills.

```bash
# All platforms
npm install -g @anthropic-ai/claude-code

# Verify
claude --version
```

### Gemini CLI (Google)

Google AI models including Gemini 3 Pro and Computer Use.

```bash
# All platforms
npm install -g @anthropic-ai/gemini-cli

# Verify
gemini --version
```

### Codex (OpenAI)

OpenAI models including GPT-4o and GPT-5.

```bash
# All platforms
npm install -g @openai/codex

# Verify
codex --version
```

### OpenCode

Multi-model CLI for GLM, Grok, BigPickle, and MiniMax models.

```bash
# All platforms (requires Go)
go install github.com/opencode-ai/opencode@latest

# Verify
opencode --version

# Enable autonomous mode
export OPENCODE_YOLO=true
```

**Available Models:**

| Model ID | Purpose |
|----------|---------|
| `opencode/big-pickle` | Deep analysis, edge cases |
| `opencode/grok-code` | Fast search, coherence checks |
| `opencode/minimax-m2.1` | Additional perspective |

### Cursor CLI

Cursor's agent mode via command line. Used by `/hive-experimental` and `/swarm-experimental` for Opus-powered agents.

```bash
# All platforms (requires Cursor installed)
# CLI is bundled with Cursor - add to PATH

# Windows (PowerShell)
$env:PATH += ";$env:LOCALAPPDATA\Programs\cursor\resources\app\bin"

# macOS
export PATH="$PATH:/Applications/Cursor.app/Contents/Resources/app/bin"

# Linux
export PATH="$PATH:/opt/cursor/resources/app/bin"

# Verify
cursor --version
```

**Agent Mode:**
```bash
# Run agent with prompt
cursor --agent "Implement feature X"

# With specific model
cursor --agent --model claude-opus-4 "Refactor this module"
```

**Notes:**
- Requires Cursor app installed (https://cursor.sh)
- Agent mode uses your Cursor subscription
- Supports Claude, GPT-4, and other models configured in Cursor

---

## Process Orchestration

### mprocs

Required for `/hive` commands that run multiple agents in parallel.

**Windows:**
```powershell
# Via Scoop (recommended)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
scoop install mprocs

# Or via winget
winget install pvolok.mprocs

# Or via Cargo
cargo install mprocs
```

**macOS:**
```bash
# Via Homebrew
brew install mprocs

# Or via Cargo
cargo install mprocs
```

**Linux:**
```bash
# Via Cargo (requires Rust)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
cargo install mprocs

# Or download binary
curl -fsSL https://github.com/pvolok/mprocs/releases/latest/download/mprocs-linux-amd64 -o /usr/local/bin/mprocs
chmod +x /usr/local/bin/mprocs
```

**Verify:**
```bash
mprocs --version
```

---

## Development Tools

| Tool | Purpose | Windows | macOS | Linux |
|------|---------|---------|-------|-------|
| **gh** | GitHub CLI | `winget install GitHub.cli` | `brew install gh` | `sudo apt install gh` |
| **git** | Version control | `winget install Git.Git` | `brew install git` | `sudo apt install git` |
| **jq** | JSON processing | `winget install jqlang.jq` | `brew install jq` | `sudo apt install jq` |

---

## Optional Dependencies

### Text-to-Speech

Used by `/tts` and `/speak` commands.

**ElevenLabs:**
```bash
pip install elevenlabs
# Requires ELEVENLABS_API_KEY
```

**Cartesia:**
```bash
pip install cartesia
# Requires CARTESIA_API_KEY
```

### Browser Automation

Used by `web-app-testing` skill and Gemini Computer Use.

**Playwright:**
```bash
pip install playwright
playwright install chromium
```

### Web Scraping

Used by various skills for documentation fetching.

**Firecrawl:**
```bash
pip install firecrawl-py
# Requires FIRECRAWL_API_KEY
```

---

## Environment Variables

Create a `.env` file or set these in your shell profile. See `.env.example` for a template.

### Required

```bash
# Anthropic (Claude Code)
export ANTHROPIC_API_KEY="sk-ant-..."

# Google (Gemini CLI)
export GOOGLE_API_KEY="..."
export GEMINI_API_KEY="..."

# OpenAI (Codex)
export OPENAI_API_KEY="sk-..."

# OpenCode
export OPENCODE_API_KEY="..."
export OPENCODE_YOLO=true  # Enable autonomous mode
```

### Optional

```bash
# Text-to-Speech
export ELEVENLABS_API_KEY="..."
export CARTESIA_API_KEY="..."

# Web Services
export FIRECRAWL_API_KEY="..."
export APIFY_API_KEY="..."  # LinkedIn scraping
```

---

## Installation

Copy contents to your `.claude/` directory:

**macOS/Linux:**
```bash
cp -r skills/* ~/.claude/skills/
cp -r commands/* ~/.claude/commands/
cp -r agents/* ~/.claude/agents/
cp CLAUDE.md ~/CLAUDE.md
```

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse skills\* $env:USERPROFILE\.claude\skills\ -Force
Copy-Item -Recurse commands\* $env:USERPROFILE\.claude\commands\ -Force
Copy-Item -Recurse agents\* $env:USERPROFILE\.claude\agents\ -Force
Copy-Item CLAUDE.md $env:USERPROFILE\CLAUDE.md -Force
```

---

## Verification

After installation, verify all tools are working:

```bash
# AI Agent Platforms
claude --version
gemini --version
codex --version
opencode --version
cursor --version  # Optional - for /hive-experimental

# Orchestration
mprocs --version

# Development Tools
gh --version
git --version
jq --version

# Python Dependencies
python -c "import playwright; print('Playwright OK')"
python -c "import elevenlabs; print('ElevenLabs OK')"
```

---

## Contents

### Thread Types Framework

| Type | Pattern | Commands |
|------|---------|----------|
| **Base** | 1 agent | Direct execution |
| **P-Thread** | Parallel | `/scout`, `/plan` |
| **C-Thread** | Chained | `/scout_plan_build_test` |
| **F-Thread** | Fusion | `/fusion-*` |
| **B-Thread** | Hive | `/hive`, `/hive-*` |
| **L-Thread** | Long-running | `/resolve*` |

### Skills (12)

| Skill | Purpose |
|-------|---------|
| `agentic-patterns` | Design patterns for AI agents |
| `ai-sdk-best-practices` | Production guidelines for AI SDK |
| `curate-learnings` | Summarize learnings into project-dna |
| `dependency-verifier` | Validate package versions |
| `frontend-design` | Production-grade UI implementation |
| `gemini-frontend-design` | UI design with Gemini ideation |
| `gemini-image` | Image generation/analysis |
| `gemini-llm` | Gemini text generation |
| `gemini-video` | Video analysis |
| `openai-llm` | OpenAI text generation |
| `skill-creator` | Create new skills |
| `web-app-testing` | Browser automation with Gemini |

### Commands (44)

#### F-Thread (Fusion - Competing Implementations)
| Command | Purpose |
|---------|---------|
| `/fusion-algorithm` | Compare algorithm implementations |
| `/fusion-api` | Compare API designs |
| `/fusion-arch` | Compare architecture patterns |
| `/fusion-bugfix` | Compare bug fix strategies |
| `/fusion-datamodel` | Compare data model designs |
| `/fusion-perf` | Compare performance optimizations |
| `/fusion-refactor` | Compare refactoring approaches |
| `/fusion-test` | Compare testing strategies |
| `/fusion-ui` | Compare UI designs |

#### B-Thread (Hive - Multi-Agent Coordination)
| Command | Purpose |
|---------|---------|
| `/hive` | Generic multi-agent (1-4 workers) |
| `/hive-experiment` | Spawn-on-demand experimental hive |
| `/hive-refactor` | 9-agent large-scale refactoring |
| `/hive-dependabot` | Dynamic agents per Dependabot PR |
| `/create-hive-issue` | Create issue with hive |
| `/refine-hive-gitissue` | Refine issue with hive |
| `/resolve-hive-issue` | Resolve issue with hive (heavyweight) |
| `/resolve-hive-comments` | Resolve PR comments with hive (lightweight) |
| `/validate-hive-issue` | Validate issue with hive |

#### C-Thread (Chained Workflows)
| Command | Purpose |
|---------|---------|
| `/scout` | Multi-model codebase search |
| `/plan` | Multi-agent planning |
| `/build` | Feature implementation |
| `/scout_plan` | Scout -> Plan |
| `/scout_plan_build` | Scout -> Plan -> Build |
| `/scout_plan_build_test` | Scout -> Plan -> Build -> Test |
| `/scout_refine` | Scout -> Refine existing plan |

#### L-Thread (Long-Running)
| Command | Purpose |
|---------|---------|
| `/resolvedependabot` | Resolve all Dependabot PRs |
| `/resolveprcomments` | Resolve all PR comments |
| `/resolvegitissue` | Resolve GitHub issue |

#### Compound Learning
| Command | Purpose |
|---------|---------|
| `/fix` | Fix with learning injection |
| `/fix-hive` | Hive fix with compound learning |
| `/init-project-dna` | Bootstrap `.ai-docs/` structure |

#### Utilities
| Command | Purpose |
|---------|---------|
| `/assess-codebase` | Multi-agent codebase assessment |
| `/gitinfo` | Git repository info |
| `/create-issue` | Create GitHub issue |
| `/validateissue` | Validate issue structure |
| `/refine` | Refine existing plan |
| `/refinegitissue` | Refine GitHub issue |
| `/compare-contrast` | Compare options |
| `/test_features` | Browser testing |
| `/speak`, `/tts` | Text-to-speech |

### Agents (13)

Specialized Task agents for domain-specific work:

| Agent | Domain |
|-------|--------|
| `ai-sdk-planner` | Vercel AI SDK architecture |
| `codebase-researcher` | Reverse-engineer codebases |
| `code-reviewer` | Code quality reviews |
| `design-review-agent` | UI/UX design reviews |
| `fastapi-specialist` | FastAPI development |
| `gcp-deployment` | Google Cloud deployment |
| `livekit-planner` | LiveKit real-time AI |
| `material3-expressive` | Material 3 design system |
| `mcp-server-specialist` | MCP server development |
| `pydantic-specialist` | Pydantic data modeling |
| `railway-specialist` | Railway deployment |
| `supabase-specialist` | Supabase development |
| `teams-integration-specialist` | Microsoft Teams integration |

---

## Hive Worker Models

Standard `/hive` and `/resolve-hive-issue` worker assignments:

| Worker | Model | Role |
|--------|-------|------|
| worker-1 | Claude Opus 4.5 | Complex logic, architecture |
| worker-2 | Gemini 3 Pro | Patterns, UI/frontend |
| worker-3 | OpenCode Grok Code | Backend/frontend coherence |
| worker-4 | Codex GPT-5.2 | Code simplification |
| reviewer-bigpickle | OpenCode BigPickle | Edge cases, deep analysis |
| reviewer-grok | OpenCode Grok Code | Quick observations |
| resolver | Claude Opus 4.5 | Address reviewer findings |
| tester | Codex GPT-5.2 | Run tests, fix failures |

### Pre-Scan Agents (4 parallel)

| Agent | Model | Focus |
|-------|-------|-------|
| Agent 1 | OpenCode BigPickle | Dependency analysis |
| Agent 2 | OpenCode Grok Code | Code organization |
| Agent 3 | OpenCode Grok Code | Quick search |
| Agent 4 | OpenCode MiniMax M2.1 | Config analysis |

---

## Compound Engineering

AI agents learn from past sessions to compound their effectiveness.

### File Structure

**Global** (`~/.ai-docs/`):
- `universal-patterns.md` - Cross-project patterns
- `model-insights.md` - AI model capabilities
- `workflow-learnings.md` - Thread type effectiveness
- `stopwords.txt` - Keyword filtering

**Per-Project** (`.ai-docs/`):
- `learnings.jsonl` - Append-only session learnings
- `project-dna.md` - Curated project patterns
- `bug-patterns.md` - Bug fix patterns

### Learning Commands

| Command | Pre-Session | Post-Session |
|---------|-------------|--------------|
| `/fix` | Grep learnings | Append learning |
| `/fix-hive` | Grep learnings | Queen appends |
| `/hive` | Pre-scan greps | Queen appends |
| `/resolve-hive-issue` | Pre-scan greps | Queen appends |

### Bootstrap New Projects

```bash
/init-project-dna
```

### Curate Learnings

```bash
/curate-learnings
```

---

## Usage

```bash
# F-Thread: Compare approaches
/fusion-arch "e-commerce platform"

# B-Thread: Multi-agent work
/hive "feature-name" 3
/hive-refactor "src/legacy/"
/resolve-hive-issue 42

# C-Thread: Chained workflow
/scout_plan_build_test "Add user authentication"

# L-Thread: Long-running
/resolvedependabot

# Compound Learning: Fix with history
/fix "authentication bug in login flow"
/fix-hive "refactor auth module"
```

---

## Platform-Specific Notes

### Windows Path Handling

**CRITICAL**: mprocs on Windows requires Windows-style paths with escaped backslashes.

```yaml
# CORRECT
cwd: "D:\\Code Projects\\MyProject"

# WRONG - Git Bash style will fail!
cwd: "/d/Code Projects/MyProject"
```

All hive commands use PowerShell to get proper Windows paths:
```bash
powershell -NoProfile -Command "(Get-Location).Path"
```

### macOS ARM (Apple Silicon)

Some tools may need Rosetta or ARM-specific builds:
```bash
# If issues with Go tools
arch -arm64 go install github.com/opencode-ai/opencode@latest
```

### Linux

Ensure `~/.local/bin` and `~/go/bin` are in your PATH:
```bash
export PATH="$HOME/.local/bin:$HOME/go/bin:$PATH"
```

---

## Troubleshooting

### Agent CLI not found
```bash
# Check if installed globally
npm list -g --depth=0

# Reinstall if missing
npm install -g @anthropic-ai/claude-code
```

### mprocs fails on Windows
- Use PowerShell, not Git Bash
- Ensure paths use `\\` not `/`
- Run as Administrator if permission issues

### OpenCode connection errors
```bash
# Verify API key
echo $OPENCODE_API_KEY

# Test connection
opencode run -m opencode/grok-code "Hello"
```

### Python dependency issues
```bash
# Use uv for faster, reliable installs
uv pip install playwright elevenlabs cartesia
```

---

## License

MIT
