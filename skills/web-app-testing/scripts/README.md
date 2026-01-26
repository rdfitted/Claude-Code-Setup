# Web App Testing Scripts

## Current Implementation

### ✅ `gemini_browser.py` - **USE THIS ONE**

**Official Gemini Computer Use implementation**

This is the ONLY script you should use. It implements Gemini Computer Use correctly according to Google's official documentation.

**Features:**
- Gemini AI analyzes screenshots and makes decisions
- Executes actions on YOUR local visible browser (Playwright)
- You can WATCH the automation happen
- Captures console logs
- Slow-motion mode for visibility

**Usage:**
```bash
python gemini_browser.py "https://en.wikipedia.org" --task "Search for cats"
```

**Options:**
- `--task` / `-t`: Required - Natural language task description
- `--slow`: Slow motion delay in ms (default: 500)
- `--headless`: Run without visible browser
- `--max-turns`: Maximum conversation turns (default: 20)

---

## Deprecated Scripts (in `deprecated/` folder)

These scripts are outdated and should NOT be used:

### ❌ `sdk_integration.py`
- **Problem**: Fakes browser actions instead of executing them
- **Replaced by**: `gemini_browser.py`

### ❌ `local_playwright.py`
- **Problem**: No AI - just hardcoded automation
- **Replaced by**: `gemini_browser.py` (has both AI + visible browser)

### ❌ `multi_turn_handler.py`
- **Problem**: Manual function execution, incomplete implementation
- **Replaced by**: `gemini_browser.py`

### ❌ `simple_demo.py`
- **Problem**: Only shows what Gemini wants to do, doesn't execute
- **Replaced by**: `gemini_browser.py`

### ❌ `real_browser_integration.py`
- **Problem**: Incomplete implementation
- **Replaced by**: `gemini_browser.py`

---

## Why Only One Script Now?

**Before (v2.x):** Multiple confusing options
- Some used Gemini but didn't show browser
- Some showed browser but had no AI
- Some didn't work properly at all

**Now (v3.0):** One correct implementation
- ✅ Gemini AI intelligence
- ✅ Visible local browser
- ✅ Official implementation pattern
- ✅ Simple to use

---

## Quick Start

```bash
# Navigate to scripts directory
cd C:\Users\USERNAME\.claude\skills\web-app-testing\scripts

# Run Gemini Computer Use with visible browser
python gemini_browser.py "https://example.com" --task "Your task here"

# Examples:
python gemini_browser.py "https://en.wikipedia.org" --task "Search for cats"
python gemini_browser.py "https://google.com" --task "Check for console errors"
python gemini_browser.py "http://localhost:3000" --task "Test the login flow"
```

That's it! One script, properly implemented, easy to use.
