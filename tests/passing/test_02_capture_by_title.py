#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import subprocess
import time
import re
import os
from pathlib import Path
from datetime import datetime

def main():
    """Test capture by window title flow."""

    cmd_process = None

    try:
        print("Starting capture by title test...", flush=True)

        # Ensure tmp directory exists
        os.makedirs('./tmp', exist_ok=True)
        print("Created ./tmp directory", flush=True)

        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
        print(f"Generated timestamp: {timestamp}", flush=True)

        # Launch controlled cmd.exe window with unique title
        unique_title = f"TestCaptureTitle_{timestamp}"
        print(f"Launching controlled cmd.exe window with title '{unique_title}'...", flush=True)
        cmd_process = subprocess.Popen(
            ['cmd.exe', '/K', f'title {unique_title}'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        cmd_pid = cmd_process.pid
        print(f"Launched cmd.exe with PID {cmd_pid} and title '{unique_title}'", flush=True)

        # Give window time to appear
        print("Waiting 2 seconds for window to appear...", flush=True)
        time.sleep(2)
        print("Window should now be visible", flush=True)

        # Test $REQ_TITLE_001: Accept --title <title> flag with string value
        print(f"Testing $REQ_TITLE_001: Capturing by title '{unique_title}'...", flush=True)
        output_path = f'./tmp/{timestamp}_capture-by-title.png'
        result = subprocess.run(
            ['./release/screenshot.exe', '--title', unique_title, output_path],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"Capture command completed with exit code {result.returncode}", flush=True)

        # Verify the command accepted the --title flag with string value
        assert result.returncode == 0, f"screenshot.exe failed with exit code {result.returncode}: {result.stderr}"  # $REQ_TITLE_001
        print("✓ $REQ_TITLE_001: --title flag accepted with string value", flush=True)

        # Test $REQ_TITLE_002: Capture window by title
        # Verify file was created (proves a window was captured)
        print(f"Checking if screenshot file exists at {output_path}...", flush=True)
        assert Path(output_path).exists(), f"Screenshot file not created at {output_path}"  # $REQ_TITLE_002
        print("✓ $REQ_TITLE_002: Screenshot captured by title", flush=True)

        # Test $REQ_TITLE_004: Save to explicit file path
        # Verify file was saved to the exact location we specified
        assert Path(output_path).is_file(), "Screenshot is not a file"  # $REQ_TITLE_004
        assert Path(output_path).stat().st_size > 0, "Screenshot file is empty"  # $REQ_TITLE_004
        print("✓ $REQ_TITLE_004: Screenshot saved to explicit file path", flush=True)

        # Test $REQ_TITLE_007: Output success message "Wrote [filepath]"
        print(f"Checking output message...", flush=True)
        print(f"stdout: {result.stdout}", flush=True)
        expected_message = f"Wrote {output_path}"
        assert expected_message in result.stdout, f"Expected '{expected_message}' in output, got: {result.stdout}"  # $REQ_TITLE_007
        print("✓ $REQ_TITLE_007: Output 'Wrote [filepath]' message", flush=True)

        # Test $REQ_TITLE_008: PNG format output
        print("Checking PNG format...", flush=True)
        with open(output_path, 'rb') as f:
            png_signature = f.read(8)
        expected_png_sig = b'\x89PNG\r\n\x1a\n'
        assert png_signature == expected_png_sig, f"Invalid PNG signature: {png_signature.hex()}"  # $REQ_TITLE_008
        print("✓ $REQ_TITLE_008: Screenshot is in PNG format", flush=True)

        # Test $REQ_TITLE_009: Capture full window with title bar and decorations
        # Use AI to verify window decorations are present
        print("Verifying full window capture with AI...", flush=True)
        ai_prompt = f"""I will provide a screenshot. Please examine it and tell me if it shows:
1. A title bar at the top
2. Window borders/decorations (edges around the window)
3. Content inside the window (the actual window area, not just decorations)

Does the screenshot show ALL THREE of these elements? Answer YES or NO.

Screenshot: @{output_path}"""

        ai_result = subprocess.run(
            ['uv', 'run', '--script', './the-system/scripts/prompt_agentic_coder.py'],
            input=ai_prompt,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"AI verification completed with exit code {ai_result.returncode}", flush=True)
        print(f"AI output: {ai_result.stdout[:200]}...", flush=True)

        # AI should return success and response should contain YES
        assert ai_result.returncode == 0, f"AI verification failed with exit code {ai_result.returncode}"  # $REQ_TITLE_009
        assert 'YES' in ai_result.stdout.upper(), f"AI did not confirm full window capture"  # $REQ_TITLE_009
        print("✓ $REQ_TITLE_009: Full window including title bar and decorations captured", flush=True)

        # Test $REQ_TITLE_005: Save to directory with timestamped filename
        print("Testing directory output with auto-generated filename...", flush=True)
        dir_result = subprocess.run(
            ['./release/screenshot.exe', '--title', unique_title, './tmp/'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"Directory capture completed with exit code {dir_result.returncode}", flush=True)
        assert dir_result.returncode == 0, f"Directory capture failed: {dir_result.stderr}"  # $REQ_TITLE_005

        # Extract the generated filename from the output message
        match = re.search(r'Wrote (.*)', dir_result.stdout)
        assert match, f"Could not find 'Wrote' message in output: {dir_result.stdout}"  # $REQ_TITLE_005
        generated_path = match.group(1)
        print(f"Generated path: {generated_path}", flush=True)

        # Verify the filename matches the timestamped format
        filename = Path(generated_path).name
        print(f"Checking filename format: {filename}", flush=True)
        timestamp_pattern = r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d+_screenshot\.png'
        assert re.match(timestamp_pattern, filename), f"Filename doesn't match timestamp pattern: {filename}"  # $REQ_TITLE_005
        assert Path(generated_path).exists(), f"Generated file not found: {generated_path}"  # $REQ_TITLE_005
        print("✓ $REQ_TITLE_005: Screenshot saved to directory with timestamped filename", flush=True)

        # Test $REQ_TITLE_006: Save to current directory with timestamped filename (omit output path)
        print("Testing omitted output path (defaults to current directory)...", flush=True)
        omit_result = subprocess.run(
            ['./release/screenshot.exe', '--title', unique_title],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"Omitted path capture completed with exit code {omit_result.returncode}", flush=True)
        assert omit_result.returncode == 0, f"Omitted path capture failed: {omit_result.stderr}"  # $REQ_TITLE_006

        # Extract the generated filename
        match = re.search(r'Wrote (.*)', omit_result.stdout)
        assert match, f"Could not find 'Wrote' message in output: {omit_result.stdout}"  # $REQ_TITLE_006
        omitted_path = match.group(1)
        print(f"Omitted path result: {omitted_path}", flush=True)

        # Verify filename format and file exists
        omitted_filename = Path(omitted_path).name
        print(f"Checking omitted filename format: {omitted_filename}", flush=True)
        assert re.match(timestamp_pattern, omitted_filename), f"Filename doesn't match timestamp pattern: {omitted_filename}"  # $REQ_TITLE_006
        assert Path(omitted_path).exists(), f"Generated file not found: {omitted_path}"  # $REQ_TITLE_006
        print("✓ $REQ_TITLE_006: Screenshot saved to current directory with timestamped filename", flush=True)

        # Clean up the omitted path file (it's in current directory, not ./tmp)
        if Path(omitted_path).exists():
            print(f"Cleaning up test file: {omitted_path}", flush=True)
            Path(omitted_path).unlink()

        # Test $REQ_TITLE_003: Handle multiple windows with same title
        # Launch a second cmd.exe window with the same title
        print("Testing multiple windows with same title...", flush=True)
        cmd_process2 = subprocess.Popen(
            ['cmd.exe', '/K', f'title {unique_title}'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print(f"Launched second cmd.exe with PID {cmd_process2.pid} and same title", flush=True)
        time.sleep(1)

        # Capture by title -- should capture one of the two windows
        multi_output = f'./tmp/{timestamp}_multi-title.png'
        multi_result = subprocess.run(
            ['./release/screenshot.exe', '--title', unique_title, multi_output],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        print(f"Multi-window capture completed with exit code {multi_result.returncode}", flush=True)

        # Verify that one window was captured successfully (requirement says "one will be captured")
        assert multi_result.returncode == 0, f"Multi-window capture failed: {multi_result.stderr}"  # $REQ_TITLE_003
        assert Path(multi_output).exists(), f"Screenshot not created for multi-window scenario"  # $REQ_TITLE_003
        assert Path(multi_output).stat().st_size > 0, "Screenshot file is empty"  # $REQ_TITLE_003
        print("✓ $REQ_TITLE_003: One window captured when multiple windows share same title", flush=True)

        # Clean up second process
        if cmd_process2.poll() is None:
            print("Cleaning up second cmd.exe process...", flush=True)
            cmd_process2.kill()
            cmd_process2.wait(timeout=5)

        print("✓ All tests passed", flush=True)
        return 0

    except AssertionError as e:
        print(f"✗ Test failed: {e}", flush=True)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # CRITICAL: Clean up -- kill cmd.exe process(es)
        if cmd_process is not None and cmd_process.poll() is None:
            print("Cleaning up cmd.exe process...", flush=True)
            cmd_process.kill()
            try:
                cmd_process.wait(timeout=5)
                print("cmd.exe process terminated", flush=True)
            except subprocess.TimeoutExpired:
                print("Warning: cmd.exe did not terminate within timeout", flush=True)

if __name__ == '__main__':
    sys.exit(main())
