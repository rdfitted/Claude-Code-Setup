#!/usr/bin/env python3
"""
Multi-turn handler for Gemini Computer Use API
Executes function calls in a loop until test results are obtained
"""

import json
import requests
import base64
import os
from typing import Dict, List, Any

API_KEY = os.environ.get("GEMINI_API_KEY")
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-computer-use-preview-10-2025:generateContent"

class GeminiComputerUseHandler:
    """Handles multi-turn conversations with Gemini Computer Use model"""

    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.endpoint = API_ENDPOINT
        self.conversation_history = []
        self.screenshots = []

    def execute_function_call(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a Computer Use function call

        Args:
            function_name: Name of the function to execute
            args: Arguments for the function

        Returns:
            Function execution result
        """
        print(f"[EXECUTING] {function_name}({args})")

        # Simulate function execution
        # In a real implementation, these would actually execute browser actions

        if function_name == "open_web_browser":
            return {
                "success": True,
                "message": "Browser opened successfully",
                "screenshot": "base64_screenshot_data_here"
            }

        elif function_name == "navigate_to":
            url = args.get("url", "")
            return {
                "success": True,
                "message": f"Navigated to {url}",
                "url": url,
                "screenshot": "base64_screenshot_data_here"
            }

        elif function_name == "take_screenshot":
            return {
                "success": True,
                "screenshot": "base64_screenshot_data_here"
            }

        elif function_name == "get_console_logs":
            # Simulate console log capture
            return {
                "success": True,
                "logs": {
                    "errors": [],
                    "warnings": [],
                    "info": ["Page loaded successfully"]
                }
            }

        elif function_name == "click_element":
            selector = args.get("selector", "")
            return {
                "success": True,
                "message": f"Clicked element: {selector}",
                "screenshot": "base64_screenshot_data_here"
            }

        elif function_name == "type_text":
            text = args.get("text", "")
            selector = args.get("selector", "")
            return {
                "success": True,
                "message": f"Typed '{text}' into {selector}"
            }

        else:
            return {
                "success": False,
                "error": f"Unknown function: {function_name}"
            }

    def make_api_call(self, prompt: str = None, function_responses: List[Dict] = None) -> Dict:
        """
        Make API call to Gemini Computer Use

        Args:
            prompt: User prompt (for first turn)
            function_responses: Function execution results (for subsequent turns)

        Returns:
            API response
        """
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        # Build request contents
        if prompt and not self.conversation_history:
            # First turn
            contents = [{
                "role": "user",
                "parts": [{"text": prompt}]
            }]
        elif function_responses:
            # Subsequent turns with function results
            contents = self.conversation_history + [{
                "role": "user",
                "parts": [
                    {
                        "functionResponse": {
                            "name": resp["name"],
                            "response": resp["response"]
                        }
                    } for resp in function_responses
                ]
            }]
        else:
            raise ValueError("Must provide either prompt or function_responses")

        payload = {
            "contents": contents,
            "tools": [{
                "computer_use": {
                    "environment": "ENVIRONMENT_BROWSER"
                }
            }],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }

        response = requests.post(
            self.endpoint,
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

        return response.json()

    def run_test(self, test_prompt: str, max_turns: int = 20) -> str:
        """
        Run a complete test with multi-turn conversation

        Args:
            test_prompt: What to test
            max_turns: Maximum conversation turns

        Returns:
            Final test results
        """
        print(f"[STARTING TEST] {test_prompt}\n")

        # First API call with user prompt
        response = self.make_api_call(prompt=test_prompt)
        self.conversation_history.append({
            "role": "user",
            "parts": [{"text": test_prompt}]
        })

        turn = 1
        while turn <= max_turns:
            print(f"\n[TURN {turn}]")

            candidate = response["candidates"][0]
            finish_reason = candidate.get("finishReason", "UNKNOWN")

            # Add model response to history
            self.conversation_history.append(candidate["content"])

            # Check if we have function calls
            parts = candidate["content"]["parts"]
            function_calls = [p for p in parts if "functionCall" in p]
            text_parts = [p for p in parts if "text" in p]

            # If we have text response, we might be done
            if text_parts and not function_calls:
                final_text = "\n".join([p["text"] for p in text_parts])
                print(f"\n[FINAL RESULT]\n{final_text}")
                return final_text

            # Execute function calls
            if function_calls:
                function_responses = []
                for fc in function_calls:
                    func_name = fc["functionCall"]["name"]
                    func_args = fc["functionCall"].get("args", {})

                    # Execute the function
                    result = self.execute_function_call(func_name, func_args)

                    function_responses.append({
                        "name": func_name,
                        "response": result
                    })

                # Continue conversation with function results
                response = self.make_api_call(function_responses=function_responses)
                turn += 1
            else:
                # No function calls and no text, something went wrong
                print(f"[WARNING] No function calls or text in response. Finish reason: {finish_reason}")
                break

        print(f"\n[TIMEOUT] Reached maximum turns ({max_turns})")
        return "Test timed out - too many turns"


def main():
    """Example usage"""
    handler = GeminiComputerUseHandler()

    test_prompt = """Navigate to https://google.com and capture all browser console messages.
    Report any errors, warnings, or info messages you find. Take a screenshot of the page
    and verify it loaded correctly. Format your response as:

## Test Results Summary
**URL**: https://google.com
**Page Load**: PASS/FAIL

## Console Logs
### Errors
- [List errors or say "No errors found"]

### Warnings
- [List warnings or say "No warnings found"]

### Info
- [List info messages or say "No info messages"]

## Summary
[Brief summary of findings]"""

    results = handler.run_test(test_prompt, max_turns=20)

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print(results)


if __name__ == "__main__":
    main()
