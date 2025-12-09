#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test: Shorthand Mode Flow
Verifies capture using shorthand syntax where the selection type is auto-detected.

Requirements:
- $REQ_SHORT_001: Auto-Detect Title When Quoted
- $REQ_SHORT_002: Auto-Detect ID or PID When Unquoted
- $REQ_SHORT_003: Output Success Message
"""

import os
import sys
import subprocess
import time
import atexit

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


def test_req_short_001_auto_detect_quoted_title():
    """$REQ_SHORT_001: Auto-Detect Title When Quoted

    When the first argument doesn't start with `--` and starts with a quote (`"`),
    match it as a window title.
    """
    print("Testing $REQ_SHORT_001: Auto-Detect Title When Quoted...")

    exe_path = get_exe_path()
    assert os.path.exists(exe_path), f"Executable not found: {exe_path}"

    # Get list of windows
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    # Pick the first available window and use its title
    test_window = windows[0]
    window_title = test_window['title']

    print(f"  Using window title: \"{window_title}\"")

    # Set up output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"{timestamp}_shorthand_title.png")

    # Run screenshot.exe with shorthand syntax (quoted title)
    # The title is passed as a single argument with quotes
    quoted_title = f'"{window_title}"'
    result = subprocess.run(
        [exe_path, quoted_title, output_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    # Check that command succeeded
    assert result.returncode == 0, \
        f"screenshot.exe shorthand title failed (exit code {result.returncode})\nstderr: {result.stderr}\nstdout: {result.stdout}"

    # Verify output file was created
    assert os.path.exists(output_path), \
        f"Output file not created: {output_path}"

    # Verify it's a valid PNG (check magic bytes)
    with open(output_path, 'rb') as f:
        header = f.read(8)

    png_signature = b'\x89PNG\r\n\x1a\n'
    assert header == png_signature, \
        f"Output file is not a valid PNG (header: {header.hex()})"

    print(f"  Created PNG file at: {output_path}")

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)

    print("✓ $REQ_SHORT_001: Auto-Detect Title When Quoted works correctly")
    return True


def test_req_short_002_auto_detect_id_or_pid():
    """$REQ_SHORT_002: Auto-Detect ID or PID When Unquoted

    When the first argument doesn't start with `--` and doesn't start with a quote,
    match it as a window ID or process ID (whichever matches first).
    """
    print("Testing $REQ_SHORT_002: Auto-Detect ID or PID When Unquoted...")

    exe_path = get_exe_path()
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    # Test with window ID (unquoted)
    test_window = windows[0]
    window_id = test_window['id']

    print(f"  Testing with window ID: {window_id}")

    # Set up output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"{timestamp}_shorthand_id.png")

    # Run screenshot.exe with shorthand syntax (unquoted window ID)
    result = subprocess.run(
        [exe_path, window_id, output_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    # Check that command succeeded
    assert result.returncode == 0, \
        f"screenshot.exe shorthand ID failed (exit code {result.returncode})\nstderr: {result.stderr}\nstdout: {result.stdout}"

    # Verify output file was created
    assert os.path.exists(output_path), \
        f"Output file not created: {output_path}"

    # Verify it's a valid PNG
    with open(output_path, 'rb') as f:
        header = f.read(8)

    png_signature = b'\x89PNG\r\n\x1a\n'
    assert header == png_signature, \
        f"Output file is not a valid PNG (header: {header.hex()})"

    print(f"  Created PNG file at: {output_path}")

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)

    # Now test with PID (if it's a valid numeric PID)
    window_pid = test_window['pid']
    print(f"  Testing with window PID: {window_pid}")

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"{timestamp}_shorthand_pid.png")

    # Run screenshot.exe with shorthand syntax (unquoted PID)
    result = subprocess.run(
        [exe_path, window_pid, output_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    # Check that command succeeded
    assert result.returncode == 0, \
        f"screenshot.exe shorthand PID failed (exit code {result.returncode})\nstderr: {result.stderr}\nstdout: {result.stdout}"

    # Verify output file was created
    assert os.path.exists(output_path), \
        f"Output file not created: {output_path}"

    print(f"  Created PNG file at: {output_path}")

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)

    print("✓ $REQ_SHORT_002: Auto-Detect ID or PID When Unquoted works correctly")
    return True


def test_req_short_003_output_success_message():
    """$REQ_SHORT_003: Output Success Message

    When a screenshot is successfully captured, output 'Wrote [filepath]' before exiting.
    """
    print("Testing $REQ_SHORT_003: Output Success Message...")

    exe_path = get_exe_path()
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    test_window = windows[0]
    window_id = test_window['id']

    # Set up output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"{timestamp}_shorthand_message.png")

    # Run screenshot.exe with shorthand syntax
    result = subprocess.run(
        [exe_path, window_id, output_path],
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

    print("✓ $REQ_SHORT_003: Output Success Message works correctly")
    return True


def main():
    """Run all tests."""
    try:
        exe_path = get_exe_path()
        if not os.path.exists(exe_path):
            print(f"FAIL: Executable not found: {exe_path}")
            sys.exit(1)

        test_req_short_001_auto_detect_quoted_title()
        test_req_short_002_auto_detect_id_or_pid()
        test_req_short_003_output_success_message()

        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
