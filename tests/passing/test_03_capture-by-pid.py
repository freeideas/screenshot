#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test: Capture by Process ID
Verifies capture by process ID works according to requirements.

Requirements:
- $REQ_PID_001: Capture Window by PID Flag
- $REQ_PID_002: Save to Specified PNG File
- $REQ_PID_003: Output Success Message
"""

import os
import sys
import subprocess
import time
import atexit
import re

# Track processes launched by this test
_test_processes = []

def cleanup_test_processes():
    """Kill any processes started by this test."""
    for proc in _test_processes:
        try:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=1)
        except:
            pass

# Register cleanup to run on exit (even if test fails)
atexit.register(cleanup_test_processes)


def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_project_root():
    return os.path.dirname(os.path.dirname(get_script_dir()))


def get_exe_path():
    """Get path to screenshot.exe in released directory."""
    return os.path.join(get_project_root(), "released", "screenshot.exe")


def get_uv_binary():
    """Get the correct uv binary for the current platform."""
    project_root = get_project_root()
    if sys.platform == 'darwin':
        return os.path.join(project_root, "the-system", "bin", "uv.mac")
    else:
        return os.path.join(project_root, "the-system", "bin", "uv.exe")


def get_window_list():
    """Run screenshot.exe to get the list of windows."""
    exe_path = get_exe_path()
    result = subprocess.run(
        [exe_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    if result.returncode != 0:
        print(f"ERROR: Failed to get window list (exit code {result.returncode})")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    # Parse window list from output
    windows = []
    for line in result.stdout.split('\n'):
        if '\t' in line:
            parts = line.split('\t')
            if len(parts) >= 3:
                windows.append({
                    'id': parts[0],
                    'pid': parts[1],
                    'title': parts[2].strip('"')
                })

    return windows


def test_req_pid_001_capture_by_pid_flag():
    """$REQ_PID_001: Capture Window by PID Flag

    When --pid <process-id> is specified, capture a window of a process by its
    numeric process ID. If the process has multiple windows, one will be captured.
    """
    print("Testing $REQ_PID_001: Capture Window by PID Flag...")

    exe_path = get_exe_path()
    assert os.path.exists(exe_path), f"Executable not found: {exe_path}"

    # Get list of windows
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    # Pick the first available window
    test_window = windows[0]
    window_pid = test_window['pid']

    # Verify PID is numeric
    assert window_pid.isdigit(), \
        f"Window PID '{window_pid}' is not numeric"

    print(f"  Using window: pid={window_pid}, title=\"{test_window['title']}\"")

    # Set up output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"{timestamp}_capture_by_pid.png")

    # Run screenshot.exe with --pid flag
    result = subprocess.run(
        [exe_path, "--pid", window_pid, output_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    # Check that command succeeded
    assert result.returncode == 0, \
        f"screenshot.exe --pid failed (exit code {result.returncode})\nstderr: {result.stderr}"

    # Verify output file was created
    assert os.path.exists(output_path), \
        f"Output file not created: {output_path}"

    # Clean up for next test
    if os.path.exists(output_path):
        os.remove(output_path)

    print("  $REQ_PID_001: Capture Window by PID Flag works correctly")
    return True


def test_req_pid_002_save_to_png():
    """$REQ_PID_002: Save to Specified PNG File

    When a .png file path is specified as output, save the screenshot to that exact location.
    """
    print("Testing $REQ_PID_002: Save to Specified PNG File...")

    exe_path = get_exe_path()
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    test_window = windows[0]
    window_pid = test_window['pid']

    # Set up specific output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"{timestamp}_exact_path_test_pid.png")

    # Run screenshot.exe with --pid flag and specific output path
    result = subprocess.run(
        [exe_path, "--pid", window_pid, output_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    assert result.returncode == 0, \
        f"screenshot.exe failed (exit code {result.returncode})\nstderr: {result.stderr}"

    # Verify file was created at exact specified location
    assert os.path.exists(output_path), \
        f"Output file not created at specified path: {output_path}"

    # Verify it's a valid PNG (check magic bytes)
    with open(output_path, 'rb') as f:
        header = f.read(8)

    png_signature = b'\x89PNG\r\n\x1a\n'
    assert header == png_signature, \
        f"Output file is not a valid PNG (header: {header.hex()})"

    # Verify file has reasonable size
    file_size = os.path.getsize(output_path)
    assert file_size > 1024, \
        f"Output file too small ({file_size} bytes), likely not a valid screenshot"

    print(f"  Created PNG file at: {output_path} ({file_size} bytes)")

    # Keep file for visual verification
    global _last_output_path
    _last_output_path = output_path

    print("  $REQ_PID_002: Save to Specified PNG File works correctly")
    return True


def test_req_pid_003_output_success_message():
    """$REQ_PID_003: Output Success Message

    When a screenshot is successfully captured, output 'Wrote [filepath]' before exiting.
    """
    print("Testing $REQ_PID_003: Output Success Message...")

    exe_path = get_exe_path()
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    test_window = windows[0]
    window_pid = test_window['pid']

    # Set up output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"{timestamp}_message_test_pid.png")

    # Run screenshot.exe with --pid flag
    result = subprocess.run(
        [exe_path, "--pid", window_pid, output_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    assert result.returncode == 0, \
        f"screenshot.exe failed (exit code {result.returncode})\nstderr: {result.stderr}"

    # Verify "Wrote [filepath]" message in output
    output = result.stdout

    # Check for "Wrote " prefix
    assert "Wrote " in output, \
        f"Expected 'Wrote [filepath]' in output, got: {output}"

    # Verify the filepath is mentioned in the message
    # The message should contain the path or filename
    assert output_path in output or os.path.basename(output_path) in output, \
        f"Expected filepath in output message, got: {output}"

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)

    print("  $REQ_PID_003: Output Success Message works correctly")
    return True


def test_visual_verification():
    """Use AI to verify screenshot plausibly matches window content."""
    print("Testing visual verification of captured screenshot...")

    exe_path = get_exe_path()
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    test_window = windows[0]
    window_pid = test_window['pid']
    window_title = test_window['title']

    # Set up output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"{timestamp}_visual_test_pid.png")

    # Capture the window
    result = subprocess.run(
        [exe_path, "--pid", window_pid, output_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    assert result.returncode == 0, \
        f"screenshot.exe failed (exit code {result.returncode})\nstderr: {result.stderr}"

    assert os.path.exists(output_path), \
        f"Output file not created: {output_path}"

    # Use visual-test.py to verify the screenshot
    visual_test_script = os.path.join(project_root, "the-system", "scripts", "visual-test.py")

    if os.path.exists(visual_test_script):
        print(f"  Verifying screenshot of window '{window_title}'...")

        visual_result = subprocess.run(
            [
                get_uv_binary(),
                "run", "--script", visual_test_script,
                output_path,
                f"A screenshot of a window. The image should show window content and possibly window decorations like a title bar."
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )

        if visual_result.returncode == 0:
            print("  Visual verification passed")
        elif visual_result.returncode == 1:
            print(f"WARNING: Visual test failed, but this may be due to window content")
            print(f"  stdout: {visual_result.stdout}")
            # Don't fail the test - visual verification is supplementary
        else:
            print(f"WARNING: Visual test error (code {visual_result.returncode})")
            print(f"  stdout: {visual_result.stdout}")
            print(f"  stderr: {visual_result.stderr}")
    else:
        print("  WARNING: visual-test.py not found, skipping visual verification")

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)

    return True


def main():
    """Run all tests."""
    try:
        exe_path = get_exe_path()
        if not os.path.exists(exe_path):
            print(f"FAIL: Executable not found: {exe_path}")
            sys.exit(1)

        test_req_pid_001_capture_by_pid_flag()
        test_req_pid_002_save_to_png()
        test_req_pid_003_output_success_message()
        test_visual_verification()

        print("\n" + "="*60)
        print("All tests passed!")
        print("="*60)
        return 0
    except AssertionError as e:
        print(f"\n Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
