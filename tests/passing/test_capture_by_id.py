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
import re
from pathlib import Path
from datetime import datetime

def get_window_id_by_pid(screenshot_exe, pid):
    """Get window ID for a process by matching its PID in the window list."""
    print(f"Getting window list to find window with PID {pid}...", flush=True)

    result = subprocess.run(
        [screenshot_exe],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print(f"Failed to get window list: {result.stderr}", flush=True)
        return None

    # Parse window list: format is <window-id>\t<pid>\t"window title"
    for line in result.stdout.splitlines():
        # Skip header and empty lines
        if not line.strip() or line.startswith('Window ID'):
            continue

        # Split by tab
        parts = line.split('\t')
        if len(parts) >= 3:
            window_id = parts[0].strip()
            line_pid = parts[1].strip()

            if line_pid == str(pid):
                print(f"Found window ID: {window_id} for PID {pid}", flush=True)
                return window_id

    return None

def verify_screenshot_with_ai(screenshot_path, expected_description):
    """Use AI to verify the screenshot matches the expected description."""
    import anthropic
    import base64

    print(f"Verifying screenshot with AI: {screenshot_path}", flush=True)

    # Read the screenshot file
    with open(screenshot_path, 'rb') as f:
        image_data = base64.standard_b64encode(f.read()).decode('utf-8')

    # Get API key from environment
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Warning: ANTHROPIC_API_KEY not set, skipping AI verification", flush=True)
        return True

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Look at this screenshot and answer with ONLY "YES" or "NO":

Does this screenshot plausibly show a window that matches this description: {expected_description}?

Consider:
- Does the window title bar match the description?
- Are there visual elements consistent with the description?
- Does it include window decorations (title bar, borders)?

Answer ONLY with "YES" or "NO"."""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
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
                        "text": prompt
                    }
                ],
            }
        ],
    )

    response = message.content[0].text.strip().upper()
    print(f"AI verification response: {response}", flush=True)

    return response == "YES"

def main():
    """Test capture by window ID flow."""

    cmd_process = None

    try:
        print("Starting capture-by-id test...", flush=True)

        # Get paths
        project_root = Path(__file__).parent.parent.parent
        screenshot_exe = project_root / "release" / "screenshot.exe"
        tmp_dir = project_root / "tmp"

        # Ensure tmp directory exists
        tmp_dir.mkdir(exist_ok=True)

        # Verify executable exists
        assert screenshot_exe.exists(), f"screenshot.exe not found at {screenshot_exe}"
        print(f"Using executable: {screenshot_exe}", flush=True)

        # Launch controlled cmd.exe window with unique title
        print("Launching controlled cmd.exe window...", flush=True)
        unique_title = f"TestWindow_CaptureByID_{int(time.time())}"
        cmd_process = subprocess.Popen(
            ['cmd.exe', '/K', f'title {unique_title}'],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        cmd_pid = cmd_process.pid
        print(f"Launched cmd.exe with PID {cmd_pid}, title: {unique_title}", flush=True)

        # Wait for window to appear
        time.sleep(2)
        print("Window should be visible now...", flush=True)

        # Get window ID by matching PID
        window_id = get_window_id_by_pid(str(screenshot_exe), cmd_pid)
        assert window_id is not None, f"Could not find window ID for PID {cmd_pid}"
        print(f"Found window ID: {window_id}", flush=True)

        # Verify window ID is alphanumeric
        assert re.match(r'^[A-Za-z0-9]+$', window_id), f"Window ID '{window_id}' is not alphanumeric"  # $REQ_ID_001
        print(f"✓ Window ID is alphanumeric: {window_id}", flush=True)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        output_file = tmp_dir / f"{timestamp}_capture-by-id.png"

        # Test 1: Capture by window ID to specific file
        print(f"Capturing window by ID {window_id} to {output_file}...", flush=True)
        result = subprocess.run(
            [str(screenshot_exe), '--id', window_id, str(output_file)],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        print(f"Capture stdout: {result.stdout}", flush=True)
        print(f"Capture stderr: {result.stderr}", flush=True)

        assert result.returncode == 0, f"Capture by ID failed with return code {result.returncode}"  # $REQ_ID_002
        print("✓ Tool accepted --id flag", flush=True)

        # Verify file was created at exact location specified
        assert output_file.exists(), f"Screenshot file not created at {output_file}"  # $REQ_ID_002 $REQ_ID_006
        assert output_file.stat().st_size > 0, "Screenshot file is empty"  # $REQ_ID_002
        print(f"✓ Screenshot file created at exact location: {output_file} ({output_file.stat().st_size} bytes)", flush=True)

        # Verify PNG format (check PNG signature: 89 50 4E 47 0D 0A 1A 0A)
        with open(output_file, 'rb') as f:
            signature = f.read(8)
            assert signature == b'\x89PNG\r\n\x1a\n', "File is not a valid PNG"  # $REQ_ID_004
        print("✓ File is valid PNG format", flush=True)

        # Verify success message
        assert f"Wrote {output_file}" in result.stdout, "Missing success message"  # $REQ_ID_009
        print("✓ Tool outputs 'Wrote [filepath]' message", flush=True)

        # Verify with AI that screenshot plausibly shows the cmd.exe window
        ai_verified = verify_screenshot_with_ai(output_file, f"cmd.exe window with title '{unique_title}'")
        assert ai_verified, "AI verification failed -- screenshot does not match expected window"  # $REQ_ID_002 $REQ_ID_003 $REQ_ID_005
        print("✓ AI verified screenshot plausibly shows the correct window with full decorations", flush=True)

        # Test 2: Capture to directory with auto-generated timestamp
        print("Testing capture to directory with auto-generated filename...", flush=True)
        result = subprocess.run(
            [str(screenshot_exe), '--id', window_id, str(tmp_dir) + '/'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        assert result.returncode == 0, "Capture to directory failed"  # $REQ_ID_007

        # Extract the generated filename from output
        match = re.search(r'Wrote (.+)', result.stdout)
        assert match, "Could not find output filename in message"  # $REQ_ID_007
        generated_file = Path(match.group(1))
        assert generated_file.exists(), f"Generated file not found: {generated_file}"  # $REQ_ID_007

        # Verify timestamped filename format
        filename = generated_file.name
        assert re.match(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d+_screenshot\.png', filename), \
            f"Filename does not match timestamped format: {filename}"  # $REQ_ID_007
        print(f"✓ Auto-generated timestamped filename: {filename}", flush=True)

        # Test 3: Capture to current directory (omit output path)
        print("Testing capture to current directory with omitted path...", flush=True)
        # Change to tmp directory so we don't clutter the project root
        original_dir = os.getcwd()
        os.chdir(tmp_dir)

        result = subprocess.run(
            [str(screenshot_exe), '--id', window_id],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        # Extract the generated filename from output before changing back
        match = re.search(r'Wrote (.+)', result.stdout)
        assert match, "Could not find output filename in message"  # $REQ_ID_008
        output_path_str = match.group(1).strip()

        # Resolve the path while still in the tmp directory
        generated_file = Path(output_path_str).resolve()

        os.chdir(original_dir)

        assert result.returncode == 0, "Capture to current directory failed"  # $REQ_ID_008
        assert generated_file.exists(), f"Generated file not found: {generated_file}"  # $REQ_ID_008

        # Verify it was created in the tmp directory (which was our current directory)
        assert generated_file.parent.resolve() == tmp_dir.resolve(), \
            f"File not created in current directory: {generated_file}"  # $REQ_ID_008
        print(f"✓ File created in current directory with auto-generated name: {generated_file.name}", flush=True)

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
        # Clean up cmd.exe process
        if cmd_process is not None and cmd_process.poll() is None:
            print("Cleaning up cmd.exe process...", flush=True)
            cmd_process.kill()
            cmd_process.wait(timeout=5)

if __name__ == '__main__':
    sys.exit(main())
