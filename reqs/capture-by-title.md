# Capture Screenshot by Window Title Flow

**Source:** ./README.md

Capture a screenshot of a window by specifying its title and save to a PNG file.

## $REQ_CAPTURE_TITLE_001: Accept Window Title Argument
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must accept a window title as the first command-line argument.

## $REQ_CAPTURE_TITLE_002: Accept Output Path Argument
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must accept an output file path as the second command-line argument.

## $REQ_CAPTURE_TITLE_003: Capture Window by Title
**Source:** ./README.md (Section: "Overview")

screenshot.exe must capture a screenshot of the window matching the specified title.

## $REQ_CAPTURE_TITLE_004: Save as PNG File
**Source:** ./README.md (Section: "Technical Details")

screenshot.exe must save the captured screenshot in PNG format to the specified output path.

## $REQ_CAPTURE_TITLE_005: Include Window Decorations
**Source:** ./README.md (Section: "Technical Details")

The captured screenshot must include the full window including title bar and decorations.

## $REQ_CAPTURE_TITLE_006: Handle Multiple Windows With Same Title
**Source:** ./README.md (Section: "Arguments")

If a window title is provided and multiple windows share the same title, screenshot.exe must capture one of those windows.
