---
description: F-Thread - Competing UI component designs in separate worktrees, user picks favorite
argument-hint: "<component-description>"
model: claude-sonnet-4-5-20250929
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
---

# Fusion UI - True F-Thread Component Design Arena

Launch 3-5 workers (based on variance level) in **separate git worktrees** to design the same UI component independently. A Judge Queen presents all designs for user selection.

## Thread Type: F-Thread (Fusion)

This is a TRUE fusion thread for UI design:
- **Divergent worktrees**: Each worker creates a unique design
- **Real artifacts**: Actual working components
- **Visual comparison**: Side-by-side preview of all designs
- **User selection**: User picks their favorite aesthetic

## Arguments

- `<component-description>`: What UI component to design (e.g., "pricing card", "navigation header", "login form")
- `--variance N`: Model diversity level (1-3, default: 1)
  - **Variance 1** (default): 3 workers (Sonnet, Gemini Pro, GPT-5.2)
  - **Variance 2**: 4 workers (+GLM 4.7 via OpenCode)

## Workflow

### Step 1-4: Prerequisites, Parse, Variables, Directories

(Same pattern as fusion-algorithm.md with appropriate substitutions)

**Variables** (in Step 3):
```
GEMINI_MODEL = "gemini-3-pro-preview"  # UI design = code generation, use Pro
```

### Step 5: Create Git Worktrees

```bash
# Worker A - Minimalist/Clean design
git worktree add "{WORKTREE_ROOT}/impl-a" -b fusion/{SESSION_ID}/impl-a

# Worker B - Bold/Expressive design
git worktree add "{WORKTREE_ROOT}/impl-b" -b fusion/{SESSION_ID}/impl-b

# Worker C - Playful/Creative design
git worktree add "{WORKTREE_ROOT}/impl-c" -b fusion/{SESSION_ID}/impl-c
```

### Step 6: Create tasks.json

```json
{
  "session": "{SESSION_ID}",
  "created": "{ISO_TIMESTAMP}",
  "status": "active",
  "thread_type": "F-Thread (Fusion)",
  "task_type": "fusion-ui",
  "component": {
    "description": "{COMPONENT_DESC}",
    "slug": "{COMPONENT_SLUG}"
  },
  "base_branch": "{BASE_BRANCH}",
  "worktrees": {
    "impl-a": {
      "path": "{WORKTREE_ROOT}/impl-a",
      "branch": "fusion/{SESSION_ID}/impl-a",
      "worker": "worker-a",
      "provider": "claude-sonnet",
      "design_style": "minimalist-clean",
      "status": "pending"
    },
    "impl-b": {
      "path": "{WORKTREE_ROOT}/impl-b",
      "branch": "fusion/{SESSION_ID}/impl-b",
      "worker": "worker-b",
      "provider": "gemini-3-pro",
      "design_style": "bold-expressive",
      "status": "pending"
    },
    "impl-c": {
      "path": "{WORKTREE_ROOT}/impl-c",
      "branch": "fusion/{SESSION_ID}/impl-c",
      "worker": "worker-c",
      "provider": "codex-gpt-5.2",
      "design_style": "playful-creative",
      "status": "pending"
    }
  },
  "evaluation": {
    "status": "pending",
    "criteria": ["visual_appeal", "accessibility", "responsiveness", "code_quality", "animation"],
    "winner": null
  }
}
```

### Step 7: Create Judge Queen Prompt

