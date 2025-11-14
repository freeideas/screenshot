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
    """Test help mode flow -- display usage and window list when run without arguments."""

    try:
        print("Starting help mode test...", flush=True)

        # Run screenshot.exe without arguments
        print("Running screenshot.exe without arguments...", flush=True)
        result = subprocess.run(
            ['./release/screenshot.exe'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=10
        )

        print(f"Exit code: {result.returncode}", flush=True)
        print(f"Output length: {len(result.stdout)} characters", flush=True)

        output = result.stdout

        # $REQ_HELP_001: When executable is run without any arguments, display help text and window list
        assert len(output) > 0, "No output produced"  # $REQ_HELP_001
        print("✓ Help text displayed", flush=True)

        # $REQ_HELP_002: Output must include usage examples showing the three capture modes
        assert '--title "window title"' in output, "Missing --title usage example"  # $REQ_HELP_002
        assert '--pid <process-id>' in output, "Missing --pid usage example"  # $REQ_HELP_002
        assert '--id <window-id>' in output, "Missing --id usage example"  # $REQ_HELP_002
        print("✓ Usage examples with title, pid, and id flags present", flush=True)

        # $REQ_HELP_003: Output must explain output path is optional with three path behaviors
        assert 'Output path is optional' in output or 'optional' in output.lower(), "Missing output path explanation"  # $REQ_HELP_003
        assert '.png file' in output or 'Specify .png file' in output, "Missing .png file path explanation"  # $REQ_HELP_003
        assert 'directory' in output, "Missing directory path explanation"  # $REQ_HELP_003
        assert 'timestamped filename' in output or 'YYYY-MM-DD' in output, "Missing timestamped filename explanation"  # $REQ_HELP_003
        print("✓ Output path instructions present", flush=True)

        # $REQ_HELP_004: Output must include header line that labels window list columns
        assert 'Currently open windows (id,pid,title):' in output, "Missing window list header"  # $REQ_HELP_004
        print("✓ Window list header present", flush=True)

        # $REQ_HELP_005: Output must list all currently open windows with one line per window
        # Find window list lines (after the header)
        lines = output.split('\n')
        header_idx = -1
        for i, line in enumerate(lines):
            if 'Currently open windows (id,pid,title):' in line:
                header_idx = i
                break

        assert header_idx >= 0, "Could not find window list header"  # $REQ_HELP_005

        # Lines after header should be window entries
        window_lines = [line for line in lines[header_idx+1:] if line.strip()]
        assert len(window_lines) > 0, "No windows listed"  # $REQ_HELP_005
        print(f"✓ Found {len(window_lines)} window entries", flush=True)

        # Verify at least one window line has correct format
        # Format: <window-id>\t<pid>\t"window title"
        found_valid_window = False
        for line in window_lines:
            # $REQ_HELP_008: Fields must be separated by tab characters
            parts = line.split('\t')
            if len(parts) >= 3:  # $REQ_HELP_008
                found_valid_window = True

                window_id = parts[0].strip()
                pid_str = parts[1].strip()
                title_part = '\t'.join(parts[2:])  # Title may contain tabs

                # $REQ_HELP_006: Window IDs must be alphanumeric hexadecimal values without 0x prefix
                assert re.match(r'^[0-9A-Fa-f]+$', window_id), f"Window ID '{window_id}' is not alphanumeric hex"  # $REQ_HELP_006
                assert not window_id.startswith('0x'), f"Window ID should not have 0x prefix: {window_id}"  # $REQ_HELP_006
                print(f"✓ Window ID format valid: {window_id}", flush=True)

                # $REQ_HELP_007: Process IDs must be numeric values
                assert re.match(r'^\d+$', pid_str), f"PID '{pid_str}' is not numeric"  # $REQ_HELP_007
                print(f"✓ PID format valid: {pid_str}", flush=True)

                # Title should be in quotes (based on format specification)
                assert '"' in title_part, f"Window title not in quotes: {title_part}"  # $REQ_HELP_005
                print(f"✓ Window title in quotes: {title_part[:50]}...", flush=True)

                break  # Only need to verify one window line

        assert found_valid_window, "No valid window entries found with tab-separated fields"  # $REQ_HELP_008

        # $REQ_HELP_009: Help mode must exit with status code 0
        assert result.returncode == 0, f"Exit code was {result.returncode}, expected 0"  # $REQ_HELP_009
        print("✓ Exit code is 0 (success)", flush=True)

        print("✓ All tests passed", flush=True)
        return 0

    except AssertionError as e:
        print(f"✗ Test failed: {e}", flush=True)
        return 1
    except subprocess.TimeoutExpired:
        print("✗ Test timed out waiting for screenshot.exe", flush=True)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", flush=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
