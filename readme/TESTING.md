# Testing Strategy

## Overview

Testing for `screenshot.exe` uses AI-based visual verification to confirm that captured screenshots plausibly match their window titles.

## Test Approach

1. **Get Window List** -- Run `screenshot.exe` without arguments to get a list of currently open windows (format: `<id> "window title"`)
2. **Random Selection** -- Pick a random window from the list
3. **Capture by ID** -- Run `screenshot.exe` with the window's ID to capture first screenshot
4. **Capture by Title** -- Run `screenshot.exe` with the window's title to capture second screenshot
5. **Timestamped Filenames** -- Save both screenshots with timestamp prefixes: `YYYY-MM-DD-HH-MM-SS-microseconds_sanitized-window-title_by-id.png` and `YYYY-MM-DD-HH-MM-SS-microseconds_sanitized-window-title_by-title.png`
6. **AI Verification (Part 1)** -- Use `the-system\scripts\prompt_agentic_coder.py` to ask an AI whether each .png file plausibly looks like a screenshot of the window title
7. **AI Verification (Part 2)** -- Ask the AI to verify that both screenshots are nearly identical (same window captured twice)

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

## AI-Based Visual Verification

Instead of pixel-by-pixel comparison, we use AI to verify visual correctness:

```bash
# 1. Get list of available windows
screenshot.exe

# 2. Pick a random window (e.g., A32F "Notepad")
# 3. Capture by ID
screenshot.exe A32F ./tmp/2025-11-10-14-54-02-779216_notepad_by-id.png

# 4. Capture by title
screenshot.exe "Notepad" ./tmp/2025-11-10-14-54-03-123456_notepad_by-title.png

# 5. Ask AI to verify each screenshot matches the title
echo "Does the image at ./tmp/2025-11-10-14-54-02-779216_notepad_by-id.png plausibly look like a screenshot of a window titled 'Notepad'?" | the-system/scripts/prompt_agentic_coder.py

# 6. Ask AI to verify both screenshots are nearly identical
echo "Compare ./tmp/2025-11-10-14-54-02-779216_notepad_by-id.png and ./tmp/2025-11-10-14-54-03-123456_notepad_by-title.png -- are these two screenshots nearly identical (same window captured twice)?" | the-system/scripts/prompt_agentic_coder.py
```

The AI examines:
- Visual elements consistent with the window title
- Presence of expected UI elements
- Overall plausibility of the match
- Whether both capture methods (by ID and by title) produce nearly identical screenshots

## What We Test

1. **File Creation** -- Verify that the output PNG files are created at the specified locations
2. **Non-Zero Size** -- Verify that the output files have sizes greater than 0 bytes
3. **Window List Format** -- Verify that the window list output follows the format: `<id> "window title"`
4. **Visual Correctness** -- AI verifies each screenshot plausibly matches the window title
5. **ID vs Title Consistency** -- AI verifies that capturing by ID and by title produces nearly identical screenshots of the same window

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

## Test Examples

```bash
# Get list of available windows (format: <id> "window title")
screenshot.exe
# Example output:
#   A32F "Notepad"
#   9939x4Q9 "Google Chrome"
#   123 "Visual Studio Code"

# Capture same window by ID and by title
screenshot.exe A32F ./tmp/2025-11-10-14-54-02-779216_notepad_by-id.png
screenshot.exe "Notepad" ./tmp/2025-11-10-14-54-03-123456_notepad_by-title.png

# Verify files exist and have content
test -f ./tmp/2025-11-10-14-54-02-779216_notepad_by-id.png && [ -s ./tmp/2025-11-10-14-54-02-779216_notepad_by-id.png ] && echo "PASS: File by ID exists and has content"
test -f ./tmp/2025-11-10-14-54-03-123456_notepad_by-title.png && [ -s ./tmp/2025-11-10-14-54-03-123456_notepad_by-title.png ] && echo "PASS: File by title exists and has content"

# Use AI to verify visual correctness of each screenshot
echo "Does the image at ./tmp/2025-11-10-14-54-02-779216_notepad_by-id.png plausibly look like a screenshot of a window titled 'Notepad'? Answer with YES or NO and brief explanation." | the-system/scripts/prompt_agentic_coder.py

# Use AI to verify both screenshots are nearly identical
echo "Compare ./tmp/2025-11-10-14-54-02-779216_notepad_by-id.png and ./tmp/2025-11-10-14-54-03-123456_notepad_by-title.png -- are these two screenshots nearly identical (same window captured twice)? Answer with YES or NO and brief explanation." | the-system/scripts/prompt_agentic_coder.py
```