```markdown
# Judge Queen - UI Design Fusion Evaluator

You are the **Judge Queen** for an F-Thread UI design fusion session.

## Your Mission

Three workers are designing the same UI component with different aesthetics. Your job is to:
1. Monitor their progress
2. Ensure all designs are functional
3. Present all three for user comparison
4. Facilitate user selection

## Component to Design

**{COMPONENT_DESC}**

## Design Styles

| Worker | Style | Characteristics |
|--------|-------|-----------------|
| worker-a | Minimalist/Clean | Whitespace, subtle, typography-focused |
| worker-b | Bold/Expressive | Strong colors, dramatic, impactful |
| worker-c | Playful/Creative | Animations, unexpected, delightful |

## Evaluation Criteria

1. **Visual Appeal**: Does it look good?
2. **Accessibility**: WCAG compliance, keyboard nav, screen reader support
3. **Responsiveness**: Works on mobile/tablet/desktop
4. **Code Quality**: Clean, maintainable component code
5. **Animation/Polish**: Micro-interactions, transitions

## When All Complete

### Generate Preview Page

Create `.hive/sessions/{SESSION_ID}/preview.html`:

```html
<!DOCTYPE html>
<html>
<head>
  <title>UI Fusion: {COMPONENT_DESC}</title>
  <style>
    .comparison { display: grid; grid-template-columns: repeat(3, 1fr); gap: 2rem; }
    .design-card { border: 1px solid #ccc; padding: 1rem; }
    .design-card h2 { margin-top: 0; }
    iframe { width: 100%; height: 400px; border: none; }
  </style>
</head>
<body>
  <h1>Component Fusion: {COMPONENT_DESC}</h1>
  <div class="comparison">
    <div class="design-card">
      <h2>A: Minimalist/Clean</h2>
      <iframe src="file://{WORKTREE_ROOT}/impl-a/preview.html"></iframe>
    </div>
    <div class="design-card">
      <h2>B: Bold/Expressive</h2>
      <iframe src="file://{WORKTREE_ROOT}/impl-b/preview.html"></iframe>
    </div>
    <div class="design-card">
      <h2>C: Playful/Creative</h2>
      <iframe src="file://{WORKTREE_ROOT}/impl-c/preview.html"></iframe>
    </div>
  </div>
</body>
</html>
```

### Present to User

Open preview page and ask:
"All three designs are ready! Which style do you prefer?
- A: Minimalist/Clean
- B: Bold/Expressive
- C: Playful/Creative
- Mix: Combine elements from multiple designs"
```

### Step 8: Create Worker Prompts

**Worker A** (Minimalist/Clean):
```markdown
# Worker A - Minimalist/Clean UI Design

## Your Mission
Design **{COMPONENT_DESC}** with a minimalist, clean aesthetic.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-a
- **Branch**: fusion/{SESSION_ID}/impl-a

## Design Principles: Minimalist/Clean

- **Whitespace**: Let elements breathe
- **Typography**: Strong type hierarchy
- **Colors**: Limited palette, subtle accents
- **Borders**: Thin or none, use shadows sparingly
- **Animation**: Subtle, functional only
- **Layout**: Clear grid, aligned elements

## Deliverables

1. Component file(s) in project structure
2. `preview.html` - Standalone preview page
3. Ensure responsive (mobile-first)
4. WCAG AA accessibility minimum

## Style Guide

```css
/* Minimalist palette */
--background: #ffffff;
--text-primary: #1a1a1a;
--text-secondary: #666666;
--accent: #0066cc;
--border: #e5e5e5;

/* Typography */
font-family: system-ui, -apple-system, sans-serif;
line-height: 1.5;
```

## Begin

Announce: "Worker A starting minimalist/clean design of {COMPONENT_DESC}"
```

**Worker B** (Bold/Expressive):
```markdown
# Worker B - Bold/Expressive UI Design

## Your Mission
Design **{COMPONENT_DESC}** with a bold, expressive aesthetic.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-b
- **Branch**: fusion/{SESSION_ID}/impl-b

## Design Principles: Bold/Expressive

- **Color**: Rich, saturated colors
- **Contrast**: Strong visual hierarchy
- **Typography**: Display fonts, varied weights
- **Shapes**: Dramatic, asymmetric
- **Animation**: Purposeful, attention-grabbing
- **Impact**: Make a statement

## Deliverables

1. Component file(s) in project structure
2. `preview.html` - Standalone preview page
3. Ensure responsive
4. WCAG AA accessibility

## Style Guide

```css
/* Bold palette */
--background: #0a0a0a;
--surface: #1a1a1a;
--primary: #ff3366;
--secondary: #00ccff;
--text: #ffffff;

/* Typography */
font-family: 'Inter', sans-serif;
font-weight: 700;
```

## Begin

Announce: "Worker B starting bold/expressive design of {COMPONENT_DESC}"
```

**Worker C** (Playful/Creative):
```markdown
# Worker C - Playful/Creative UI Design

## Your Mission
Design **{COMPONENT_DESC}** with a playful, creative aesthetic.

## Your Worktree
- **Path**: {WORKTREE_ROOT}/impl-c
- **Branch**: fusion/{SESSION_ID}/impl-c

## Design Principles: Playful/Creative

- **Surprise**: Unexpected interactions
- **Delight**: Micro-animations, Easter eggs
- **Color**: Vibrant, gradient-rich
- **Shapes**: Organic, rounded, irregular
- **Animation**: Bouncy, playful easing
- **Personality**: Inject character

## Deliverables

1. Component file(s) in project structure
2. `preview.html` - Standalone preview page
3. Ensure responsive
4. WCAG AA accessibility

## Style Guide

```css
/* Playful palette */
--gradient-start: #ff6b6b;
--gradient-end: #4ecdc4;
--accent: #ffe66d;
--background: #f7f7f7;
--text: #2d3436;

/* Typography */
font-family: 'Nunito', sans-serif;
border-radius: 1rem;
```

## Begin

Announce: "Worker C starting playful/creative design of {COMPONENT_DESC}"
```

### Output Status

```markdown
## Fusion UI Arena Launched!

**Thread Type**: F-Thread (True Fusion)
**Session**: {SESSION_ID}
**Component**: {COMPONENT_DESC}

### Competing Design Styles

| Worker | Style | Vibe |
|--------|-------|------|
| Worker A | Minimalist/Clean | Apple, Notion, Linear |
| Worker B | Bold/Expressive | Stripe, Vercel, Framer |
| Worker C | Playful/Creative | Notion AI, Duolingo, Slack |

### Evaluation

When all designs are complete:
1. Preview page generated for side-by-side comparison
2. Accessibility audit on each
3. **You choose your favorite!**

Watch three design philosophies come to life!
```

### Step 9: Generate mprocs.yaml

Write to `.hive/mprocs.yaml`:

```yaml
# mprocs configuration for Fusion UI session: {SESSION_ID}
# Gemini CLI: using latest installed version
procs:
  judge-queen:
    cmd: ["claude", "--model", "opus", "--dangerously-skip-permissions", "You are the JUDGE QUEEN. Read .hive/sessions/{SESSION_ID}/queen-prompt.md"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
    env:
      HIVE_ROLE: "judge-queen"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"
      FUSION_TYPE: "ui"

  worker-a-sonnet:
    cmd: ["claude", "--model", "sonnet", "--dangerously-skip-permissions", "You are WORKER A. Read .hive/sessions/{SESSION_ID}/worker-a-prompt.md"]
    cwd: "{WORKTREE_ROOT}/impl-a"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "a"
      FUSION_APPROACH: "minimalist-clean"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-b-gemini:
    cmd: ["powershell", "-NoProfile", "-Command", "gemini -m {GEMINI_MODEL} -y -i 'You are WORKER B. Read .hive/sessions/{SESSION_ID}/worker-b-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-b"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "b"
      FUSION_APPROACH: "bold-expressive"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  worker-c-gpt:
    cmd: ["powershell", "-NoProfile", "-Command", "codex --dangerously-bypass-approvals-and-sandbox -m gpt-5.2 'You are WORKER C. Read .hive/sessions/{SESSION_ID}/worker-c-prompt.md'"]
    cwd: "{WORKTREE_ROOT}/impl-c"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "c"
      FUSION_APPROACH: "playful-creative"
      HIVE_SESSION: ".hive/sessions/{SESSION_ID}"

  logs:
    cmd: ["powershell", "-Command", "while($true) { Get-ChildItem '.hive/sessions/{SESSION_ID}/*.log' -ErrorAction SilentlyContinue | ForEach-Object { Write-Host \"=== $($_.Name) ===\"; Get-Content $_ -Tail 5 }; Start-Sleep 3; Clear-Host }"]
    cwd: "{PROJECT_ROOT_WINDOWS with \\ escaped as \\\\}"
```

### Variance Workers (Optional)

**If VARIANCE >= 2, add Worker D (GLM 4.7 - Accessible/Inclusive design):**

```yaml
  worker-d-glm:
    cmd: ["powershell", "-NoProfile", "-Command", "cd '{WORKTREE_ROOT}/impl-d'; $env:OPENCODE_YOLO='true'; opencode run --format default -m opencode/glm-4.7-free 'You are WORKER D. Design with accessibility-first approach. Focus on WCAG AAA compliance, keyboard navigation, screen reader optimization, and inclusive design patterns.'"]
    cwd: "{WORKTREE_ROOT}/impl-d"
    env:
      HIVE_ROLE: "fusion-worker"
      HIVE_WORKER_ID: "d"
      FUSION_APPROACH: "accessible-inclusive"
```

Create additional worktrees for variance workers:
```bash
# If VARIANCE >= 2:
git worktree add "{WORKTREE_ROOT}/impl-d" -b fusion/{SESSION_ID}/impl-d
```
