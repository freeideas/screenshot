# Capture by Window ID Flow

**Source:** ./README.md

Capture a screenshot of a window by matching its unique window ID.

## $REQ_ID_001: Accept ID Flag

**Source:** ./README.md (Section: "Arguments")

Tool must accept --id flag followed by an alphanumeric window ID.

## $REQ_ID_002: Match Window by ID

**Source:** ./README.md (Section: "Arguments")

Tool must capture the window with the specified alphanumeric window ID.

## $REQ_ID_003: Unique Window Identification

**Source:** ./README.md (Section: "Arguments")

Window IDs uniquely identify a specific window.

## $REQ_ID_004: Save PNG File

**Source:** ./README.md (Section: "Technical Details")

Tool must save the captured screenshot in PNG format.

## $REQ_ID_005: Capture Full Window

**Source:** ./README.md (Section: "Technical Details")

Tool must capture the full window including title bar and decorations.

## $REQ_ID_006: Output to Specific File

**Source:** ./README.md (Section: "Arguments")

When output path is a .png file path, save screenshot to that exact location.

## $REQ_ID_007: Output to Directory with Timestamp

**Source:** ./README.md (Section: "Arguments")

When output path is a directory, generate timestamped filename in format YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png.

## $REQ_ID_008: Output to Current Directory

**Source:** ./README.md (Section: "Arguments")

When output path is omitted, save to current directory with auto-generated timestamped filename.

## $REQ_ID_009: Display Success Message

**Source:** ./README.md (Section: "Arguments")

When screenshot is successfully captured, output "Wrote [filepath]" before exiting.
