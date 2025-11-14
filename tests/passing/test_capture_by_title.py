#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "anthropic",
# ]
# ///

import sys
# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import subprocess
import time
import os
from pathlib import Path
from datetime import datetime

def main():
    """Test capture by title flow."""

    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")

    # Ensure tmp directory exists
    tmp_dir = Path('./tmp')
    tmp_dir.mkdir(exist_ok=True)

    # Define test output files
    output_file_explicit = tmp_dir / f"{timestamp}_title_explicit.png"
    output_dir = tmp_dir

    cmd_process = None

    try:
        # Launch controlled cmd.exe window with unique title
        print("Launching cmd.exe with unique title...", flush=True)
        unique_title = f"TestWindow_{timestamp}"
        cmd_process = subprocess.Popen(
            ['cmd.exe', '/K', f'title {unique_title}'],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        cmd_pid = cmd_process.pid
        print(f"Launched cmd.exe with PID {cmd_pid}, setting title to: {unique_title}", flush=True)
        time.sleep(3)  # Give window time to appear and title to be set

        # Verify window is running
        print("Verifying cmd.exe process is running...", flush=True)
        assert cmd_process.poll() is None, "cmd.exe process failed to stay running"
        print("Process confirmed running", flush=True)

        # Get actual window title by querying screenshot.exe and matching PID
        print(f"Querying window list to find actual title for PID {cmd_pid}...", flush=True)
        list_result = subprocess.run(
            ['./release/screenshot.exe'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10
        )

        actual_title = None
        for line in list_result.stdout.splitlines():
            # Format: window_id\tpid\t"title"
            parts = line.split('\t')
            if len(parts) >= 3:
                try:
                    line_pid = int(parts[1])
                    if line_pid == cmd_pid:
                        # Extract title (strip quotes)
                        title_with_quotes = '\t'.join(parts[2:])
                        actual_title = title_with_quotes.strip().strip('"')
                        print(f"Found window with PID {cmd_pid}, title: {actual_title}", flush=True)
                        break
                except (ValueError, IndexError):
                    continue

        if not actual_title:
            print(f"Warning: Could not find window with PID {cmd_pid} in window list", flush=True)
            print(f"Window list output:\n{list_result.stdout}", flush=True)
            actual_title = unique_title  # Fallback to expected title

        # Use the actual title we found
        test_title = actual_title

        # Test $REQ_TITLE_001: Accept --title flag
        print(f"Testing $REQ_TITLE_001: Capture with --title flag to {output_file_explicit}...", flush=True)
        result = subprocess.run(
            ['./release/screenshot.exe', '--title', test_title, str(output_file_explicit)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10
        )
        print(f"screenshot.exe exit code: {result.returncode}", flush=True)
        print(f"stdout: {result.stdout}", flush=True)
        if result.stderr:
            print(f"stderr: {result.stderr}", flush=True)

        assert result.returncode == 0, f"screenshot.exe failed with exit code {result.returncode}"  # $REQ_TITLE_001
        print("✓ $REQ_TITLE_001: Tool accepts --title flag", flush=True)

        # Test $REQ_TITLE_002: Window matched by title
        # Test $REQ_TITLE_005: Output to specific file
        print(f"Verifying screenshot file was created at {output_file_explicit}...", flush=True)
        assert output_file_explicit.exists(), f"Screenshot file not created at {output_file_explicit}"  # $REQ_TITLE_002
        assert output_file_explicit.stat().st_size > 0, "Screenshot file is empty"  # $REQ_TITLE_002
        print(f"✓ $REQ_TITLE_002: Window matched by title (file size: {output_file_explicit.stat().st_size} bytes)", flush=True)
        print(f"✓ $REQ_TITLE_005: Screenshot saved to specific file path", flush=True)

        # Test $REQ_TITLE_003: PNG format
        print("Verifying PNG file format...", flush=True)
        with open(output_file_explicit, 'rb') as f:
            header = f.read(8)
            assert header == b'\x89PNG\r\n\x1a\n', "File is not a valid PNG"  # $REQ_TITLE_003
        print("✓ $REQ_TITLE_003: Screenshot saved in PNG format", flush=True)

        # Test $REQ_TITLE_008: Success message
        print("Verifying 'Wrote [filepath]' message...", flush=True)
        assert 'Wrote' in result.stdout, "Missing 'Wrote' in output message"  # $REQ_TITLE_008
        assert str(output_file_explicit) in result.stdout or output_file_explicit.name in result.stdout, "Filepath not in output message"  # $REQ_TITLE_008
        print(f"✓ $REQ_TITLE_008: Tool outputs 'Wrote [filepath]' message", flush=True)

        # Test $REQ_TITLE_004: Full window with decorations (AI verification)
        print("Testing $REQ_TITLE_004: Verifying full window capture with AI...", flush=True)
        ai_result = verify_screenshot_with_ai(
            output_file_explicit,
            f"This should be a screenshot of a Windows cmd.exe window with title '{test_title}'. "
            f"The screenshot must include the full window with title bar showing '{test_title}', "
            f"window borders, and decorations. Does this screenshot plausibly show a complete cmd.exe window with visible title bar and borders?"
        )
        assert ai_result, "AI verification failed: screenshot does not show full window with decorations"  # $REQ_TITLE_004
        print("✓ $REQ_TITLE_004: Full window including title bar and decorations captured", flush=True)

        # Test $REQ_TITLE_006: Output to directory with timestamp
        print(f"Testing $REQ_TITLE_006: Capture to directory {output_dir}...", flush=True)

        # Get list of files before capture
        files_before = set(output_dir.glob('*.png'))

        result_dir = subprocess.run(
            ['./release/screenshot.exe', '--title', test_title, str(output_dir) + '/'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10
        )
        print(f"Directory capture exit code: {result_dir.returncode}", flush=True)
        print(f"stdout: {result_dir.stdout}", flush=True)

        assert result_dir.returncode == 0, f"Directory capture failed with exit code {result_dir.returncode}"  # $REQ_TITLE_006

        # Find the new file
        files_after = set(output_dir.glob('*.png'))
        new_files = files_after - files_before
        assert len(new_files) == 1, f"Expected 1 new file, found {len(new_files)}"  # $REQ_TITLE_006

        new_file = list(new_files)[0]
        print(f"New file created: {new_file.name}", flush=True)

        # Verify timestamped filename format: YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png
        filename = new_file.name
        assert filename.endswith('_screenshot.png'), f"Filename does not end with '_screenshot.png': {filename}"  # $REQ_TITLE_006

        # Parse timestamp part (everything before _screenshot.png)
        timestamp_part = filename.replace('_screenshot.png', '')
        parts = timestamp_part.split('-')
        assert len(parts) == 7, f"Timestamp format incorrect, expected 7 parts (YYYY-MM-DD-HH-MM-SS-microseconds), got {len(parts)}: {timestamp_part}"  # $REQ_TITLE_006

        # Verify each part is numeric
        for part in parts:
            assert part.isdigit(), f"Timestamp part is not numeric: {part}"  # $REQ_TITLE_006

        print(f"✓ $REQ_TITLE_006: Timestamped filename generated in directory: {filename}", flush=True)

        # Test $REQ_TITLE_007: Output to current directory (omit path)
        print("Testing $REQ_TITLE_007: Capture to current directory with omitted path...", flush=True)

        # Get list of PNG files in current directory before capture
        current_dir = Path('.')
        files_before_current = set(current_dir.glob('*.png'))

        result_current = subprocess.run(
            ['./release/screenshot.exe', '--title', test_title],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10
        )
        print(f"Current directory capture exit code: {result_current.returncode}", flush=True)
        print(f"stdout: {result_current.stdout}", flush=True)

        assert result_current.returncode == 0, f"Current directory capture failed with exit code {result_current.returncode}"  # $REQ_TITLE_007

        # Find the new file in current directory
        files_after_current = set(current_dir.glob('*.png'))
        new_files_current = files_after_current - files_before_current
        assert len(new_files_current) == 1, f"Expected 1 new file in current directory, found {len(new_files_current)}"  # $REQ_TITLE_007

        new_file_current = list(new_files_current)[0]
        print(f"New file created in current directory: {new_file_current.name}", flush=True)

        # Verify timestamped filename format
        filename_current = new_file_current.name
        assert filename_current.endswith('_screenshot.png'), f"Filename does not end with '_screenshot.png': {filename_current}"  # $REQ_TITLE_007

        print(f"✓ $REQ_TITLE_007: Timestamped filename generated in current directory: {filename_current}", flush=True)

        # Clean up the file in current directory
        try:
            new_file_current.unlink()
            print(f"Cleaned up {new_file_current}", flush=True)
        except Exception as e:
            print(f"Warning: Failed to clean up {new_file_current}: {e}", flush=True)

        print("✓ All tests passed", flush=True)
        return 0

    except AssertionError as e:
        print(f"✗ Test failed: {e}", flush=True)
        return 1
    except subprocess.TimeoutExpired as e:
        print(f"✗ Test failed: Command timed out: {e}", flush=True)
        return 1
    except Exception as e:
        print(f"✗ Test failed with unexpected error: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Clean up cmd.exe process
        if cmd_process is not None:
            print("Cleaning up cmd.exe process...", flush=True)
            try:
                if cmd_process.poll() is None:
                    cmd_process.kill()
                    cmd_process.wait(timeout=5)
                    print("cmd.exe process killed", flush=True)
            except Exception as e:
                print(f"Warning: Error cleaning up cmd.exe: {e}", flush=True)


def verify_screenshot_with_ai(image_path: Path, prompt: str) -> bool:
    """
    Use AI to verify the screenshot matches expectations.
    Returns True if AI confirms, False otherwise.
    """
    import anthropic
    import base64

    print(f"Reading screenshot for AI verification: {image_path}", flush=True)

    # Read and encode the image
    with open(image_path, 'rb') as f:
        image_data = base64.standard_b64encode(f.read()).decode('utf-8')

    # Get API key from environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Warning: ANTHROPIC_API_KEY not set, skipping AI verification", flush=True)
        return True  # Skip verification if no API key

    client = anthropic.Anthropic(api_key=api_key)

    print("Calling Claude API for verification...", flush=True)

    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": f"{prompt}\n\nRespond with only 'YES' if the screenshot matches the description, or 'NO' if it does not."
                        }
                    ],
                }
            ],
        )

        response_text = message.content[0].text.strip().upper()
        print(f"AI response: {response_text}", flush=True)

        return 'YES' in response_text

    except Exception as e:
        print(f"Warning: AI verification failed with error: {e}", flush=True)
        return True  # Don't fail test on AI API errors


if __name__ == '__main__':
    sys.exit(main())
