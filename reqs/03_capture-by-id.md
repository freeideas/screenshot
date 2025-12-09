# Capture by Window ID Flow

**Source:** ./README.md

Capture a screenshot of a window by specifying its unique window ID, save to output location.

## $REQ_ID_001: Capture Window by ID Flag
**Source:** ./README.md (Section: "Arguments")

When `--id <window-id>` is specified, capture a window by its alphanumeric window ID. Window IDs uniquely identify a specific window.

## $REQ_ID_002: Save to Specified PNG File
**Source:** ./README.md (Section: "Arguments")

When a `.png` file path is specified as output, save the screenshot to that exact location.

## $REQ_ID_003: Output Success Message
**Source:** ./README.md (Section: "Arguments")

When a screenshot is successfully captured, output `Wrote [filepath]` before exiting.
