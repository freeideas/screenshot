#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test: Output Path Handling
Verifies output path handling according to requirements.

Requirements:
- $REQ_OUTPUT_001: Save to Explicit PNG Path
- $REQ_OUTPUT_002: Save to Directory with Timestamped Filename
- $REQ_OUTPUT_003: Default to Current Directory with Timestamped Filename
- $REQ_OUTPUT_004: Output Format is PNG
"""

import os
import sys
import subprocess
import time
import re
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


def test_req_output_001_explicit_png_path():
    """$REQ_OUTPUT_001: Save to Explicit PNG Path

    When a .png file path is specified, save the screenshot to that exact location.
    """
    print("Testing $REQ_OUTPUT_001: Save to Explicit PNG Path...")

    exe_path = get_exe_path()
    assert os.path.exists(exe_path), f"Executable not found: {exe_path}"

    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    test_window = windows[0]
    window_title = test_window['title']

    # Set up a specific PNG output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"explicit_{timestamp}.png")

    # Run screenshot.exe with explicit PNG path
    result = subprocess.run(
        [exe_path, "--title", window_title, output_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    assert result.returncode == 0, \
        f"screenshot.exe failed (exit code {result.returncode})\nstderr: {result.stderr}"

    # Verify file was created at the exact specified location
    assert os.path.exists(output_path), \
        f"Output file not created at specified path: {output_path}"

    # Verify the "Wrote" message contains our exact path
    assert output_path in result.stdout or os.path.basename(output_path) in result.stdout, \
        f"Expected exact path in output message, got: {result.stdout}"

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)

    print("  ✓ $REQ_OUTPUT_001: Save to Explicit PNG Path works correctly")
    return True


def test_req_output_002_directory_with_timestamp():
    """$REQ_OUTPUT_002: Save to Directory with Timestamped Filename

    When a directory is specified, generate a timestamped filename in the format
    YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png and save in that directory.
    """
    print("Testing $REQ_OUTPUT_002: Save to Directory with Timestamped Filename...")

    exe_path = get_exe_path()
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    test_window = windows[0]
    window_title = test_window['title']

    # Set up a directory output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp", "dir_output_test")
    os.makedirs(tmp_dir, exist_ok=True)

    # Clear any existing screenshots in the directory
    for f in os.listdir(tmp_dir):
        if f.endswith('.png'):
            os.remove(os.path.join(tmp_dir, f))

    # Run screenshot.exe with directory as output
    result = subprocess.run(
        [exe_path, "--title", window_title, tmp_dir],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    assert result.returncode == 0, \
        f"screenshot.exe failed (exit code {result.returncode})\nstderr: {result.stderr}"

    # Find the created file
    png_files = [f for f in os.listdir(tmp_dir) if f.endswith('.png')]
    assert len(png_files) == 1, \
        f"Expected 1 PNG file in directory, found {len(png_files)}: {png_files}"

    filename = png_files[0]

    # Verify the filename matches the timestamp pattern: YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png
    # Pattern: 2025-11-10-23-30-22-293532_screenshot.png
    timestamp_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d+_screenshot\.png$')
    assert timestamp_pattern.match(filename), \
        f"Filename does not match timestamp pattern 'YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png': {filename}"

    print(f"  Created file: {filename}")

    # Clean up
    for f in os.listdir(tmp_dir):
        if f.endswith('.png'):
            os.remove(os.path.join(tmp_dir, f))

    print("  ✓ $REQ_OUTPUT_002: Save to Directory with Timestamped Filename works correctly")
    return True


def test_req_output_003_default_current_directory():
    """$REQ_OUTPUT_003: Default to Current Directory with Timestamped Filename

    When output path is omitted, save the screenshot to the current directory
    with an auto-generated timestamped filename.
    """
    print("Testing $REQ_OUTPUT_003: Default to Current Directory with Timestamped Filename...")

    exe_path = get_exe_path()
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    test_window = windows[0]
    window_title = test_window['title']

    # Set up a working directory for this test
    project_root = get_project_root()
    work_dir = os.path.join(project_root, "tmp", "cwd_test")
    os.makedirs(work_dir, exist_ok=True)

    # Clear any existing screenshots in the directory
    for f in os.listdir(work_dir):
        if f.endswith('.png'):
            os.remove(os.path.join(work_dir, f))

    # Run screenshot.exe WITHOUT output path, from the work directory
    result = subprocess.run(
        [exe_path, "--title", window_title],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30,
        cwd=work_dir
    )

    assert result.returncode == 0, \
        f"screenshot.exe failed (exit code {result.returncode})\nstderr: {result.stderr}"

    # Find the created file in the current working directory
    png_files = [f for f in os.listdir(work_dir) if f.endswith('.png')]
    assert len(png_files) == 1, \
        f"Expected 1 PNG file in current directory, found {len(png_files)}: {png_files}"

    filename = png_files[0]

    # Verify the filename matches the timestamp pattern
    timestamp_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d+_screenshot\.png$')
    assert timestamp_pattern.match(filename), \
        f"Filename does not match timestamp pattern 'YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png': {filename}"

    print(f"  Created file in current directory: {filename}")

    # Clean up
    for f in os.listdir(work_dir):
        if f.endswith('.png'):
            os.remove(os.path.join(work_dir, f))

    print("  ✓ $REQ_OUTPUT_003: Default to Current Directory with Timestamped Filename works correctly")
    return True


def test_req_output_004_png_format():
    """$REQ_OUTPUT_004: Output Format is PNG

    The screenshot is saved in PNG format.
    """
    print("Testing $REQ_OUTPUT_004: Output Format is PNG...")

    exe_path = get_exe_path()
    windows = get_window_list()
    assert len(windows) > 0, "No windows available to capture"

    test_window = windows[0]
    window_title = test_window['title']

    # Set up output path
    project_root = get_project_root()
    tmp_dir = os.path.join(project_root, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    output_path = os.path.join(tmp_dir, f"format_test_{timestamp}.png")

    # Run screenshot.exe
    result = subprocess.run(
        [exe_path, "--title", window_title, output_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    assert result.returncode == 0, \
        f"screenshot.exe failed (exit code {result.returncode})\nstderr: {result.stderr}"

    assert os.path.exists(output_path), \
        f"Output file not created: {output_path}"

    # Verify it's a valid PNG by checking magic bytes
    with open(output_path, 'rb') as f:
        header = f.read(8)

    png_signature = b'\x89PNG\r\n\x1a\n'
    assert header == png_signature, \
        f"Output file is not a valid PNG (header: {header.hex()})"

    # Verify file has reasonable size (not empty or corrupted)
    file_size = os.path.getsize(output_path)
    assert file_size > 1024, \
        f"Output file too small ({file_size} bytes), likely not a valid screenshot"

    print(f"  Valid PNG file created: {file_size} bytes")

    # Clean up
    if os.path.exists(output_path):
        os.remove(output_path)

    print("  ✓ $REQ_OUTPUT_004: Output Format is PNG works correctly")
    return True


def main():
    """Run all tests."""
    try:
        exe_path = get_exe_path()
        if not os.path.exists(exe_path):
            print(f"FAIL: Executable not found: {exe_path}")
            sys.exit(1)

        test_req_output_001_explicit_png_path()
        test_req_output_002_directory_with_timestamp()
        test_req_output_003_default_current_directory()
        test_req_output_004_png_format()

        print("\n" + "="*60)
        print("All tests passed!")
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
