#!/usr/bin/env python3
"""
Gemini Computer Use - Official SDK Implementation
Gemini AI controls a REAL local browser using Playwright
Uses official google-genai SDK as per Google's documentation
"""

import os
import sys
import time
import base64
from typing import Dict, Any, List
from pathlib import Path

from google import genai
from google.genai import types
from google.genai.types import Content, Part
from playwright.sync_api import sync_playwright, Page, Browser

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Configure API
API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.5-computer-use-preview-10-2025"

# Screen dimensions (as per Google docs)
SCREEN_WIDTH = 1440
SCREEN_HEIGHT = 900


class GeminiBrowserController:
    """
    Gemini Computer Use controller with REAL visible browser
    Uses official google-genai SDK
    """

    def __init__(self, api_key: str = API_KEY, headless: bool = False, slow_mo: int = 500):
        self.api_key = api_key
        self.headless = headless
        self.slow_mo = slow_mo

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Playwright state
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # Console logs
        self.console_logs = []

    def start_browser(self):
        """Start Playwright browser"""
        print(f"[BROWSER] Launching {'headless' if self.headless else 'VISIBLE'} browser...")

        self.playwright = sync_playwright().start()

        # Launch browser with slow motion for visibility
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo
        )

        # Create context with specified dimensions (as per Google docs)
        self.context = self.browser.new_context(
            viewport={"width": SCREEN_WIDTH, "height": SCREEN_HEIGHT}
        )

        self.page = self.context.new_page()

        # Capture console logs
        self.page.on('console', lambda msg: self.console_logs.append({
            'type': msg.type,
            'text': msg.text
        }))

        print("[BROWSER] ✓ Browser ready")
        print(f"[BROWSER] Viewport: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

    def capture_screenshot(self) -> str:
        """Capture screenshot and return base64 encoded image"""
        screenshot_bytes = self.page.screenshot()
        return base64.b64encode(screenshot_bytes).decode('utf-8')

    def get_current_url(self) -> str:
        """Get current page URL"""
        return self.page.url if self.page else "about:blank"

    def denormalize_x(self, x: int) -> int:
        """Convert normalized x coordinate (0-1000) to actual pixel coordinate"""
        return int(int(x) / 1000 * SCREEN_WIDTH)

    def denormalize_y(self, y: int) -> int:
        """Convert normalized y coordinate (0-1000) to actual pixel coordinate"""
        return int(int(y) / 1000 * SCREEN_HEIGHT)

    def execute_action(self, action_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute browser action based on Gemini's Computer Use function call

        According to Google docs, Computer Use has predefined actions:
        - navigate, click, type_text, wait, scroll, etc.

        Args:
            action_name: Computer Use action name
            args: Action arguments

        Returns:
            Execution result
        """
        print(f"\n[EXECUTING] {action_name}({args})")

        # Check for safety decision in args
        safety_decision = args.get("safety_decision")
        if safety_decision:
            print(f"[SAFETY] Decision: {safety_decision.get('decision')}")
            print(f"[SAFETY] Explanation: {safety_decision.get('explanation')}")

        try:
            # Navigate action
            if action_name in ["navigate", "navigate_to"]:
                url = args.get("url", "")
                print(f"  → Navigating to: {url}")
                self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(1)  # Let page settle
                return {
                    "success": True,
                    "message": f"Navigated to {url}",
                    "url": self.get_current_url()
                }

            # Click action
            elif action_name in ["click", "mouse_click", "click_at"]:
                x = args.get("x")
                y = args.get("y")
                if x is not None and y is not None:
                    # Denormalize coordinates from 0-1000 to actual pixels
                    actual_x = self.denormalize_x(x)
                    actual_y = self.denormalize_y(y)
                    print(f"  → Clicking at normalized ({x}, {y}) = actual ({actual_x}, {actual_y})")
                    self.page.mouse.click(actual_x, actual_y)
                    time.sleep(0.5)
                    return {
                        "success": True,
                        "message": f"Clicked at normalized ({x}, {y}) = actual ({actual_x}, {actual_y})",
                        "url": self.get_current_url()
                    }
                else:
                    return {"success": False, "error": "Missing x,y coordinates"}

            # Type text action (combined click+type)
            elif action_name in ["type", "type_text", "keyboard_type", "type_text_at"]:
                text = args.get("text", "")
                press_enter = args.get("press_enter", False)

                # If coordinates provided, click first
                x = args.get("x")
                y = args.get("y")
                if x is not None and y is not None:
                    # Denormalize coordinates from 0-1000 to actual pixels
                    actual_x = self.denormalize_x(x)
                    actual_y = self.denormalize_y(y)
                    print(f"  → Clicking at normalized ({x}, {y}) = actual ({actual_x}, {actual_y}) first...")
                    self.page.mouse.click(actual_x, actual_y)
                    time.sleep(0.3)

                    # Try to focus an editable element at the click point
                    try:
                        focused = self.page.evaluate("""
                            ([x, y]) => {
                              const el = document.elementFromPoint(x, y);
                              if (!el) return false;
                              const target = el.closest('input,textarea,[contenteditable="true"],[role="searchbox"],[type="search"]');
                              if (!target) return false;
                              target.focus();
                              try {
                                if (target.select) target.select();
                                else if (target.setSelectionRange && typeof target.value === 'string') {
                                  target.setSelectionRange(0, target.value.length);
                                }
                              } catch (_) {}
                              return true;
                            }
                        """, [actual_x, actual_y])

                        if focused:
                            print(f"  → Focused input element at ({actual_x}, {actual_y})")
                    except Exception as e:
                        print(f"  → Could not focus element: {e}")

                print(f"  → Typing: '{text}'")
                self.page.keyboard.type(text, delay=50)

                if press_enter:
                    print(f"  → Pressing Enter")
                    self.page.keyboard.press('Enter')

                time.sleep(0.5)
                return {
                    "success": True,
                    "message": f"Typed '{text}'" + (" and pressed Enter" if press_enter else ""),
                    "url": self.get_current_url()
                }

            # Press key action
            elif action_name in ["press_key", "key_press", "keyboard_press"]:
                key = args.get("key", "")
                print(f"  → Pressing key: {key}")
                self.page.keyboard.press(key)
                time.sleep(0.3)
                return {
                    "success": True,
                    "message": f"Pressed '{key}'",
                    "url": self.get_current_url()
                }

            # Browser navigation actions
            elif action_name in ["go_back", "back"]:
                print(f"  → Going back...")
                self.page.go_back(wait_until='domcontentloaded', timeout=10000)
                time.sleep(0.5)
                return {
                    "success": True,
                    "message": "Went back",
                    "url": self.get_current_url()
                }

            elif action_name in ["go_forward", "forward"]:
                print(f"  → Going forward...")
                self.page.go_forward(wait_until='domcontentloaded', timeout=10000)
                time.sleep(0.5)
                return {
                    "success": True,
                    "message": "Went forward",
                    "url": self.get_current_url()
                }

            # Wait action
            elif action_name in ["wait", "wait_seconds"]:
                seconds = args.get("seconds", 2)
                print(f"  → Waiting {seconds} seconds...")
                time.sleep(seconds)
                return {
                    "success": True,
                    "message": f"Waited {seconds}s",
                    "url": self.get_current_url()
                }

            # Scroll action
            elif action_name == "scroll":
                direction = args.get("direction", "down")
                amount = args.get("amount", 500)
                print(f"  → Scrolling {direction} by {amount}px")

                if direction == "down":
                    self.page.mouse.wheel(0, amount)
                elif direction == "up":
                    self.page.mouse.wheel(0, -amount)

                time.sleep(0.5)
                return {
                    "success": True,
                    "message": f"Scrolled {direction}",
                    "url": self.get_current_url()
                }

            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action_name}",
                    "url": self.get_current_url()
                }

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": self.get_current_url()
            }

    def run_task(self, initial_url: str, task: str, max_turns: int = 20):
        """
        Run Gemini Computer Use task with visible browser

        Args:
            initial_url: Starting URL
            task: Task description
            max_turns: Maximum conversation turns
        """
        print("=" * 70)
        print(f"GEMINI COMPUTER USE - OFFICIAL SDK IMPLEMENTATION")
        print(f"Initial URL: {initial_url}")
        print(f"TASK: {task}")
        print("=" * 70)

        try:
            # Start browser
            self.start_browser()

            # Navigate to initial URL
            print(f"\n[INITIAL] Navigating to {initial_url}...")
            self.page.goto(initial_url, wait_until='domcontentloaded', timeout=30000)
            time.sleep(1)

            # Capture initial screenshot
            print("[SCREENSHOT] Capturing initial state...")
            initial_screenshot = self.capture_screenshot()

            # Configure Computer Use tool
            config = types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        computer_use=types.ComputerUse(
                            environment=types.Environment.ENVIRONMENT_BROWSER
                        )
                    )
                ],
                temperature=0.2,
            )

            # Build conversation history
            conversation_history = []

            # Initial user message with screenshot and task
            initial_message = Content(
                role="user",
                parts=[
                    Part(text=f"You are controlling a web browser. Complete this task: {task}\n\nCurrent URL: {self.get_current_url()}\n\nUse the available Computer Use functions to interact with the browser."),
                    Part(
                        inline_data=types.Blob(
                            mime_type="image/png",
                            data=initial_screenshot
                        )
                    )
                ]
            )
            conversation_history.append(initial_message)

            turn = 1
            while turn <= max_turns:
                print(f"\n{'='*70}")
                print(f"TURN {turn}")
                print(f"{'='*70}")

                # Generate content with Computer Use
                response = self.client.models.generate_content(
                    model=MODEL_NAME,
                    contents=conversation_history,
                    config=config
                )

                # Debug: Print FULL response structure
                print(f"\n[DEBUG] ========== FULL RESPONSE DEBUG ==========")
                print(f"[DEBUG] Response type: {type(response)}")
                print(f"[DEBUG] Response attributes: {dir(response)}")
                if response.candidates:
                    print(f"[DEBUG] Number of candidates: {len(response.candidates)}")
                    for idx, candidate in enumerate(response.candidates):
                        print(f"\n[DEBUG] --- Candidate {idx} ---")
                        print(f"[DEBUG] Candidate type: {type(candidate)}")
                        print(f"[DEBUG] Candidate attributes: {dir(candidate)}")
                        if candidate.content:
                            print(f"[DEBUG] Content role: {candidate.content.role}")
                            print(f"[DEBUG] Content parts count: {len(candidate.content.parts)}")
                            for part_idx, part in enumerate(candidate.content.parts):
                                print(f"\n[DEBUG] ----- Part {part_idx} -----")
                                print(f"[DEBUG] Part type: {type(part)}")
                                print(f"[DEBUG] Part attributes: {dir(part)}")
                                if hasattr(part, 'text') and part.text:
                                    print(f"[DEBUG] Part has TEXT: {part.text[:200]}...")
                                if hasattr(part, 'function_call') and part.function_call:
                                    print(f"[DEBUG] Part has FUNCTION_CALL!")
                                    print(f"[DEBUG] Function call type: {type(part.function_call)}")
                                    print(f"[DEBUG] Function call attributes: {dir(part.function_call)}")
                                    print(f"[DEBUG] Function name: {part.function_call.name}")
                                    print(f"[DEBUG] Function args: {dict(part.function_call.args) if part.function_call.args else {}}")
                print(f"[DEBUG] ==========================================\n")

                # Add model's response to conversation
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    model_content = candidate.content
                    conversation_history.append(model_content)

                    # Process parts in the response
                    has_function_calls = False
                    has_text = False
                    function_results = []

                    for part in model_content.parts:
                        # Check for text
                        if part.text:
                            has_text = True
                            print(f"\n[GEMINI TEXT]")
                            print(part.text)

                        # Check for function calls
                        if part.function_call:
                            has_function_calls = True
                            func_call = part.function_call
                            func_name = func_call.name
                            func_args = dict(func_call.args) if func_call.args else {}

                            # Execute the action
                            result = self.execute_action(func_name, func_args)

                            # Check if there was a safety decision that needs acknowledgment
                            safety_decision = func_args.get("safety_decision")
                            if safety_decision:
                                # Add safety decision acknowledgment to response
                                result["safety_decision_acknowledgment"] = {
                                    "decision": safety_decision.get("decision"),
                                    "acknowledged": True
                                }

                            # Build function response
                            function_results.append(
                                Part(
                                    function_response=types.FunctionResponse(
                                        name=func_name,
                                        response=result
                                    )
                                )
                            )

                    # If there were function calls, send results back with screenshot
                    if has_function_calls:
                        # Capture new screenshot after actions
                        time.sleep(0.5)  # Let page settle
                        new_screenshot = self.capture_screenshot()

                        # Add function responses and screenshot
                        function_results.append(
                            Part(
                                inline_data=types.Blob(
                                    mime_type="image/png",
                                    data=new_screenshot
                                )
                            )
                        )

                        # Add to conversation
                        conversation_history.append(
                            Content(
                                role="user",
                                parts=function_results
                            )
                        )

                        print(f"\n[SENDING] Function results + screenshot back to Gemini...")
                        turn += 1

                    # If only text (no function calls), task is complete
                    elif has_text:
                        print(f"\n[COMPLETE] Task finished!")
                        final_text = "\n".join([part.text for part in model_content.parts if part.text])

                        # Show console logs
                        self.show_console_logs()

                        # Keep browser open
                        print(f"\n[BROWSER] Keeping browser open for 10 seconds...")
                        print("         (Press Ctrl+C to close immediately)")
                        time.sleep(10)

                        return final_text

                    else:
                        print("[WARNING] Response has no text or function calls")
                        break

                else:
                    print("[ERROR] No candidates in response")
                    break

            print(f"\n[TIMEOUT] Maximum turns reached ({max_turns})")
            return "Task execution timed out"

        except KeyboardInterrupt:
            print("\n[INTERRUPTED] User stopped execution")
            return "Task interrupted by user"

        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {e}"

        finally:
            print("\n[CLEANUP] Closing browser...")
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()

    def show_console_logs(self):
        """Display captured console logs"""
        print("\n" + "=" * 70)
        print("BROWSER CONSOLE LOGS")
        print("=" * 70)

        if not self.console_logs:
            print("✓ No console messages")
            return

        errors = [log for log in self.console_logs if log['type'] == 'error']
        warnings = [log for log in self.console_logs if log['type'] == 'warning']
        others = [log for log in self.console_logs if log['type'] not in ['error', 'warning']]

        if errors:
            print(f"\n🔴 ERRORS ({len(errors)}):")
            for log in errors[:10]:
                print(f"  - {log['text']}")

        if warnings:
            print(f"\n⚠️  WARNINGS ({len(warnings)}):")
            for log in warnings[:10]:
                print(f"  - {log['text']}")

        if others:
            print(f"\n📋 OTHER ({len(others)}):")
            for log in others[:5]:
                print(f"  [{log['type']}] {log['text']}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Gemini Computer Use with official SDK and VISIBLE browser'
    )
    parser.add_argument('url', help='Initial URL to navigate to')
    parser.add_argument('--task', '-t', required=True, help='Task description')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--slow', type=int, default=500, help='Slow motion delay (ms)')
    parser.add_argument('--max-turns', type=int, default=20, help='Maximum turns')

    args = parser.parse_args()

    controller = GeminiBrowserController(
        headless=args.headless,
        slow_mo=args.slow
    )

    result = controller.run_task(args.url, args.task, args.max_turns)

    print("\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)
    print(result)
    print("=" * 70)


if __name__ == '__main__':
    main()
