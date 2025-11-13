# Capture Screenshot by Process ID Flow

**Source:** ./README.md

Capture a screenshot of a window by specifying its process ID and save to a PNG file.

## $REQ_CAPTURE_PID_001: Accept --pid Flag
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must accept a `--pid` flag followed by a numeric process ID.

## $REQ_CAPTURE_PID_002: Accept Output Path Argument
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must accept an output file path as the final command-line argument.

## $REQ_CAPTURE_PID_003: Capture Window by Process ID
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must capture a screenshot of the main window belonging to the process with the specified process ID.

## $REQ_CAPTURE_PID_004: Handle Main Window Selection
**Source:** ./README.md (Section: "Arguments")

If the process has multiple windows, screenshot.exe must capture the main window of that process.
