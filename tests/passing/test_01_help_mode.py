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
import re

def main():
    """Test help mode flow -- verify all help text and window list requirements."""

    try:
        print("Starting help mode test...", flush=True)

        # Run screenshot.exe without arguments
        print("Running screenshot.exe without arguments...", flush=True)
        result = subprocess.run(
            ['./release/screenshot.exe'],
            capture_output=True,
            timeout=10
        )
        print(f"Screenshot.exe exited with code {result.returncode}", flush=True)

        # Decode output - try UTF-8, fall back to cp1252 (Windows default)
        try:
            output = result.stdout.decode('utf-8')
        except UnicodeDecodeError:
            output = result.stdout.decode('cp1252', errors='replace')

        print(f"Output length: {len(output)} characters", flush=True)
        print("=" * 60, flush=True)
        print(output, flush=True)
        print("=" * 60, flush=True)

        # $REQ_HELP_008: Exit Success
        assert result.returncode == 0, f"Help mode should exit with code 0, got {result.returncode}"  # $REQ_HELP_008
        print("✓ Exit code is 0", flush=True)

        # $REQ_HELP_001: Display Usage Examples
        # Must show three capture modes: by title, by PID, and by window ID
        print("Checking for usage examples...", flush=True)
        assert '--title' in output, "Missing --title usage example"  # $REQ_HELP_001
        assert '--pid' in output, "Missing --pid usage example"  # $REQ_HELP_001
        assert '--id' in output, "Missing --id usage example"  # $REQ_HELP_001
        print("✓ All three capture modes shown (--title, --pid, --id)", flush=True)

        # $REQ_HELP_002: Display Output Path Instructions
        # Must explain: explicit .png file paths, directory paths with auto-generated timestamped filenames,
        # and omitted paths defaulting to current directory
        print("Checking for output path instructions...", flush=True)
        output_lower = output.lower()
        assert 'output' in output_lower, "Missing output path instructions"  # $REQ_HELP_002
        assert 'directory' in output_lower or 'timestamped' in output_lower, "Missing directory/timestamped filename explanation"  # $REQ_HELP_002
        print("✓ Output path instructions present", flush=True)

        # $REQ_HELP_003: Display Window List Header
        # Must show: "Currently open windows (id,pid,title):"
        print("Checking for window list header...", flush=True)
        assert 'Currently open windows' in output, "Missing window list header"  # $REQ_HELP_003
        assert 'id' in output and 'pid' in output and 'title' in output, "Window list header missing field labels"  # $REQ_HELP_003
        print("✓ Window list header present", flush=True)

        # $REQ_HELP_004: List Open Windows
        # Format: <window-id>\t<pid>\t"window title" with tab separators
        print("Checking for window list entries...", flush=True)
        lines = output.split('\n')
        window_lines = []
        for line in lines:
            # Look for lines matching the window list format: alphanumeric\t<digits>\t"..."
            if '\t' in line and '"' in line:
                parts = line.split('\t')
                if len(parts) >= 3:
                    window_lines.append(line)

        assert len(window_lines) > 0, "No window list entries found"  # $REQ_HELP_004
        print(f"✓ Found {len(window_lines)} window list entries", flush=True)

        # Verify at least one window entry has proper format
        sample_window = window_lines[0]
        print(f"Sample window entry: {sample_window}", flush=True)
        parts = sample_window.split('\t')

        # $REQ_HELP_005: Window ID Format
        # Window IDs are alphanumeric hexadecimal values without 0x prefix
        window_id = parts[0].strip()
        assert re.match(r'^[0-9A-Fa-f]+$', window_id), f"Window ID '{window_id}' is not alphanumeric hexadecimal"  # $REQ_HELP_005
        print(f"✓ Window ID format valid: {window_id}", flush=True)

        # $REQ_HELP_006: Process ID Format
        # Process IDs are numeric values
        pid = parts[1].strip()
        assert re.match(r'^\d+$', pid), f"PID '{pid}' is not numeric"  # $REQ_HELP_006
        print(f"✓ Process ID format valid: {pid}", flush=True)

        # $REQ_HELP_007: Window Title Quoting
        # Window titles are displayed with double quotes
        title_part = '\t'.join(parts[2:])  # Join remaining parts in case title contains tabs
        assert '"' in title_part, "Window title not enclosed in double quotes"  # $REQ_HELP_007
        print(f"✓ Window title has double quotes: {title_part[:50]}...", flush=True)

        print("✓ All tests passed", flush=True)
        return 0

    except AssertionError as e:
        print(f"✗ Test failed: {e}", flush=True)
        return 1
    except subprocess.TimeoutExpired:
        print("✗ Test failed: screenshot.exe timed out", flush=True)
        return 1
    except Exception as e:
        print(f"✗ Test failed with exception: {e}", flush=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
