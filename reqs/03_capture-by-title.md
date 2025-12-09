# Capture by Title Flow

**Source:** ./README.md

Capture a screenshot of a window by specifying its title, save to output location.

## $REQ_TITLE_001: Capture Window by Title Flag
**Source:** ./README.md (Section: "Arguments")

When `--title <title>` is specified, capture a window matching that title. If multiple windows share the same title, one will be captured (unspecified which).

## $REQ_TITLE_002: Save to Specified PNG File
**Source:** ./README.md (Section: "Arguments")

When a `.png` file path is specified as output, save the screenshot to that exact location.

## $REQ_TITLE_003: Output Success Message
**Source:** ./README.md (Section: "Arguments")

When a screenshot is successfully captured, output `Wrote [filepath]` before exiting.
