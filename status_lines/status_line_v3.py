#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Fix Windows Unicode output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def log_status_line(input_data, status_line_output, error_message=None):
    """Log status line event to logs directory."""
    # Ensure logs directory exists
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "status_line.json"

    # Read existing log data or initialize empty list
    if log_file.exists():
        with open(log_file, "r") as f:
            try:
                log_data = json.load(f)
            except (json.JSONDecodeError, ValueError):
                log_data = []
    else:
        log_data = []

    # Create log entry with input data and generated output
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "version": "v3",
        "input_data": input_data,
        "status_line_output": status_line_output,
    }

    if error_message:
        log_entry["error"] = error_message

    # Append the log entry
    log_data.append(log_entry)

    # Write back to file with formatting
    with open(log_file, "w") as f:
        json.dump(log_data, f, indent=2)


def get_session_data(transcript_path):
    """Get session data from transcript file."""
    if not transcript_path or not Path(transcript_path).exists():
        return None, f"Transcript file {transcript_path} does not exist"

    try:
        prompts = []
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if entry.get("type") == "user" and not entry.get("isMeta"):
                        message = entry.get("message", {})
                        content = message.get("content", [])
                        if content:
                            # Extract text from content array
                            text_parts = []
                            for item in content:
                                if item.get("type") == "text":
                                    text = item.get("text", "").strip()
                                    # Skip command messages
                                    if not text.startswith("<command-"):
                                        text_parts.append(text)
                            
                            if text_parts:
                                full_text = " ".join(text_parts).strip()
                                if full_text:
                                    prompts.append(full_text)
        
        return {"prompts": prompts}, None
    except Exception as e:
        return None, f"Error reading transcript file: {str(e)}"


def truncate_prompt(prompt, max_length=75):
    """Truncate prompt to specified length."""
    # Remove newlines and excessive whitespace
    prompt = " ".join(prompt.split())

    if len(prompt) > max_length:
        return prompt[: max_length - 3] + "..."
    return prompt


def get_prompt_icon(prompt):
    """Get icon based on prompt type."""
    if prompt.startswith("/"):
        return ">"
    elif "?" in prompt:
        return "?"
    elif any(
        word in prompt.lower()
        for word in ["create", "write", "add", "implement", "build"]
    ):
        return "+"
    elif any(word in prompt.lower() for word in ["fix", "debug", "error", "issue"]):
        return "!"
    elif any(word in prompt.lower() for word in ["refactor", "improve", "optimize"]):
        return "~"
    else:
        return "*"


def generate_status_line(input_data):
    """Generate the status line with agent name and last 3 prompts."""
    # Extract transcript path from input data
    transcript_path = input_data.get("transcript_path")

    # Get model name
    model_info = input_data.get("model", {})
    model_name = model_info.get("display_name", "Claude")

    # Get session data
    session_data, error = get_session_data(transcript_path)

    if error:
        # Log the error but show a default message
        log_status_line(input_data, f"[{model_name}] - No session data", error)
        return f"\033[36m[{model_name}]\033[0m \033[90m- No session data\033[0m"

    # Extract prompts
    prompts = session_data.get("prompts", [])

    # Build status line components
    parts = []

    # Model name - Blue
    parts.append(f"\033[34m[{model_name}]\033[0m")

    # Last 3 prompts (most recent first)
    if prompts:
        # Current prompt - white/bright with "CURRENT:" prefix
        current_prompt = prompts[-1]
        icon = get_prompt_icon(current_prompt)
        truncated = truncate_prompt(current_prompt, 60)
        parts.append(f"{icon} \033[97mCURRENT: {truncated}\033[0m")

        # Previous prompt - gray
        if len(prompts) > 1:
            prev_prompt = prompts[-2]
            truncated = truncate_prompt(prev_prompt, 40)
            parts.append(f"\033[90mprev: {truncated}\033[0m")

        # Two prompts ago - darker gray
        if len(prompts) > 2:
            older_prompt = prompts[-3]
            truncated = truncate_prompt(older_prompt, 30)
            parts.append(f"\033[90molder: {truncated}\033[0m")
    else:
        parts.append("\033[90m- No prompts yet\033[0m")

    # Join with separator
    status_line = " | ".join(parts)

    return status_line


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())

        # Generate status line
        status_line = generate_status_line(input_data)

        # Log the status line event (without error since it's successful)
        log_status_line(input_data, status_line)

        # Output the status line (first line of stdout becomes the status line)
        print(status_line)

        # Success
        sys.exit(0)

    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully - output basic status
        print("\033[31m[Agent] [Claude] - JSON Error\033[0m")
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully - output basic status
        print(f"\033[31m[Agent] [Claude] - Error: {str(e)}\033[0m")
        sys.exit(0)


if __name__ == "__main__":
    main()
