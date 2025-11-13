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
        if line.startswith("Usage:") or line.startswith("Run without arguments") or line.startswith("Currently open windows:"):
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
    print("Starting capture-by-title flow test...", flush=True)

    # Step 1: Launch a cmd.exe window for controlled testing with a custom title
    print("Launching cmd.exe for controlled testing...", flush=True)
    cmd_process = subprocess.Popen(
        ['cmd.exe', '/K', 'title ScreenshotTestWindow'],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    cmd_pid = cmd_process.pid
    print(f"Launched cmd.exe with PID: {cmd_pid}", flush=True)

    # Give the window time to appear
    import time
    time.sleep(2)

    try:
        # Step 2: Get list of windows (help mode)
        print("Listing windows via ./release/screenshot.exe (help mode)...", flush=True)
        list_proc = run(['./release/screenshot.exe'], check=False, capture=True)
        if list_proc.returncode != 0:
            print(f"✗ Failed to list windows (exit {list_proc.returncode})")
            print(list_proc.stderr)
            return 1

        windows = parse_window_list(list_proc.stdout)
        assert len(windows) > 0, "No windows found to capture; ensure at least one visible window is open"  # $REQ_CAPTURE_TITLE_003

        # Find the Command Prompt window by matching the PID we just launched
        cmd_window = None
        for win_id, pid_str, title in windows:
            if int(pid_str) == cmd_pid:
                cmd_window = (win_id, pid_str, title)
                break

        assert cmd_window is not None, f"Could not find window with PID {cmd_pid} in window list"
        win_id, pid_str, title = cmd_window
        print(f"Selected window: id={win_id} pid={pid_str} title=\"{title}\"", flush=True)

        # Step 3: Capture by --title to an output path
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
        out_dir = Path('./tmp')
        out_dir.mkdir(parents=True, exist_ok=True)
        sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", title).strip('-') or 'window'
        out_title = out_dir / f"{timestamp}_{sanitized}_by-title.png"

        print(f"Capturing by title to {out_title}...", flush=True)
        cap_title = run(['./release/screenshot.exe', '--title', title, str(out_title)], check=False, capture=True)
        assert cap_title.returncode == 0, f"Capture by --title failed (exit {cap_title.returncode}): {cap_title.stderr.strip()}"  # $REQ_CAPTURE_TITLE_001

        # Step 4: Verify output path handling and file creation
        assert out_title.exists(), f"Output file was not created at {out_title}"  # $REQ_CAPTURE_TITLE_002
        assert out_title.is_file(), f"Output path is not a file: {out_title}"  # $REQ_CAPTURE_TITLE_002
        assert out_title.stat().st_size > 0, f"Output file is empty: {out_title}"  # $REQ_CAPTURE_TITLE_002

        # Step 5: Visual plausibility check (AI-based) for capture correctness by title
        prompt_match = (
            f"Does the image at {out_title} plausibly look like a screenshot of a command prompt/terminal window with title 'ScreenshotTestWindow'? "
            f"Answer with YES or NO and a brief explanation."
        )
        print("Submitting AI verification prompt for plausibility...", flush=True)
        ai_proc1 = subprocess.run(
            ['uv', 'run', '--script', './the-system/scripts/prompt_agentic_coder.py'],
            input=prompt_match,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        ai_text1 = ai_proc1.stdout or ""
        print("AI plausibility response (truncated):", ai_text1[:300].replace('\n', ' '), flush=True)
        assert ai_proc1.returncode == 0, f"AI verification tool failed (exit {ai_proc1.returncode})"  # $REQ_CAPTURE_TITLE_003
        assert re.search(r"\bYES\b", ai_text1, flags=re.IGNORECASE), "AI did not confirm screenshot plausibility (expected YES)"  # $REQ_CAPTURE_TITLE_003

        # Step 6: Test duplicate title handling (REQ_CAPTURE_TITLE_004)
        # Launch a second cmd.exe with the SAME title to test duplicate handling
        print("Launching second cmd.exe with duplicate title for REQ_CAPTURE_TITLE_004...", flush=True)
        cmd_process2 = subprocess.Popen(
            ['cmd.exe', '/K', 'title ScreenshotTestWindow'],
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        time.sleep(2)  # Give window time to appear

        try:
            # Now there are TWO windows with title "ScreenshotTestWindow"
            # Try to capture by title -- it should capture one of them successfully
            out_duplicate = out_dir / f"{timestamp}_ScreenshotTestWindow_duplicate-title-test.png"
            print(f"Capturing by duplicate title to {out_duplicate}...", flush=True)
            cap_duplicate = run(['./release/screenshot.exe', '--title', 'ScreenshotTestWindow', str(out_duplicate)], check=False, capture=True)
            assert cap_duplicate.returncode == 0, f"Capture by --title with duplicate titles failed (exit {cap_duplicate.returncode}): {cap_duplicate.stderr.strip()}"  # $REQ_CAPTURE_TITLE_004
            assert out_duplicate.exists() and out_duplicate.stat().st_size > 0, "Duplicate-title capture did not produce a non-empty file"  # $REQ_CAPTURE_TITLE_004
            print("✓ Duplicate title test passed (REQ_CAPTURE_TITLE_004)")
        finally:
            # Clean up second cmd.exe
            print("Cleaning up second cmd.exe process...", flush=True)
            try:
                cmd_process2.terminate()
                cmd_process2.wait(timeout=5)
            except Exception as e:
                print(f"Warning: Failed to cleanly terminate second cmd.exe: {e}", flush=True)
                try:
                    cmd_process2.kill()
                except Exception:
                    pass

        print("✓ All tests passed for capture-by-title flow")
        return 0

    finally:
        # Cleanup: Kill the cmd.exe process
        print("Cleaning up cmd.exe process...", flush=True)
        try:
            cmd_process.terminate()
            cmd_process.wait(timeout=5)
        except Exception as e:
            print(f"Warning: Failed to cleanly terminate cmd.exe: {e}", flush=True)
            try:
                cmd_process.kill()
            except Exception:
                pass


if __name__ == '__main__':
    sys.exit(main())

