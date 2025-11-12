# Screenshot

A simple command-line standalone AOT-compiled C# application that captures screenshots of specific windows by title or ID.

## Overview

`screenshot.exe` takes a screenshot of a window matching the specified title or ID and saves it to a PNG file. This is similar to the functionality in `doc\example.cpp`, except instead of capturing the entire desktop, it captures a specific window by its title or ID.

## Usage

```bash
screenshot.exe "window title" ./path/to/output.png
# OR
screenshot.exe <window-id> ./path/to/output.png

# Run without arguments to see list of windows with IDs
screenshot.exe
```

### Arguments

1. **Window Title or ID** (required) -- Either the title of the window to capture OR the window ID. If a window title is provided and multiple windows share the same title, one will be captured (which one is unspecified). Window IDs uniquely identify a specific window.
2. **Output Path** (required) -- The file path where the PNG screenshot will be saved.

### Help Mode

If `screenshot.exe` is run without exactly two command-line arguments, it will print usage information followed by a list of all currently open windows. Each line in the window list shows an alphanumeric window ID, followed by a space, followed by the quoted window title. This makes it easy to find the exact window title or ID to use.

Format: `<id> "window title"`

### Example

```bash
# Run without arguments to see available windows
screenshot.exe
# Output shows:
# Currently open windows:
#
#   A32F "Untitled - Notepad"
#   9939x4Q9 "Google Chrome"
#   123 "Visual Studio Code"

# Capture a Notepad window by title
screenshot.exe "Untitled - Notepad" ./screenshots/notepad.png

# Capture a browser window by title
screenshot.exe "Google Chrome" ./output.png

# Capture a window by ID (alphanumeric)
screenshot.exe A32F ./output.png
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
