# Capture by Window ID Flow

**Source:** ./README.md (Section: "Usage"), ./readme/HELP_TEXT.md (Section: "Use Cases")

Capture a screenshot of a window specified by its unique window ID.

## $REQ_ID_001: Accept Window ID Argument
**Source:** ./README.md (Section: "Arguments")

Accept `--id <window-id>` flag with an alphanumeric window ID value.

## $REQ_ID_002: Capture Window by ID
**Source:** ./README.md (Section: "Arguments")

Capture a screenshot of the window matching the specified window ID.

## $REQ_ID_003: Save to Explicit File Path
**Source:** ./README.md (Section: "Arguments")

When output path is a .png file path, save screenshot to that exact location.

## $REQ_ID_004: Save to Directory with Timestamped Filename
**Source:** ./README.md (Section: "Arguments")

When output path is a directory, save screenshot with auto-generated timestamped filename in format `YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png`.

## $REQ_ID_005: Save to Current Directory with Timestamped Filename
**Source:** ./README.md (Section: "Arguments")

When output path is omitted, save screenshot to current directory with auto-generated timestamped filename.

## $REQ_ID_006: Output Success Message
**Source:** ./README.md (Section: "Arguments")

When screenshot is successfully captured, output "Wrote [filepath]" before exiting.

## $REQ_ID_007: PNG Format Output
**Source:** ./README.md (Section: "Technical Details")

Output screenshots in PNG format.

## $REQ_ID_008: Capture Full Window
**Source:** ./README.md (Section: "Technical Details")

Capture the full window including title bar and decorations.
