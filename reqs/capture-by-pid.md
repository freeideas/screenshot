# Capture by PID Flow

**Source:** ./README.md

Capture a screenshot of a window by matching its process ID.

## $REQ_PID_001: Accept PID Flag

**Source:** ./README.md (Section: "Arguments")

Tool must accept --pid flag followed by a numeric process ID.

## $REQ_PID_002: Match Window by PID

**Source:** ./README.md (Section: "Arguments")

Tool must capture a window belonging to the process with the specified numeric process ID.

## $REQ_PID_003: Save PNG File

**Source:** ./README.md (Section: "Technical Details")

Tool must save the captured screenshot in PNG format.

## $REQ_PID_004: Capture Full Window

**Source:** ./README.md (Section: "Technical Details")

Tool must capture the full window including title bar and decorations.

## $REQ_PID_005: Output to Specific File

**Source:** ./README.md (Section: "Arguments")

When output path is a .png file path, save screenshot to that exact location.

## $REQ_PID_006: Output to Directory with Timestamp

**Source:** ./README.md (Section: "Arguments")

When output path is a directory, generate timestamped filename in format YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png.

## $REQ_PID_007: Output to Current Directory

**Source:** ./README.md (Section: "Arguments")

When output path is omitted, save to current directory with auto-generated timestamped filename.

## $REQ_PID_008: Display Success Message

**Source:** ./README.md (Section: "Arguments")

When screenshot is successfully captured, output "Wrote [filepath]" before exiting.
