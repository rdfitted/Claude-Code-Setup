#!/usr/bin/env python3
"""
Sync Claude Code configuration to public agent-setup repository.
Excludes sensitive data, scans for secrets, creates sanitized examples.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuration
HOME = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", "")))
SOURCE_ROOT = HOME
CLAUDE_DIR = HOME / ".claude"
TARGET_REPO = Path("D:/Code Projects/agent-setup")

# What to sync
SYNC_MAP = {
    # Source -> Destination (relative to respective roots)
    # Claude Code
    "CLAUDE.md": "CLAUDE.md",
    ".claude/commands": "commands",
    ".claude/skills": "skills",
    ".claude/hooks": "hooks",
    ".claude/agents": "agents",
    ".claude/settings.json": "settings.json",
    ".claude/status_lines": "status_lines",
    ".claude/output-styles": "output-styles",
    # Gemini CLI
    ".gemini/GEMINI.md": ".gemini/GEMINI.md",
    ".gemini/settings.json": ".gemini/settings.json",
    ".gemini/commands": ".gemini/commands",
    ".gemini/agents": ".gemini/agents",
    # Codex CLI (OpenAI)
    ".codex/skills": ".codex/skills",
    # Global learnings
    ".ai-docs": "global-learnings",
}

# Files/folders to exclude
EXCLUDE_PATTERNS = [
    # Claude sensitive
    ".credentials.json",
    "settings.local.json",
    "history.jsonl",
    "stats-cache.json",
    "cache",
    "chrome",
    "debug",
    "file-history",
    "ide",
    "paste-cache",
    "plans",
    "projects",
    "shell-snapshots",
    "statsig",
    "tasks",
    "telemetry",
    "todos",
    ".mcp.json",
    "mcp.json",
    ".env",
    "env",
    "__pycache__",
    ".pyc",
    "node_modules",
    ".git",
    "workflow elements.zip",
    "common-errors-fixes.md",
    # Gemini sensitive
    "oauth_creds.json",
    "google_accounts.json",
    "installation_id",
    "user_id",
    "state.json",
    "antigravity",
    "antigravity-browser-profile",
    "extensions",
    "tmp",
    # Codex sensitive
    "auth.json",
    "config.toml",  # has project paths
    "models_cache.json",
    "version.json",
    "sessions",
    "log",
    ".system",
]

# Patterns that indicate ACTUAL sensitive content (real keys, not documentation)
# These must match real key formats with specific lengths
SENSITIVE_PATTERNS = [
    r"sk-ant-api[a-zA-Z0-9\-]{40,}",  # Anthropic API key (real format)
    r"sk-[a-zA-Z0-9]{48}",  # OpenAI API key (real format, exactly 48 chars after sk-)
    r"ghp_[a-zA-Z0-9]{36}",  # GitHub PAT (exactly 36 chars)
    r"gho_[a-zA-Z0-9]{36}",  # GitHub OAuth (exactly 36 chars)
    r"fc-[a-f0-9]{32}",  # Firecrawl key (exactly 32 hex chars)
    r"AIzaSy[a-zA-Z0-9\-_]{33}",  # Google API key (starts with AIzaSy, 39 total)
    # Actual credential assignments with real-looking values
    r'"api_key"\s*:\s*"[a-zA-Z0-9\-_]{30,}"',  # JSON API key assignment
    r"api_key\s*=\s*['\"][a-zA-Z0-9\-_]{30,}['\"]",  # Python/env API key
]

# Patterns that look like keys but are OK (documentation, examples, patterns)
SAFE_PATTERNS = [
    r"AIza\[",  # Regex pattern documentation
    r"sk-\.\*",  # Regex pattern documentation
    r"sk-\.\.\.",  # Placeholder
    r"sk-ant-\.\.\.",  # Placeholder
    r'api_key.*\$',  # Variable reference
    r"Bearer\s+\{",  # Template placeholder
    r"Bearer\s+<",  # Template placeholder
]

# Path patterns to sanitize (replace with placeholders)
PATH_SANITIZE = [
    (r"C:\\Users\\[^\\\"]+", r"C:\\Users\\USERNAME"),
    (r"/c/Users/USERNAME/\"]+", r"/c/Users/USERNAME"),
    (r"/Users/USERNAME/\"]+", r"/Users/USERNAME"),
    (r"/home/USERNAME/\"]+", r"/home/USERNAME"),
]

# API key patterns to sanitize (replace with env var references)
API_KEY_SANITIZE = [
    # Inline env var assignments before commands (GEMINI_API_KEY=xxx gemini ...)
    (r"GEMINI_API_KEY=AIzaSy[a-zA-Z0-9\-_]{33}", r"GEMINI_API_KEY=${GEMINI_API_KEY}"),
    (r"GOOGLE_API_KEY=AIzaSy[a-zA-Z0-9\-_]{33}", r"GOOGLE_API_KEY=${GOOGLE_API_KEY}"),
    (r"OPENAI_API_KEY=sk-[a-zA-Z0-9]{48}", r"OPENAI_API_KEY=${OPENAI_API_KEY}"),
    (r"ANTHROPIC_API_KEY=sk-ant-[a-zA-Z0-9\-]{40,}", r"ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"),
    # Python variable assignments (API_KEY = "..." or api_key = '...')
    (r"API_KEY\s*=\s*['\"]AIzaSy[a-zA-Z0-9\-_]{33}['\"]", r'API_KEY = os.environ.get("GEMINI_API_KEY")'),
    (r"api_key\s*=\s*['\"]AIzaSy[a-zA-Z0-9\-_]{33}['\"]", r'api_key=os.environ.get("GEMINI_API_KEY")'),
    (r"api_key\s*=\s*['\"]sk-[a-zA-Z0-9]{48}['\"]", r'api_key=os.environ.get("OPENAI_API_KEY")'),
    # genai.Client(api_key='...') style
    (r"Client\(api_key=['\"]AIzaSy[a-zA-Z0-9\-_]{33}['\"]\)", r'Client(api_key=os.environ.get("GEMINI_API_KEY"))'),
    # OpenAI project keys (sk-proj-...)
    (r"api_key=['\"]sk-proj-[a-zA-Z0-9_]{100,}['\"]", r'api_key=os.environ.get("OPENAI_API_KEY")'),
    (r"OpenAI\(api_key=['\"]sk-proj-[a-zA-Z0-9_]{100,}['\"]\)", r'OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))'),
    # JSON assignments
    (r'"api_key"\s*:\s*"AIzaSy[a-zA-Z0-9\-_]{33}"', r'"api_key": "${GEMINI_API_KEY}"'),
    (r'"api_key"\s*:\s*"sk-[a-zA-Z0-9]{48}"', r'"api_key": "${OPENAI_API_KEY}"'),
    # Markdown backticks with API keys
    (r"`AIzaSy[a-zA-Z0-9\-_]{33}`", r"`${GEMINI_API_KEY}`"),
    (r"`sk-[a-zA-Z0-9]{48}`", r"`${OPENAI_API_KEY}`"),
    # Firecrawl
    (r"FIRECRAWL_API_KEY=fc-[a-f0-9]{32}", r"FIRECRAWL_API_KEY=${FIRECRAWL_API_KEY}"),
    (r'"FIRECRAWL_API_KEY"\s*:\s*"fc-[a-f0-9]{32}"', r'"FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"'),
    # ElevenLabs
    (r"ELEVENLABS_API_KEY=[a-zA-Z0-9]{32}", r"ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}"),
]


class SyncStats:
    def __init__(self):
        self.files_copied = 0
        self.files_skipped = 0
        self.files_unchanged = 0
        self.dirs_created = 0
        self.warnings = []
        self.changes = []


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded from sync."""
    path_str = str(path)
    name = path.name

    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str or name == pattern or name.endswith(pattern):
            return True

    # Exclude retired folders
    if "retired" in path.parts:
        return True

    return False


