#!/usr/bin/env python3
"""
Simplified demo version of Gemini Computer Use
Shows what actions the model wants to take without full execution
"""

import json
import requests
from typing import Dict, List

API_KEY = os.environ.get("GEMINI_API_KEY")
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-computer-use-preview-10-2025:generateContent"


def demo_test(url: str, task: str = "check console logs"):
    """
    Simple demo that shows what Gemini Computer Use wants to do

    Args:
        url: URL to test
        task: What to test
    """
    print(f"\n{'='*60}")
    print(f"DEMO: Testing {url}")
    print(f"Task: {task}")
    print(f"{'='*60}\n")

    prompt = f"""Navigate to {url} and {task}.
    Take screenshots and report your findings."""

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "tools": [{
            "computer_use": {
                "environment": "ENVIRONMENT_BROWSER"
            }
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2048
        }
    }

    print("[API CALL] Sending request to Gemini Computer Use...\n")

    response = requests.post(API_ENDPOINT, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"[ERROR] API returned {response.status_code}")
        print(response.text)
        return

    data = response.json()

    print("[RESPONSE RECEIVED]\n")

    # Extract what the model wants to do
    candidate = data["candidates"][0]
    parts = candidate["content"]["parts"]

    print("="*60)
    print("GEMINI WANTS TO EXECUTE:")
    print("="*60)

    for i, part in enumerate(parts, 1):
        if "functionCall" in part:
            func = part["functionCall"]
            func_name = func["name"]
            func_args = func.get("args", {})

            print(f"\n{i}. Function: {func_name}")
            if func_args:
                print(f"   Arguments:")
                for key, value in func_args.items():
                    print(f"     - {key}: {value}")
            else:
                print(f"   Arguments: None")

        elif "text" in part:
            print(f"\n{i}. Text Response:")
            print(f"   {part['text'][:200]}...")

    print("\n" + "="*60)
    print("METADATA:")
    print("="*60)
    usage = data.get("usageMetadata", {})
    print(f"Model: {data.get('modelVersion', 'Unknown')}")
    print(f"Tokens Used: {usage.get('totalTokenCount', 0)} ({usage.get('promptTokenCount', 0)} prompt + {usage.get('candidatesTokenCount', 0)} response)")
    print(f"Finish Reason: {candidate.get('finishReason', 'Unknown')}")

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("To fully execute this test:")
    print("1. Execute the function calls above")
    print("2. Capture screenshots and logs")
    print("3. Send results back to Gemini")
    print("4. Continue conversation until final test results")
    print("\nUse 'multi_turn_handler.py' for full execution")
    print("Or 'sdk_integration.py' for automatic handling")
    print("="*60 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        url = sys.argv[1]
        task = sys.argv[2] if len(sys.argv) > 2 else "check console logs and verify page loaded"
    else:
        url = "https://google.com"
        task = "check console logs and verify page loaded"

    demo_test(url, task)
