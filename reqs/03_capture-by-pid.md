# Capture by Process ID Flow

**Source:** ./README.md

Capture a screenshot of a window by specifying its process ID, save to output location.

## $REQ_PID_001: Capture Window by PID Flag
**Source:** ./README.md (Section: "Arguments")

When `--pid <process-id>` is specified, capture a window of a process by its numeric process ID. If the process has multiple windows, one will be captured (unspecified which).

## $REQ_PID_002: Save to Specified PNG File
**Source:** ./README.md (Section: "Arguments")

When a `.png` file path is specified as output, save the screenshot to that exact location.

## $REQ_PID_003: Output Success Message
**Source:** ./README.md (Section: "Arguments")

When a screenshot is successfully captured, output `Wrote [filepath]` before exiting.
