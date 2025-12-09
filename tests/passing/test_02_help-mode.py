#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test: Help Mode Verification
Verifies the help output meets specifications when run without arguments.
"""

import os
import sys
import subprocess
import re


def get_exe_path():
    """Get path to screenshot.exe in released directory."""
    test_dir = os.path.dirname(__file__)
    released_dir = os.path.join(test_dir, "..", "..", "released")
    exe_path = os.path.abspath(os.path.join(released_dir, "screenshot.exe"))
    return exe_path


def run_help_mode():
    """Run screenshot.exe without arguments and capture output."""
    exe_path = get_exe_path()
    assert os.path.exists(exe_path), f"Executable not found: {exe_path}"

    result = subprocess.run(
        [exe_path],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )
    return result


def test_req_help_001_display_usage():
    """$REQ_HELP_001: Display usage when run without arguments."""
    result = run_help_mode()

    # Should display something (usage info)
    has_output = bool(result.stdout or result.stderr)
    assert has_output, "Help mode should produce output"

    # Usage should be in stdout
    output = result.stdout
    assert "usage" in output.lower() or "screenshot" in output.lower(), \
        f"Help mode should display usage information, got: {output[:200]}"

    print("✓ $REQ_HELP_001: Display usage when run without arguments")


def test_req_help_002_usage_examples():
    """Show usage examples for three capture modes."""
    result = run_help_mode()
    output = result.stdout

    # Check for --title example
    assert '--title "window title"' in output or '--title' in output, \
        "Help should show --title option"

    # Check for --pid example
    assert '--pid' in output, "Help should show --pid option"

    # Check for --id example
    assert '--id' in output, "Help should show --id option"

    # Check output path format hint (optional argument indicator)
    assert '[' in output or 'output' in output.lower(), \
        "Help should indicate output path is optional"

    print("✓ Usage examples show three capture modes")


def test_req_help_003_output_path_instructions():
    """Explain output path options."""
    result = run_help_mode()
    output = result.stdout

    # Should mention .png file option
    assert '.png' in output.lower(), "Help should mention .png file option"

    # Should mention directory option
    assert 'directory' in output.lower() or 'dir' in output.lower(), \
        "Help should mention directory option"

    # Should mention timestamp (auto-generated filename)
    assert 'timestamp' in output.lower() or 'current' in output.lower() or 'omit' in output.lower(), \
        "Help should explain what happens when output is omitted"

    print("✓ Output path instructions are provided")


def test_req_help_004_window_list_header():
    """Window list header must be 'Currently open windows (id,pid,title):'"""
    result = run_help_mode()
    output = result.stdout

    expected_header = "Currently open windows (id,pid,title):"
    assert expected_header in output, \
        f"Expected header '{expected_header}' not found in output:\n{output}"

    print("✓ Window list header is correct")


def test_req_help_005_window_list_format():
    """Each window listed as <window-id>\\t<pid>\\t\"window title\""""
    result = run_help_mode()
    output = result.stdout

    # Find lines after the header
    lines = output.split('\n')
    header_idx = None
    for i, line in enumerate(lines):
        if "Currently open windows" in line:
            header_idx = i
            break

    assert header_idx is not None, "Window list header not found"

    # Check at least one window line follows the format
    # Format: <window-id>\t<pid>\t"window title"
    window_line_pattern = re.compile(r'^[A-Fa-f0-9]+\t\d+\t".+"$')

    found_valid_window = False
    for line in lines[header_idx + 1:]:
        line = line.strip()
        if not line:
            continue
        if window_line_pattern.match(line):
            found_valid_window = True
            break

    assert found_valid_window, \
        f"No window line matches format '<window-id>\\t<pid>\\t\"window title\"' in:\n{output}"

    print("✓ Window list format is correct (tab-separated with quoted title)")


def test_req_help_006_window_id_format():
    """Window IDs are alphanumeric hexadecimal (0-9, A-F)."""
    result = run_help_mode()
    output = result.stdout

    # Find window list lines
    lines = output.split('\n')
    header_idx = None
    for i, line in enumerate(lines):
        if "Currently open windows" in line:
            header_idx = i
            break

    assert header_idx is not None, "Window list header not found"

    # Check window ID format (first field before tab)
    hex_pattern = re.compile(r'^[A-Fa-f0-9]+$')

    found_window = False
    for line in lines[header_idx + 1:]:
        line = line.strip()
        if not line:
            continue
        if '\t' not in line:
            continue

        window_id = line.split('\t')[0]
        found_window = True

        # Window ID must be hex (0-9, A-F) without 0x prefix
        assert hex_pattern.match(window_id), \
            f"Window ID '{window_id}' is not valid hexadecimal (expected 0-9, A-F)"
        assert not window_id.startswith('0x'), \
            f"Window ID '{window_id}' should not have 0x prefix"
        break

    assert found_window, "No window lines found to check ID format"

    print("✓ Window ID format is correct (hexadecimal without 0x)")


def test_req_help_007_exit_code_zero():
    """Help mode exits with code 0."""
    result = run_help_mode()

    assert result.returncode == 0, \
        f"Help mode should exit with code 0, got {result.returncode}"

    print("✓ Exit code is 0")


def main():
    """Run all tests."""
    try:
        test_req_help_001_display_usage()
        test_req_help_002_usage_examples()
        test_req_help_003_output_path_instructions()
        test_req_help_004_window_list_header()
        test_req_help_005_window_list_format()
        test_req_help_006_window_id_format()
        test_req_help_007_exit_code_zero()
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
