# Capture Screenshot by Window ID Flow

**Source:** ./README.md

Capture a screenshot of a window by specifying its alphanumeric ID and save to a PNG file.

## $REQ_CAPTURE_ID_001: Accept Window ID Argument
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must accept an alphanumeric window ID as the first command-line argument.

## $REQ_CAPTURE_ID_002: Accept Output Path Argument
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must accept an output file path as the second command-line argument.

## $REQ_CAPTURE_ID_003: Capture Window by ID
**Source:** ./README.md (Section: "Arguments")

screenshot.exe must capture a screenshot of the window uniquely identified by the specified window ID.

## $REQ_CAPTURE_ID_004: Save as PNG File
**Source:** ./README.md (Section: "Technical Details")

screenshot.exe must save the captured screenshot in PNG format to the specified output path.

## $REQ_CAPTURE_ID_005: Include Window Decorations
**Source:** ./README.md (Section: "Technical Details")

The captured screenshot must include the full window including title bar and decorations.
