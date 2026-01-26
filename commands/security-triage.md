---
description: Full security scan with LLM triage of findings
argument-hint: [path] [--fix]
allowed-tools: [Bash, Read, Edit, Glob, Grep]
---

# Security Triage

Full programmatic security scan, then LLM triages the noise.

No targeting - scan everything, then filter.

## Step 1: Run All Available Scanners

Run whatever's installed. Capture all output.

```bash
# Semgrep (best general-purpose scanner)
echo "=== SEMGREP ===" && semgrep scan --config=auto --config=p/security-audit --json 2>/dev/null | head -400 || echo "semgrep not installed"
```

```bash
# npm audit (JS/TS dependencies)
echo "=== NPM AUDIT ===" && npm audit --json 2>/dev/null | head -150 || echo "no package-lock.json"
```

```bash
# pip-audit (Python dependencies)
echo "=== PIP AUDIT ===" && pip-audit --format json 2>/dev/null | head -150 || echo "pip-audit not installed"
```

```bash
# Bandit (Python source)
echo "=== BANDIT ===" && bandit -r . -f json 2>/dev/null | head -300 || echo "bandit not installed"
```

```bash
# Check for obvious secrets (quick grep)
echo "=== SECRET PATTERNS ===" && grep -rn "API_KEY\|SECRET\|PASSWORD\|PRIVATE_KEY" --include="*.ts" --include="*.js" --include="*.py" --include="*.env*" . 2>/dev/null | grep -v node_modules | grep -v ".git" | head -30
```

## Step 2: LLM Triages Each Finding

For each scanner finding:

### Read the flagged code in context

Use Read tool to see the actual code around the flagged line.

### Classify as:

| Classification | Action |
|----------------|--------|
| **CRITICAL** | Must fix before merge. SQL injection, command injection, hardcoded prod secrets. |
| **HIGH** | Fix soon. XSS, path traversal, auth bypass. |
| **MEDIUM** | Track as tech debt. Weak crypto, missing validation. |
| **LOW** | Nice to have. Deprecated functions, missing headers. |
| **FALSE POSITIVE** | Ignore. Test code, examples, comments, already-sanitized input. |

### For FALSE POSITIVE, explain why:
- "This is test fixture data, not a real secret"
- "Input is already validated by middleware above"
- "This is a documentation example, not executed code"

### For real issues, provide:
- What the vulnerability is (OWASP category)
- How it could be exploited (1-2 sentences)
- The fix (actual code)

## Step 3: Fix Critical/High (if --fix flag)

If `--fix` flag passed, fix CRITICAL and HIGH issues:

1. Read the full file
2. Apply the fix with Edit tool
3. Only fix if the change is mechanical and safe

**Do NOT auto-fix if:**
- Fix requires architectural changes
- Fix might break functionality
- You're not 100% sure of the fix

## Output

```markdown
## Security Triage Report

**Scanners Run**: semgrep, npm audit, bandit
**Total Findings**: {N}
**After Triage**: {N} real issues

### Summary

| Severity | Count | False Positives Filtered |
|----------|-------|--------------------------|
| CRITICAL | 0 | 0 |
| HIGH | 1 | 2 |
| MEDIUM | 3 | 5 |
| LOW | 4 | 8 |

### Real Issues

#### [HIGH] SQL Injection
**File**: `src/api/users.ts:42`
**Scanner**: semgrep (sql-injection)

\`\`\`typescript
// Vulnerable
const user = await db.query(`SELECT * FROM users WHERE id = ${id}`)
\`\`\`

**Exploit**: `/api/users/1'; DROP TABLE users--`

**Fix**:
\`\`\`typescript
const user = await db.query('SELECT * FROM users WHERE id = $1', [id])
\`\`\`

---

### False Positives Filtered

| File | Scanner Rule | Why Ignored |
|------|--------------|-------------|
| tests/fixtures/secrets.ts | hardcoded-secret | Test fixture |
| docs/example.py | sql-injection | Documentation example |
| src/config.example.ts | api-key-exposed | Template file with placeholder |

### Dependency Vulnerabilities

| Package | Severity | CVE | Upgrade To |
|---------|----------|-----|------------|
| lodash | HIGH | CVE-2021-23337 | 4.17.21 |

Run `npm audit fix` or `pip-audit --fix` to remediate.
```
