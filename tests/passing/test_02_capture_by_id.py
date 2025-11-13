#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime

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
        # Skip header lines
        if line.startswith("Usage:") or line.startswith("Run without arguments") or line.startswith("Currently open windows (id,pid,title):"):
            continue
        parts = line.split('\t')
        if len(parts) != 3:
            continue
        win_id, pid_str, title_quoted = parts
        # Expect quotes around title
        if not (len(title_quoted) >= 2 and title_quoted[0] == '"' and title_quoted[-1] == '"'):
            continue
        title = title_quoted[1:-1]
        lines.append((win_id, pid_str, title))
    return lines


def main() -> int:
    print("Starting capture-by-id flow test...", flush=True)

    # Step 1: Get list of windows
    print("Listing windows via ./release/screenshot.exe (help mode)...", flush=True)
    list_proc = run(['./release/screenshot.exe'], check=False, capture=True)
    if list_proc.returncode != 0:
        print(f"✗ Failed to list windows (exit {list_proc.returncode})")
        print(list_proc.stderr)
        return 1

    windows = parse_window_list(list_proc.stdout)
    assert len(windows) > 0, "No windows found to capture; ensure at least one visible window is open"  # $REQ_CAPTURE_ID_003

    # Choose the first window for determinism
    win_id, pid_str, title = windows[0]
    print(f"Selected window: id={win_id} pid={pid_str} title=\"{title}\"", flush=True)

    # Validate window id is alphanumeric (as documented)
    assert re.fullmatch(r"[A-Za-z0-9]+", win_id) is not None, "Window ID must be alphanumeric"  # $REQ_CAPTURE_ID_001

    # Step 2: Capture by --id to an output path
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
    out_dir = Path('./tmp')
    out_dir.mkdir(parents=True, exist_ok=True)
    # Sanitize title for filename
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", title).strip('-') or 'window'
    out_path = out_dir / f"{timestamp}_{sanitized}_by-id.png"

    print(f"Capturing by id to {out_path}...", flush=True)
    cap_proc = run(['./release/screenshot.exe', '--id', win_id, str(out_path)], check=False, capture=True)
    assert cap_proc.returncode == 0, f"Capture by --id failed (exit {cap_proc.returncode}): {cap_proc.stderr.strip()}"  # $REQ_CAPTURE_ID_001

    # Step 3: Verify output path handling and file creation
    assert out_path.exists(), f"Output file was not created at {out_path}"  # $REQ_CAPTURE_ID_002
    assert out_path.is_file(), f"Output path is not a file: {out_path}"  # $REQ_CAPTURE_ID_002
    assert out_path.stat().st_size > 0, f"Output file is empty: {out_path}"  # $REQ_CAPTURE_ID_002

    # Step 4: Visual plausibility check (AI-based) for capture correctness
    # Ask if the image plausibly looks like a screenshot of its window title
    prompt = (
        f"Does the image at {out_path} plausibly look like a screenshot of a window titled '{title}'? "
        f"Answer with YES or NO and a brief explanation."
    )
    print("Submitting AI verification prompt via the-system/scripts/prompt_agentic_coder.py...", flush=True)
    ai_proc = run(['uv', 'run', '--script', './the-system/scripts/prompt_agentic_coder.py'], check=False, capture=True)
    # The wrapper reads prompt from stdin; re-run passing input if needed
    if ai_proc.returncode != 0 or not ai_proc.stdout:
        # Fallback: explicitly provide prompt via subprocess.run with input
        ai_proc = subprocess.run(
            ['uv', 'run', '--script', './the-system/scripts/prompt_agentic_coder.py'],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

    ai_text = ai_proc.stdout or ""
    print("AI response (truncated):", ai_text[:300].replace('\n', ' '), flush=True)
    assert ai_proc.returncode == 0, f"AI verification tool failed (exit {ai_proc.returncode})"  # $REQ_CAPTURE_ID_003
    assert re.search(r"\bYES\b", ai_text, flags=re.IGNORECASE), "AI did not confirm screenshot plausibility (expected YES)"  # $REQ_CAPTURE_ID_003

    print("✓ All tests passed for capture-by-id flow")
    return 0


if __name__ == '__main__':
    sys.exit(main())

