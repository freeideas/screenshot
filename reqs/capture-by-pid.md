# Capture by Process ID Flow

**Source:** ./README.md (Section: "Usage")

Capture a screenshot of a window of a process specified by its process ID.

## $REQ_PID_001: Accept Process ID Argument
**Source:** ./README.md (Section: "Arguments")

Accept `--pid <process-id>` flag with a numeric process ID value.

## $REQ_PID_002: Capture Window by PID
**Source:** ./README.md (Section: "Arguments")

Capture a screenshot of a window of the process matching the specified process ID.

## $REQ_PID_003: Handle Multiple Windows for Process
**Source:** ./README.md (Section: "Arguments")

If the process has multiple windows, one will be captured (unspecified which).

## $REQ_PID_004: Save to Explicit File Path
**Source:** ./README.md (Section: "Arguments")

When output path is a .png file path, save screenshot to that exact location.

## $REQ_PID_005: Save to Directory with Timestamped Filename
**Source:** ./README.md (Section: "Arguments")

When output path is a directory, save screenshot with auto-generated timestamped filename in format `YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png`.

## $REQ_PID_006: Save to Current Directory with Timestamped Filename
**Source:** ./README.md (Section: "Arguments")

When output path is omitted, save screenshot to current directory with auto-generated timestamped filename.

## $REQ_PID_007: Output Success Message
**Source:** ./README.md (Section: "Arguments")

When screenshot is successfully captured, output "Wrote [filepath]" before exiting.

## $REQ_PID_008: PNG Format Output
**Source:** ./README.md (Section: "Technical Details")

Output screenshots in PNG format.

## $REQ_PID_009: Capture Full Window
**Source:** ./README.md (Section: "Technical Details")

Capture the full window including title bar and decorations.
