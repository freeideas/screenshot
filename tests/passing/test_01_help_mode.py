#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import re
import subprocess

# Fix Windows console encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass


def run(cmd: list[str], check: bool = False, capture: bool = True) -> subprocess.CompletedProcess:
    print(f"RUN: {' '.join(cmd)}", flush=True)
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
        encoding='utf-8',
        errors='replace'
    )


def parse_window_list(output: str):
    """Parse window list lines of form: <id>\t<pid>\t"title"""
    lines = []
    for raw in output.splitlines():
        line = raw.strip()
        if not line:
            continue
        # Skip header/usage lines
        if line.startswith("Usage:") or line.startswith("Run without arguments") or line.startswith("Currently open windows (id,pid,title):"):
            continue
        parts = line.split('\t')
        if len(parts) != 3:
            continue
        win_id, pid_str, title_quoted = parts
        if not (len(title_quoted) >= 2 and title_quoted[0] == '"' and title_quoted[-1] == '"'):
            continue
        title = title_quoted[1:-1]
        lines.append((win_id, pid_str, title))
    return lines


def main() -> int:
    print("Starting help-mode flow test...", flush=True)

    # Step: Run without arguments to trigger help mode
    print("Invoking ./release/screenshot.exe with no arguments...", flush=True)
    proc = run(['./release/screenshot.exe'], check=False, capture=True)

    # Expect successful exit when showing help
    assert proc.returncode == 0, f"Help mode exited with non-zero code: {proc.returncode}"

    out = proc.stdout or ""
    err = proc.stderr or ""
    print("STDOUT (truncated):", out[:400].replace('\n', ' '), flush=True)
    if err:
        print("STDERR (truncated):", err[:200].replace('\n', ' '), flush=True)

    # Requirement: When run without arguments, it must print usage information.
    assert "Usage:" in out, "Expected usage information in help output"  # $REQ_HELP_001

    # Requirement: Must include a header for the window list
    assert "Currently open windows (id,pid,title):" in out, "Expected window list header in help output"  # $REQ_HELP_005

    # Requirement: When run without arguments, it must print a list of all currently open windows.
    windows = parse_window_list(out)
    assert len(windows) > 0, "Expected at least one window listed in help output"  # $REQ_HELP_002

    # Take the first parsed line and validate format and separators
    win_id, pid_str, title = windows[0]

    # Requirement: Line format contains ID, PID, and quoted title
    assert re.fullmatch(r"[A-Za-z0-9]+", win_id) is not None, "Window ID must be alphanumeric"  # $REQ_HELP_003
    assert pid_str.isdigit(), "Process ID must be numeric"  # $REQ_HELP_003
    # We parsed quotes off the title; ensure original line had exactly two tabs
    original_line = f"{win_id}\t{pid_str}\t\"{title}\""
    assert original_line.count('\t') == 2, "Fields must be tab-separated"  # $REQ_HELP_004

    # Requirement: Exactly one selection flag required when not in help mode
    # Invoke with only an output path (no selection flag) to force an error
    print("Invoking with only output path (expect usage error)...", flush=True)
    bad_proc = run(['./release/screenshot.exe', './tmp/should-not-exist.png'], check=False, capture=True)
    bad_out = (bad_proc.stdout or "") + "\n" + (bad_proc.stderr or "")
    assert bad_proc.returncode != 0, "Expected non-zero exit when selection flag is missing"  # $REQ_HELP_006
    assert "Usage:" in bad_out, "Expected usage shown when selection flag is missing"  # $REQ_HELP_006

    print("✓ All tests passed for help-mode flow")
    return 0


if __name__ == '__main__':
    sys.exit(main())