def check_sensitive_content(content: str, filepath: Path) -> list[str]:
    """Scan content for sensitive patterns. Returns list of warnings."""
    warnings = []

    # First check if this looks like documentation/regex patterns (safe)
    for safe_pattern in SAFE_PATTERNS:
        if re.search(safe_pattern, content):
            # File contains documentation patterns, be more lenient
            return []

    for pattern in SENSITIVE_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            # Don't include the actual sensitive value in warning
            warnings.append(f"  - Potential sensitive data ({pattern[:25]}...) in {filepath}")

    return warnings


def sanitize_paths(content: str) -> str:
    """Replace user-specific paths with placeholders."""
    for pattern, replacement in PATH_SANITIZE:
        content = re.sub(pattern, replacement, content)
    return content


def sanitize_api_keys(content: str) -> tuple[str, int]:
    """Replace API keys with environment variable references. Returns (content, count)."""
    count = 0
    for pattern, replacement in API_KEY_SANITIZE:
        new_content, n = re.subn(pattern, replacement, content)
        if n > 0:
            count += n
            content = new_content
    return content, count


def get_file_hash(filepath: Path) -> Optional[str]:
    """Get MD5 hash of file for change detection."""
    if not filepath.exists():
        return None
    try:
        return hashlib.md5(filepath.read_bytes()).hexdigest()
    except Exception:
        return None


