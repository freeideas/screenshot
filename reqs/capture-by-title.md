# Capture Screenshot by Window Title Flow

**Source:** ./README.md

Capture a screenshot of a window by specifying its title and save to a PNG file.

## $REQ_CAPTURE_TITLE_001: Accept --title Flag
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must accept a `--title` flag followed by a window title string.

## $REQ_CAPTURE_TITLE_002: Accept Output Path Argument
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must accept an output file path as the final command-line argument.

## $REQ_CAPTURE_TITLE_003: Capture Window by Title
**Source:** ./README.md (Section: "Overview")

screenshot.exe must capture a screenshot of the window matching the specified title.

## $REQ_CAPTURE_TITLE_004: Handle Multiple Windows With Same Title
**Source:** ./README.md (Section: "Arguments")

If a window title is provided and multiple windows share the same title, screenshot.exe must capture one of those windows.
