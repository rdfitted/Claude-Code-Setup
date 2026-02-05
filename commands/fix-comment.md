---
description: Validate and fix a single PR/review comment (lightweight, no agents)
argument-hint: "<paste comment here>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

# Fix Comment - Lightweight PR Comment Resolution

Validate a single PR comment (CodeRabbit, reviewer, etc.) and take action directly. No multi-agent, no gh calls, no mprocs.

## Workflow

### Step 1: Parse the Comment

Extract from the provided comment:
- **File**: The file being commented on
- **Lines**: Specific line numbers if mentioned
- **Issue**: What the comment claims is wrong
- **Suggested Fix**: If provided

> **Note**: Historical context, project DNA, and code standards are automatically injected by the `UserPromptSubmit` hook.

### Step 2: Read the Relevant Code

```bash
# Read the file mentioned in the comment
```

Understand:
- Current implementation
- Context around the flagged lines
- How the code actually works

### Step 3: Validate the Concern

**Ask yourself:**
1. Is the comment technically correct?
2. Does the issue actually exist in the code?
3. Could this be a false positive / misunderstanding?
4. Is the suggested fix appropriate?

### Step 4: Take Action

**If VALID (issue is real):**
1. Explain why it's valid
2. Consider any auto-injected context (project DNA, learnings)
3. Implement the fix following code standards
4. Show what changed

**If NOT VALID (false positive):**
1. Explain why it's not valid
2. Show evidence from the code
3. Optionally suggest a reply to the comment

### Step 5: Output

```markdown
## Comment Analysis

**File**: {file}
**Lines**: {lines}
**Issue Claimed**: {what the comment says}

### Verdict: VALID / NOT VALID

**Reasoning**: {why}

### Action Taken

{what was done - fix applied OR explanation of why no fix needed}
```

---

## Example Usage

```
/fix-comment The handler uses the stale React `error` state after awaiting retryFailedItems...
```

```
/fix-comment @coderabbitai says there's a race condition in onClick handler line 1185
```

---

## Notes

- This is for **single comments** that don't warrant full `/resolveprcomments`
- No git operations - just read, validate, fix
- You commit separately after reviewing changes
- For 3+ comments, use `/resolveprcomments` instead
