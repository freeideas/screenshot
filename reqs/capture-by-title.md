# Capture by Title Flow

**Source:** ./README.md

Capture a screenshot of a window by matching its title.

## $REQ_TITLE_001: Accept Title Flag

**Source:** ./README.md (Section: "Arguments")

Tool must accept --title flag followed by a window title string.

## $REQ_TITLE_002: Match Window by Title

**Source:** ./README.md (Section: "Arguments")

Tool must capture a window whose title matches the provided string.

## $REQ_TITLE_003: Save PNG File

**Source:** ./README.md (Section: "Technical Details")

Tool must save the captured screenshot in PNG format.

## $REQ_TITLE_004: Capture Full Window

**Source:** ./README.md (Section: "Technical Details")

Tool must capture the full window including title bar and decorations.

## $REQ_TITLE_005: Output to Specific File

**Source:** ./README.md (Section: "Arguments")

When output path is a .png file path, save screenshot to that exact location.

## $REQ_TITLE_006: Output to Directory with Timestamp

**Source:** ./README.md (Section: "Arguments")

When output path is a directory, generate timestamped filename in format YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png.

## $REQ_TITLE_007: Output to Current Directory

**Source:** ./README.md (Section: "Arguments")

When output path is omitted, save to current directory with auto-generated timestamped filename.

## $REQ_TITLE_008: Display Success Message

**Source:** ./README.md (Section: "Arguments")

When screenshot is successfully captured, output "Wrote [filepath]" before exiting.
