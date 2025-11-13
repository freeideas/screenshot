#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Screenshot-based test script for GUI applications using PID capture.

Launches an application, waits for it to render, captures a screenshot by PID,
kills the process, and uses AI to verify the visual output matches expectations.

IMPORTANT: --launch must be the LAST argument on the command line.
Everything after --launch is used as the command to execute.

Usage:
    echo "verify the window shows hello world" | test-screenshot.py --launch ./app.exe --url test.html
    test-screenshot.py --wait 3 --launch ./myapp.exe
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path
from datetime import datetime

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add the-system/scripts to path for prompt_agentic_coder
sys.path.insert(0, str(Path(__file__).parent))
from prompt_agentic_coder import get_ai_response_text


def capture_screenshot_by_pid(pid, output_path):
    """Capture screenshot of the process by PID using screenshot.exe --pid."""
    screenshot_exe = Path('./release/screenshot.exe')
    if not screenshot_exe.exists():
        # Try alternative location
        screenshot_exe = Path('./the-system/bin/screenshot.exe')

    if not screenshot_exe.exists():
        raise RuntimeError(f"screenshot.exe not found at ./release/ or ./the-system/bin/")

    result = subprocess.run(
        [str(screenshot_exe), '--pid', str(pid), str(output_path)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.returncode != 0:
        raise RuntimeError(f"screenshot.exe failed: {result.stderr}")

    if not output_path.exists():
        raise RuntimeError(f"Screenshot file was not created: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Screenshot-based GUI test with AI verification (PID-based)',
        epilog='The --launch flag must be LAST. Everything after it becomes the command to execute.'
    )
    parser.add_argument(
        '--wait',
        type=int,
        default=5,
        help='Seconds to wait after launching before capturing screenshot (default: 5)'
    )
    parser.add_argument(
        '--prompt-file',
        default='-',
        help='File containing AI prompt, or "-" for stdin (default: stdin)'
    )
    parser.add_argument(
        '--launch',
        nargs=argparse.REMAINDER,
        required=True,
        help='Command and arguments to launch (MUST be last argument)'
    )

    args = parser.parse_args()

    # Read the prompt
    if args.prompt_file == '-':
        print("Reading prompt from stdin...", file=sys.stderr, flush=True)
        prompt = sys.stdin.read()
    else:
        prompt_path = Path(args.prompt_file)
        if not prompt_path.exists():
            print(f"Error: Prompt file not found: {prompt_path}", file=sys.stderr)
            sys.exit(1)
        prompt = prompt_path.read_text(encoding='utf-8')

    if not prompt.strip():
        print("Error: Empty prompt provided", file=sys.stderr)
        sys.exit(1)

    # Ensure tmp directory exists
    tmp_dir = Path('./tmp')
    tmp_dir.mkdir(exist_ok=True)

    # Validate launch command
    launch_cmd = args.launch
    if not launch_cmd:
        print("Error: No launch command provided after --launch", file=sys.stderr)
        sys.exit(1)

    # Launch the application
    print(f"Launching: {' '.join(launch_cmd)}", file=sys.stderr, flush=True)
    try:
        proc = subprocess.Popen(
            launch_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        pid = proc.pid
        print(f"Process launched with PID: {pid}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"Error: Failed to launch process: {e}", file=sys.stderr)
        sys.exit(1)

    # Wait for the application to render
    print(f"Waiting {args.wait} seconds for window to render...", file=sys.stderr, flush=True)
    time.sleep(args.wait)

    # Check if process is still alive
    poll_result = proc.poll()
    if poll_result is not None:
        # Process died
        stdout, stderr = proc.communicate()
        print("\n" + "="*60, file=sys.stderr)
        print("AUTOMATIC FAIL: Process died before screenshot could be captured", file=sys.stderr)
        print(f"Process exited with code: {poll_result}", file=sys.stderr)
        if stdout:
            print(f"\nStdout:\n{stdout.decode('utf-8', errors='replace')}", file=sys.stderr)
        if stderr:
            print(f"\nStderr:\n{stderr.decode('utf-8', errors='replace')}", file=sys.stderr)
        print("="*60, file=sys.stderr)
        sys.exit(1)

    # Generate screenshot filename
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    screenshot_name = f"{timestamp}_pid-{pid}_test.png"
    screenshot_path = tmp_dir / screenshot_name

    # Capture screenshot
    try:
        print(f"Capturing screenshot to {screenshot_path}...", file=sys.stderr, flush=True)
        capture_screenshot_by_pid(pid, screenshot_path)
        print(f"Screenshot saved: {screenshot_path}", file=sys.stderr, flush=True)
    except Exception as e:
        print(f"\nError capturing screenshot: {e}", file=sys.stderr)
        # Kill process before exiting
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
        sys.exit(1)

    # Kill the process now that we have the screenshot
    print("Terminating test process...", file=sys.stderr, flush=True)
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        print("Process didn't terminate cleanly, killing it...", file=sys.stderr, flush=True)
        proc.kill()
        proc.wait()

    # Build AI prompt with clear instructions
    full_prompt = f"""{prompt}

Screenshot file: {screenshot_path.absolute()}

IMPORTANT: Analyze the screenshot and determine if it matches the description above.
- If it matches, start your response with "YES" on its own line, followed by your explanation.
- If it does NOT match, start your response with "NO" on its own line, followed by your explanation.
"""

    # Get AI verification
    print("Sending screenshot to AI for verification...", file=sys.stderr, flush=True)
    try:
        ai_response = get_ai_response_text(
            full_prompt,
            report_type="screenshot_test"
        )
    except Exception as e:
        print(f"\nError getting AI response: {e}", file=sys.stderr)
        sys.exit(1)

    # Print AI response
    print("\n" + "="*60)
    print("AI ANALYSIS:")
    print("="*60)
    print(ai_response)
    print("="*60 + "\n")

    # Check for YES or NO in the response
    lines = ai_response.splitlines()
    result = None

    for line in lines:
        stripped = line.strip().upper()
        # Look for YES or NO at the start of a line
        if stripped.startswith('YES'):
            result = 'YES'
            break
        if stripped.startswith('NO'):
            result = 'NO'
            break

    # Exit based on result
    if result == 'YES':
        print("✓ Test PASSED: Image matches description", file=sys.stderr)
        sys.exit(0)
    elif result == 'NO':
        print("✗ Test FAILED: Image does not match description", file=sys.stderr)
        sys.exit(1)
    else:
        print("⚠ Test INCONCLUSIVE: No clear YES or NO found in AI response", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