def sync_file(src: Path, dst: Path, stats: SyncStats, dry_run: bool = False) -> None:
    """Sync a single file with automatic sanitization of sensitive content."""
    if should_exclude(src):
        stats.files_skipped += 1
        return

    # Read content
    try:
        if src.suffix in [".md", ".json", ".py", ".ps1", ".sh", ".txt", ".yaml", ".yml", ".toml"]:
            content = src.read_text(encoding="utf-8", errors="replace")

            # Sanitize API keys (replace with env var references)
            content, keys_sanitized = sanitize_api_keys(content)
            if keys_sanitized > 0:
                stats.warnings.append(f"  - Sanitized {keys_sanitized} API key(s) in {src.name}")

            # Sanitize paths
            content = sanitize_paths(content)

            # Check for any remaining sensitive content we might have missed
            warnings = check_sensitive_content(content, src)
            if warnings:
                stats.warnings.extend(warnings)
                # Still sync, but warn - the sanitization should have caught real keys

            # Check if file changed
            if dst.exists():
                existing = dst.read_text(encoding="utf-8", errors="replace")
                if existing == content:
                    stats.files_unchanged += 1
                    return

            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(content, encoding="utf-8")

            stats.files_copied += 1
            status = "Updated" if dst.exists() else "Added"
            sanitize_note = f" (sanitized)" if keys_sanitized > 0 else ""
            stats.changes.append(f"  {'[DRY] ' if dry_run else ''}{status}: {dst.relative_to(TARGET_REPO)}{sanitize_note}")
        else:
            # Binary file - just copy
            src_hash = get_file_hash(src)
            dst_hash = get_file_hash(dst)

            if src_hash == dst_hash:
                stats.files_unchanged += 1
                return

            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)

            stats.files_copied += 1
            stats.changes.append(f"  {'[DRY] ' if dry_run else ''}{'Updated' if dst.exists() else 'Added'}: {dst.relative_to(TARGET_REPO)}")

    except Exception as e:
        stats.warnings.append(f"  - Error processing {src}: {e}")
        stats.files_skipped += 1


def sync_directory(src_dir: Path, dst_dir: Path, stats: SyncStats, dry_run: bool = False) -> None:
    """Recursively sync a directory."""
    if not src_dir.exists():
        stats.warnings.append(f"  - Source not found: {src_dir}")
        return

    if src_dir.is_file():
        sync_file(src_dir, dst_dir, stats, dry_run)
        return

    for item in src_dir.rglob("*"):
        if item.is_file() and not should_exclude(item):
            rel_path = item.relative_to(src_dir)
            dst_path = dst_dir / rel_path
            sync_file(item, dst_path, stats, dry_run)


def create_settings_example(stats: SyncStats, dry_run: bool = False) -> None:
    """Create sanitized settings.local.example.json."""
    src = CLAUDE_DIR / "settings.local.json"
    dst = TARGET_REPO / "settings.local.example.json"

    if not src.exists():
        return

    try:
        content = json.loads(src.read_text(encoding="utf-8"))

        # Sanitize the content
        sanitized = {
            "permissions": {
                "allow": ["WebFetch(domain:docs.example.com)", "WebSearch"],
                "deny": []
            },
            "enableAllProjectMcpServers": content.get("enableAllProjectMcpServers", False),
            "enabledMcpjsonServers": ["context7", "playwright"],
            "hooks": {}
        }

        # Include hooks structure but sanitize paths
        if "hooks" in content:
            for hook_type, hook_configs in content["hooks"].items():
                sanitized["hooks"][hook_type] = []
                for config in hook_configs:
                    sanitized_config = {}
                    if "matcher" in config:
                        sanitized_config["matcher"] = config["matcher"]
                    if "hooks" in config:
                        sanitized_config["hooks"] = []
                        for hook in config["hooks"]:
                            sanitized_hook = {"type": hook.get("type", "command")}
                            if "command" in hook:
                                # Sanitize path
                                cmd = hook["command"]
                                cmd = re.sub(r"C:\\Users\\[^\\]+", r"C:\\Users\\USERNAME", cmd)
                                cmd = re.sub(r"/c/Users/USERNAME/]+", r"/c/Users/USERNAME", cmd)
                                sanitized_hook["command"] = cmd
                            if "statusMessage" in hook:
                                sanitized_hook["statusMessage"] = hook["statusMessage"]
                            sanitized_config["hooks"].append(sanitized_hook)
                    sanitized["hooks"][hook_type].append(sanitized_config)

        output = json.dumps(sanitized, indent=2)

        if dst.exists():
            existing = dst.read_text(encoding="utf-8")
            if existing == output:
                stats.files_unchanged += 1
                return

        if not dry_run:
            dst.write_text(output, encoding="utf-8")

        stats.files_copied += 1
        stats.changes.append(f"  {'[DRY] ' if dry_run else ''}Generated: settings.local.example.json")

    except Exception as e:
        stats.warnings.append(f"  - Error creating settings example: {e}")


