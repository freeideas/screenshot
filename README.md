# Screenshot

A simple command-line standalone AOT-compiled C# application that captures screenshots of specific windows by title, process ID, or window ID.

## Overview

`screenshot.exe` takes a screenshot of a window matching the specified criteria and saves it to a PNG file. This is similar to the functionality in `doc\example.cpp`.

## Usage

```bash
# Capture by window title to specific file
screenshot.exe --title "window title" output.png

# Capture by process ID to specific file
screenshot.exe --pid 1234 output.png

# Capture by window ID to specific file
screenshot.exe --id A32F output.png

# Capture to a directory with auto-generated timestamped filename
screenshot.exe --title "window title" ./screenshots/

# Capture to current directory with auto-generated timestamped filename
screenshot.exe --title "window title"

# Run without arguments to see list of windows with IDs and PIDs
screenshot.exe
```

### Arguments

The tool requires exactly one selection flag followed by its value:

- `--title <title>` -- Capture a window by its title. If multiple windows share the same title, one will be captured (unspecified which).
- `--pid <process-id>` -- Capture a window of a process by its numeric process ID. If the process has multiple windows, one will be captured (unspecified which).
- `--id <window-id>` -- Capture a window by its alphanumeric window ID. Window IDs uniquely identify a specific window.
- `<output-path>` (optional) -- The file path or directory where the PNG screenshot will be saved:
  - If a `.png` file path is specified, the screenshot is saved to that exact location
  - If a directory is specified, a timestamped filename is automatically generated in the format `YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png` (e.g., `2025-11-10-23-30-22-293532_screenshot.png`)
  - If omitted, the screenshot is saved to the current directory with an auto-generated timestamped filename

When a screenshot is successfully captured, the tool outputs `Wrote [filepath]` before exiting.

### Help Mode

Run without arguments to see usage information and a list of all currently open windows:

```bash
screenshot.exe
```

See `readme\HELP_TEXT.md` for detailed help mode documentation.

### Example

```bash
# Run without arguments to see available windows
screenshot.exe

# Capture a Notepad window by title to specific file
screenshot.exe --title "Untitled - Notepad" ./screenshots/notepad.png
# Output: Wrote ./screenshots/notepad.png

# Capture a browser window by process ID to specific file
screenshot.exe --pid 8124 ./output.png
# Output: Wrote ./output.png

# Capture a window by its unique ID to specific file
screenshot.exe --id A32F ./output.png
# Output: Wrote ./output.png

# Capture to a directory with auto-generated timestamped filename
screenshot.exe --title "Untitled - Notepad" ./screenshots/
# Output: Wrote ./screenshots/2025-11-10-23-30-22-293532_screenshot.png

# Capture to current directory with auto-generated timestamped filename
screenshot.exe --title "Untitled - Notepad"
# Output: Wrote ./2025-11-10-23-30-22-293532_screenshot.png
```

## Technical Details

- AOT compiled with no runtime dependencies required
- Outputs PNG format
- Captures the full window including title bar and decorations

## Testing

This project uses AI-based visual verification to test screenshot accuracy. Tests launch controlled `cmd.exe` windows, capture them using all three methods (by ID, title, and PID), and verify:

1. Screenshots are created with correct timestamped filenames
2. AI confirms screenshots plausibly match window titles
3. Each capture method works correctly

See `readme\TESTING.md` for detailed testing documentation.

## Filename Convention for Test Screenshots

Test screenshots use timestamped filenames for uniqueness and chronological ordering:

```
2025-11-10-14-54-02-779216_notepad.png
2025-11-10-14-54-15-123456_google-chrome.png
```

Format: `YYYY-MM-DD-HH-MM-SS-microseconds_window-description.png`

## Building

See the build instructions in the project source files.
