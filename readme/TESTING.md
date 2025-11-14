# Testing Strategy

## Overview

Testing for `screenshot.exe` uses direct invocation of `./release/screenshot.exe` with AI-based visual verification to confirm that captured screenshots plausibly match their window titles.

**Note:** This project tests `screenshot.exe` directly, not via `test-screenshot.py` (which is a general-purpose GUI testing tool used in other projects).

## Test Approach

Tests invoke `./release/screenshot.exe` directly with controlled `cmd.exe` windows for reliable, repeatable testing:

1. **Help Mode Test** -- Validates window list format: `<window-id>\t<pid>\t"window title"`
2. **Capture by ID Test** -- Captures first available window by its window ID, verifies with AI
3. **Capture by Title Test** -- Launches controlled cmd.exe, captures by title, verifies with AI
4. **Capture by PID Test** -- Launches controlled cmd.exe, captures by PID, verifies with AI
5. **File Output Test** -- Validates PNG format signature, file creation, and window decorations

All screenshots use timestamped filenames: `YYYY-MM-DD-HH-MM-SS-microseconds_description.png`

## Filename Convention

All test screenshots use timestamped filenames:

```
2025-11-10-14-54-02-779216_notepad.png
2025-11-10-14-54-15-123456_google-chrome.png
2025-11-10-14-55-30-987654_visual-studio-code.png
```

Format: `YYYY-MM-DD-HH-MM-SS-microseconds_window-description.png`

This ensures:
- Unique filenames for each test run
- Chronological ordering
- Easy identification of what was captured

## Creating Controlled Test Windows

For reliable, repeatable testing, use `cmd.exe` with a custom title:

```python
import subprocess
import time

# Launch cmd.exe with a unique, predictable title
cmd_process = subprocess.Popen(
    ['cmd.exe', '/K', 'title MyTestWindow'],
    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
)
cmd_pid = cmd_process.pid
time.sleep(2)  # Give window time to appear

# Find the window by matching its PID
# ... run screenshot.exe to get window list ...
# ... match window by PID ...
# ... use the matched window's exact title for testing ...

# Always clean up when done
try:
    cmd_process.terminate()
    cmd_process.wait(timeout=5)
except Exception:
    cmd_process.kill()
```

**Why this approach works:**
- `cmd.exe` is available on every Windows system
- The `title` command sets a completely predictable window title
- Matching by PID ensures you get the exact window you launched
- Unique titles avoid conflicts with other windows
- Clean up is straightforward

## AI-Based Visual Verification

Instead of pixel-by-pixel comparison, we use AI to verify visual correctness. The AI examines:
- Visual elements consistent with the window title
- Presence of expected UI elements (title bar, borders)
- Overall plausibility of the screenshot

## What We Test

1. **Build Artifacts** -- Validates that `./release/screenshot.exe` is built correctly
2. **Window List Format** -- Verifies format: `<window-id>\t<pid>\t"window title"` with proper tab separators
3. **Capture by ID** -- Validates window ID is alphanumeric, file is created, AI verifies plausibility
4. **Capture by Title** -- Validates title capture works, AI verifies plausibility
5. **Capture by PID** -- Validates numeric PID capture works, AI verifies plausibility
6. **Multiple Windows** -- When multiple windows share same title/PID, validates that one window is captured successfully
7. **PNG Format** -- Validates PNG signature bytes and file structure
8. **Window Decorations** -- AI verifies full window including title bar and borders is captured
9. **File Creation** -- Verifies output files are created at specified locations with non-zero size
10. **Output Messages** -- Validates that tool outputs `Wrote [filepath]` after successful capture
11. **Output Path Handling** -- Tests explicit file paths, directory paths, and omitted paths (defaults to current directory)

## Rationale

Traditional visual verification requires:
- Image comparison libraries
- Reference screenshots
- Complex pixel-by-pixel analysis

AI-based verification provides:
- Natural language understanding of window titles
- Flexible visual recognition
- Human-like assessment of "does this look right?"
- No need for reference images

## Running Tests

```bash
# Run all passing tests
uv run --script ./the-system/scripts/test.py --passing

# Run a specific test
uv run --script ./the-system/scripts/test.py ./tests/passing/test_02_capture_by_pid.py
```

## Test Examples

Each test launches controlled windows and validates specific functionality:

**Capture by PID:**
```python
# Launch controlled cmd.exe window
cmd_process = subprocess.Popen(['cmd.exe', '/K', 'title MyTestWindow'])
cmd_pid = cmd_process.pid

# Capture by PID
screenshot.exe --pid {cmd_pid} ./tmp/{timestamp}_by-pid.png
# Output: Wrote ./tmp/2025-11-10-13-59-01-48215_by-pid.png

# AI verifies the screenshot plausibly shows a cmd.exe window
```

**Multiple Windows with Same Title/PID:**
```python
# Launch two cmd.exe windows with same title
subprocess.Popen(['cmd.exe', '/K', 'title SameTitle'])
subprocess.Popen(['cmd.exe', '/K', 'title SameTitle'])

# Capture by title -- should capture one of them successfully
screenshot.exe --title "SameTitle" ./tmp/output.png
# Output: Wrote ./tmp/output.png
# Test verifies: file was created and contains a valid screenshot (doesn't matter which window)
```