def create_codex_config_example(stats: SyncStats, dry_run: bool = False) -> None:
    """Create sanitized config.toml.example for Codex."""
    src = HOME / ".codex" / "config.toml"
    dst = TARGET_REPO / ".codex" / "config.toml.example"

    if not src.exists():
        return

    try:
        content = src.read_text(encoding="utf-8")

        # Create sanitized version
        sanitized = '''# Codex CLI Configuration Example
# Copy to ~/.codex/config.toml and customize

model = "gpt-5.2-codex"
model_reasoning_effort = "medium"
windows_wsl_setup_acknowledged = true

# Trust your project directories
# [projects.'C:\\Path\\To\\Project']
# trust_level = "trusted"

[notice]
hide_gpt5_1_migration_prompt = true
"hide_gpt-5.1-codex-max_migration_prompt" = true

[notice.model_migrations]
"gpt-5.2" = "gpt-5.2-codex"

[features]
unified_exec = true
shell_snapshot = true
powershell_utf8 = true
collab = true
steer = true
'''

        if dst.exists():
            existing = dst.read_text(encoding="utf-8")
            if existing == sanitized:
                stats.files_unchanged += 1
                return

        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(sanitized, encoding="utf-8")

        stats.files_copied += 1
        stats.changes.append(f"  {'[DRY] ' if dry_run else ''}Generated: .codex/config.toml.example")

    except Exception as e:
        stats.warnings.append(f"  - Error creating Codex config example: {e}")


def main():
    parser = argparse.ArgumentParser(description="Sync Claude setup to public repo")
    parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview only")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print("AGENT SETUP SYNC")
    print(f"{'='*60}")
    print(f"Source: {SOURCE_ROOT}")
    print(f"Target: {TARGET_REPO}")
    print(f"Mode:   {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*60}\n")

    if not TARGET_REPO.exists():
        print(f"ERROR: Target repo not found: {TARGET_REPO}")
        sys.exit(1)

    stats = SyncStats()

    # Sync each mapped item
    print("Syncing files...")
    for src_rel, dst_rel in SYNC_MAP.items():
        src_path = SOURCE_ROOT / src_rel
        dst_path = TARGET_REPO / dst_rel

        print(f"  {src_rel} -> {dst_rel}")
        sync_directory(src_path, dst_path, stats, args.dry_run)

    # Create sanitized example files
    print("\nGenerating example configs...")
    create_settings_example(stats, args.dry_run)
    create_codex_config_example(stats, args.dry_run)

    # Print results
    print(f"\n{'='*60}")
    print("SYNC RESULTS")
    print(f"{'='*60}")
    print(f"Files copied/updated: {stats.files_copied}")
    print(f"Files unchanged:      {stats.files_unchanged}")
    print(f"Files skipped:        {stats.files_skipped}")

    if stats.changes:
        print(f"\nChanges:")
        for change in stats.changes[:50]:  # Limit output
            print(change)
        if len(stats.changes) > 50:
            print(f"  ... and {len(stats.changes) - 50} more")

    if stats.warnings:
        print(f"\nWarnings ({len(stats.warnings)}):")
        for warning in stats.warnings[:20]:
            print(warning)
        if len(stats.warnings) > 20:
            print(f"  ... and {len(stats.warnings) - 20} more")

    print(f"\n{'='*60}")

    if args.dry_run:
        print("DRY RUN COMPLETE - No files were modified")
    else:
        print("SYNC COMPLETE")

    print(f"{'='*60}\n")

    # Only return error code if there are actual problems (not just sanitization notices)
    has_errors = any("Error" in w or "Potential sensitive" in w for w in stats.warnings)
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
