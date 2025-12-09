# Output Path Handling Flow

**Source:** ./README.md

Handle various output path specifications: explicit file, directory, or default to current directory.

## $REQ_OUTPUT_001: Save to Explicit PNG Path
**Source:** ./README.md (Section: "Arguments")

When a `.png` file path is specified, save the screenshot to that exact location.

## $REQ_OUTPUT_002: Save to Directory with Timestamped Filename
**Source:** ./README.md (Section: "Arguments")

When a directory is specified, generate a timestamped filename in the format `YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png` (e.g., `2025-11-10-23-30-22-293532_screenshot.png`) and save in that directory.

## $REQ_OUTPUT_003: Default to Current Directory with Timestamped Filename
**Source:** ./README.md (Section: "Arguments")

When output path is omitted, save the screenshot to the current directory with an auto-generated timestamped filename.

## $REQ_OUTPUT_004: Output Format is PNG
**Source:** ./README.md (Section: "Technical Details")

The screenshot is saved in PNG format.
