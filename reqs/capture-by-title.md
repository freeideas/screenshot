# Capture by Window Title Flow

**Source:** ./README.md (Section: "Usage")

Capture a screenshot of a window specified by its title.

## $REQ_TITLE_001: Accept Window Title Argument
**Source:** ./README.md (Section: "Arguments")

Accept `--title <title>` flag with a window title string value.

## $REQ_TITLE_002: Capture Window by Title
**Source:** ./README.md (Section: "Arguments")

Capture a screenshot of a window matching the specified title.

## $REQ_TITLE_003: Handle Multiple Windows with Same Title
**Source:** ./README.md (Section: "Arguments")

If multiple windows share the same title, one will be captured (unspecified which).

## $REQ_TITLE_004: Save to Explicit File Path
**Source:** ./README.md (Section: "Arguments")

When output path is a .png file path, save screenshot to that exact location.

## $REQ_TITLE_005: Save to Directory with Timestamped Filename
**Source:** ./README.md (Section: "Arguments")

When output path is a directory, save screenshot with auto-generated timestamped filename in format `YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png`.

## $REQ_TITLE_006: Save to Current Directory with Timestamped Filename
**Source:** ./README.md (Section: "Arguments")

When output path is omitted, save screenshot to current directory with auto-generated timestamped filename.

## $REQ_TITLE_007: Output Success Message
**Source:** ./README.md (Section: "Arguments")

When screenshot is successfully captured, output "Wrote [filepath]" before exiting.

## $REQ_TITLE_008: PNG Format Output
**Source:** ./README.md (Section: "Technical Details")

Output screenshots in PNG format.

## $REQ_TITLE_009: Capture Full Window
**Source:** ./README.md (Section: "Technical Details")

Capture the full window including title bar and decorations.
