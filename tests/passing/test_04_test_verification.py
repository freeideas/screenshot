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
        # Skip header and usage lines
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
    print("Starting file output verification flow...", flush=True)

    # Step 1: Launch a cmd.exe window for controlled testing with a custom title
    print("Launching cmd.exe for controlled testing...", flush=True)
    cmd_process = subprocess.Popen(
        ['cmd.exe', '/K', 'title ScreenshotTestWindowVerification'],
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    cmd_pid = cmd_process.pid
    print(f"Launched cmd.exe with PID: {cmd_pid}", flush=True)

    # Give the window time to appear
    import time
    time.sleep(2)

    try:
        # Step 2: Get list of windows (help mode)
        print("Listing windows via ./release/screenshot.exe...", flush=True)
        list_proc = run(['./release/screenshot.exe'], check=False, capture=True)
        if list_proc.returncode != 0:
            print(f"âœ— Failed to list windows (exit {list_proc.returncode})")
            print(list_proc.stderr)
            return 1

        windows = parse_window_list(list_proc.stdout)
        assert len(windows) > 0, "No windows found to capture; ensure at least one visible window is open"

        # Find the Command Prompt window by matching the PID we just launched
        cmd_window = None
        for win_id, pid_str, title in windows:
            if int(pid_str) == cmd_pid:
                cmd_window = (win_id, pid_str, title)
                break

        assert cmd_window is not None, f"Could not find window with PID {cmd_pid} in window list"
        win_id, pid_str, title = cmd_window
        print(f"Selected window: id={win_id} pid={pid_str} title=\"{title}\"", flush=True)

        # Prepare output path
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')
        out_dir = Path('./tmp')
        out_dir.mkdir(parents=True, exist_ok=True)
        sanitized = re.sub(r"[^A-Za-z0-9._-]+", "-", title).strip('-') or 'window'
        out_path = out_dir / f"{timestamp}_{sanitized}_verification.png"

        # Step 3: Capture by --id to specified output path
        print(f"Capturing by --id to {out_path}...", flush=True)
        cap_proc = run(['./release/screenshot.exe', '--id', win_id, str(out_path)], check=False, capture=True)
        if cap_proc.returncode != 0:
            print(f"Capture failed (exit {cap_proc.returncode})")
            print(cap_proc.stderr)
            return 1

        # Step 4: Verify file was created at specified path
        assert out_path.exists(), f"Output file was not created at {out_path}"  # $REQ_OUTPUT_001
        assert out_path.is_file(), f"Output path is not a file: {out_path}"  # $REQ_OUTPUT_001

        # Step 5: Verify PNG format by checking signature bytes
        sig = b''
        try:
            with out_path.open('rb') as f:
                sig = f.read(8)
        except Exception as e:
            print(f"Error reading output file: {e}")
        assert sig == b"\x89PNG\r\n\x1a\n", "Output file does not have PNG signature"  # $REQ_OUTPUT_002

        # Step 6: Verify file has content (> 0 bytes)
        assert out_path.stat().st_size > 0, f"Output PNG file is empty: {out_path}"  # $REQ_OUTPUT_004

        # Step 7: Visual check for window decorations (AI-based)
        prompt = (
            f"Does the image at {out_path} show the full window including the title bar and standard window decorations (borders, title area)? "
            f"Answer with YES or NO and a brief explanation."
        )
        print("Submitting AI verification prompt for window decorations...", flush=True)
        ai_proc = subprocess.run(
            ['uv', 'run', '--script', './the-system/scripts/prompt_agentic_coder.py'],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        ai_text = ai_proc.stdout or ""
        print("AI response (truncated):", (ai_text[:300] if ai_text else '').replace('\n', ' '), flush=True)
        assert ai_proc.returncode == 0, f"AI verification tool failed (exit {ai_proc.returncode})"  # $REQ_OUTPUT_003
        assert re.search(r"\bYES\b", ai_text, flags=re.IGNORECASE), "AI did not confirm presence of window decorations (expected YES)"  # $REQ_OUTPUT_003

        print("All tests passed for file output verification flow")
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
