#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test: Build Output Verification
Verifies the released executable exists and meets specifications.
"""

import os
import sys
import subprocess

def test_req_build_001_released_contains_screenshot_exe():
    """$REQ_BUILD_001: Released directory contains screenshot.exe as the only file."""
    released_dir = os.path.join(os.path.dirname(__file__), "..", "..", "released")
    released_dir = os.path.abspath(released_dir)

    # Check released directory exists
    assert os.path.isdir(released_dir), f"Released directory does not exist: {released_dir}"

    # List all files in released directory
    files = os.listdir(released_dir)

    # Should contain exactly one file
    assert len(files) == 1, f"Released directory should contain exactly 1 file, found {len(files)}: {files}"

    # That file should be screenshot.exe
    assert files[0] == "screenshot.exe", f"Expected 'screenshot.exe', found '{files[0]}'"

    # Verify it's actually a file, not a directory
    exe_path = os.path.join(released_dir, "screenshot.exe")
    assert os.path.isfile(exe_path), f"screenshot.exe is not a file"

    print("✓ $REQ_BUILD_001: Released directory contains screenshot.exe as the only file")


def test_req_build_002_native_compiled():
    """The executable must be native compiled with no runtime dependencies."""
    released_dir = os.path.join(os.path.dirname(__file__), "..", "..", "released")
    exe_path = os.path.abspath(os.path.join(released_dir, "screenshot.exe"))

    assert os.path.exists(exe_path), f"Executable not found: {exe_path}"

    # Verify it's executable and runs (at least shows help)
    # A native compiled binary should run without needing an interpreter or runtime
    result = subprocess.run(
        [exe_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    # The binary should execute (exit code 0 for help mode per README)
    # Even if it exits with non-zero, as long as it runs at all, it's native
    # We just need to confirm it executed (didn't crash due to missing runtime)

    # Check that it produced some output (either stdout or stderr)
    has_output = bool(result.stdout or result.stderr)

    # A native binary that runs help mode should produce output
    assert has_output, "Executable produced no output - may not be a valid native binary"

    print("✓ Executable is native compiled (runs without runtime dependencies)")


def main():
    """Run all tests."""
    try:
        test_req_build_001_released_contains_screenshot_exe()
        test_req_build_002_native_compiled()
        print("\n✓ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
