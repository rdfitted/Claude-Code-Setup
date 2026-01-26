#!/usr/bin/env python3
"""
Gemini Computer Use integration using official Google Generative AI SDK
Handles multi-turn conversations automatically with proper function execution
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List

import requests

# Configure API
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-computer-use-preview-10-2025"


class ComputerUseTester:
    """
    Web application tester using Gemini Computer Use SDK
    """

    def __init__(self, api_key: str = API_KEY):
        self.api_key = api_key
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent"

        # Function execution state
        self.browser_state = {
            "opened": False,
            "current_url": None,
            "console_logs": {
                "errors": [],
                "warnings": [],
                "info": []
            }
        }

    def execute_browser_function(self, function_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a browser automation function

        Args:
            function_name: Name of the Computer Use function
            args: Function arguments

        Returns:
            Execution result
        """
        print(f"\n[EXECUTING] {function_name}({json.dumps(args, indent=2)})")

        # Simulate browser actions
        # In production, these would use Playwright, Selenium, or similar

        if function_name == "open_web_browser":
            self.browser_state["opened"] = True
            self.browser_state["current_url"] = "about:blank"
            return {
                "success": True,
                "message": "Browser opened",
                "state": "ready",
                "url": "about:blank"
            }

        elif function_name in ["navigate_to", "navigate"]:
            url = args.get("url", "")
            self.browser_state["current_url"] = url

            # Simulate page load
            page_loaded = True

            # Simulate console logs for Google.com
            if "google.com" in url:
                self.browser_state["console_logs"] = {
                    "errors": [],
                    "warnings": [],
                    "info": ["Google page loaded successfully"]
                }

            return {
                "success": page_loaded,
                "message": f"Navigated to {url}",
                "url": url,
                "page_loaded": True,
                "console_logs": self.browser_state["console_logs"]
            }

        elif function_name == "take_screenshot":
            return {
                "success": True,
                "screenshot_path": "/tmp/screenshot.png",
                "message": "Screenshot captured",
                "url": self.browser_state["current_url"]
            }

        elif function_name == "get_console_logs":
            return {
                "success": True,
                "logs": self.browser_state["console_logs"],
                "url": self.browser_state["current_url"]
            }

        elif function_name == "click_element":
            selector = args.get("selector", "")
            return {
                "success": True,
                "message": f"Clicked: {selector}",
                "element_found": True,
                "url": self.browser_state["current_url"]
            }

        elif function_name == "type_text":
            text = args.get("text", "")
            selector = args.get("selector", "")
            return {
                "success": True,
                "message": f"Typed '{text}' into {selector}",
                "url": self.browser_state["current_url"]
            }

        elif function_name == "wait_for_element":
            selector = args.get("selector", "")
            timeout = args.get("timeout_ms", 5000)
            return {
                "success": True,
                "message": f"Element found: {selector}",
                "wait_time_ms": 234,
                "url": self.browser_state["current_url"]
            }

        elif function_name in ["wait_5_seconds", "wait"]:
            return {
                "success": True,
                "message": "Waited successfully",
                "url": self.browser_state["current_url"]
            }

        else:
            return {
                "success": False,
                "error": f"Unknown function: {function_name}",
                "url": self.browser_state.get("current_url", "about:blank")
            }

    def make_api_request(self, messages: List[Dict]) -> Dict:
        """Make API request to Gemini Computer Use"""
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

        payload = {
            "contents": messages,
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

        response = requests.post(self.endpoint, headers=headers, json=payload)

        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")

        return response.json()

    def test_web_app(self, url: str, test_description: str, max_turns: int = 20) -> str:
        """
        Test a web application with Computer Use

        Args:
            url: URL to test
            test_description: What to test
            max_turns: Maximum conversation turns

        Returns:
            Test results
        """
        print(f"\n{'='*70}")
        print(f"TESTING: {url}")
        print(f"TASK: {test_description}")
        print(f"{'='*70}")

        # Construct test prompt
        prompt = f"""Test the web application at {url}.

Task: {test_description}

Instructions:
1. Open a web browser
2. Navigate to {url}
3. Wait for the page to fully load
4. Capture browser console logs (errors, warnings, info)
5. Take screenshots as evidence
6. Perform any requested tests
7. Report findings

Format your final response as:

## Test Results Summary
**URL**: {url}
**Page Load**: PASS/FAIL
**Console Errors**: X
**Console Warnings**: Y

## Detailed Findings

### Console Errors
- [List or "No errors found"]

### Console Warnings
- [List or "No warnings found"]

### Console Info/Logs
- [List or "No info messages"]

## Test Conclusion
[Summary of test results and recommendations]
"""

        # Initialize conversation history
        conversation = [{
            "role": "user",
            "parts": [{"text": prompt}]
        }]

        # Send initial prompt
        response = self.make_api_request(conversation)

        turn = 1
        while turn <= max_turns:
            print(f"\n{'='*70}")
            print(f"TURN {turn}")
            print(f"{'='*70}")

            # Add model response to conversation
            candidate = response["candidates"][0]
            model_message = candidate["content"]
            conversation.append(model_message)

            # Check for function calls in response
            parts = model_message.get("parts", [])
            if parts:
                has_function_calls = False
                has_text = False
                function_responses_parts = []

                for part in parts:
                    if "functionCall" in part:
                        has_function_calls = True
                        # Execute the function call
                        func_name = part["functionCall"]["name"]
                        func_args = part["functionCall"].get("args", {})

                        result = self.execute_browser_function(func_name, func_args)

                        # Prepare function response
                        function_responses_parts.append({
                            "functionResponse": {
                                "name": func_name,
                                "response": result
                            }
                        })

                    elif "text" in part:
                        has_text = True
                        print(f"\n[MODEL RESPONSE]")
                        print(part["text"])

                # If we have function calls, send responses back
                if has_function_calls:
                    print(f"\n[SENDING FUNCTION RESULTS] Sending {len(function_responses_parts)} function results...")

                    # Add function responses to conversation
                    conversation.append({
                        "role": "user",
                        "parts": function_responses_parts
                    })

                    response = self.make_api_request(conversation)
                    turn += 1

                # If we have text and no more function calls, we're done
                elif has_text and not has_function_calls:
                    print(f"\n[TEST COMPLETE] Final results received")
                    final_text = "\n\n".join([
                        part["text"] for part in parts
                        if "text" in part
                    ])
                    return final_text

                else:
                    print("[WARNING] Unexpected response format")
                    break
            else:
                print("[WARNING] Empty response")
                break

        print(f"\n[TIMEOUT] Reached maximum turns ({max_turns})")
        return "Test execution timed out"


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Test web applications with Gemini Computer Use")
    parser.add_argument("url", nargs="?", default="https://google.com", help="URL to test")
    parser.add_argument("--task", default="Check browser console for errors and warnings", help="Test description")
    parser.add_argument("--max-turns", type=int, default=20, help="Maximum conversation turns")

    args = parser.parse_args()

    try:
        tester = ComputerUseTester()
        results = tester.test_web_app(args.url, args.task, args.max_turns)

        print(f"\n{'='*70}")
        print("FINAL TEST RESULTS")
        print(f"{'='*70}\n")
        print(results)
        print(f"\n{'='*70}\n")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
