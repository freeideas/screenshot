# Screenshot

A simple command-line standalone AOT-compiled C# application that captures screenshots of specific windows by title, process ID, or window ID.

## Overview

`screenshot.exe` takes a screenshot of a window matching the specified criteria and saves it to a PNG file. This is similar to the functionality in `doc\example.cpp`.

## Usage

```bash
# Capture by window title
screenshot.exe --title "window title" output.png

# Capture by process ID
screenshot.exe --pid 1234 output.png

# Capture by window ID
screenshot.exe --id A32F output.png

# Capture to a directory with auto-generated timestamped filename
screenshot.exe --title "window title" ./screenshots/

# Run without arguments to see list of windows with IDs and PIDs
screenshot.exe
```

### Arguments

The tool requires exactly one selection flag followed by its value, and an output path:

- `--title <title>` -- Capture a window by its title. If multiple windows share the same title, one will be captured (which one is unspecified).
- `--pid <process-id>` -- Capture the main window of a process by its numeric process ID. If the process has multiple windows, the main window will be captured.
- `--id <window-id>` -- Capture a window by its alphanumeric window ID. Window IDs uniquely identify a specific window.
- `<output-path>` (required) -- The file path where the PNG screenshot will be saved. If the path is a directory, a timestamped filename will be automatically generated in the format `YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png` (e.g., `2025-11-10-23-30-22-293532_screenshot.png`).

### Help Mode

If `screenshot.exe` is run without arguments, it will print usage information followed by a list of all currently open windows. Each line in the window list shows:

Format: `<window-id>\t<pid>\t"window title"`

Where:
- `<window-id>` is an alphanumeric identifier for the window
- `<pid>` is the numeric process ID
- `"window title"` is the window title in quotes
- Fields are separated by tab characters (`\t`)

### Example

```bash
# Run without arguments to see available windows
screenshot.exe
# Output shows:
# Currently open windows:
#
#   A32F	5432	"Untitled - Notepad"
#   9939x4Q9	8124	"Google Chrome"
#   123	4567	"Visual Studio Code"

# Capture a Notepad window by title
screenshot.exe --title "Untitled - Notepad" ./screenshots/notepad.png

# Capture a browser window by process ID
screenshot.exe --pid 8124 ./output.png

# Capture a window by its unique ID
screenshot.exe --id A32F ./output.png

# Capture to a directory with auto-generated timestamped filename
screenshot.exe --title "Untitled - Notepad" ./screenshots/
# Creates: ./screenshots/2025-11-10-23-30-22-293532_screenshot.png
```

## Technical Details

- AOT compiled with no runtime dependencies required
- Outputs PNG format
- Captures the full window including title bar and decorations

## Testing

This project uses AI-based visual verification to test screenshot accuracy. The testing approach:

1. Randomly selects a window from the list returned by `screenshot.exe`
2. Captures a screenshot with a timestamped filename (e.g., `2025-11-10-14-54-02-779216_notepad.png`)
3. Uses `the-system\scripts\prompt_agentic_coder.py` to ask an AI whether the .png file plausibly looks like a screenshot of its window title

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
