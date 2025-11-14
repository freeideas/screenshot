# Help Mode Flow

**Source:** ./README.md, ./readme/HELP_TEXT.md

Display usage information and list all currently open windows when run without arguments.

## $REQ_HELP_001: Run Without Arguments

**Source:** ./README.md (Section: "Help Mode")

When executable is run without any arguments, display help text and window list.

## $REQ_HELP_002: Display Usage Examples

**Source:** ./readme/HELP_TEXT.md (Section: "Output Format")

Output must include usage examples showing the three capture modes with title, pid, and id flags.

## $REQ_HELP_003: Display Output Path Instructions

**Source:** ./readme/HELP_TEXT.md (Section: "Output Format")

Output must explain that output path is optional and describe the three path behaviors: explicit .png file, directory with timestamped filename, or omitted for current directory with timestamped filename.

## $REQ_HELP_004: Display Window List Header

**Source:** ./readme/HELP_TEXT.md (Section: "Output Format")

Output must include header line that labels the window list columns with format "Currently open windows (id,pid,title):".

## $REQ_HELP_005: List Open Windows

**Source:** ./readme/HELP_TEXT.md (Section: "Field Descriptions")

Output must list all currently open windows with one line per window in format: window-id, tab character, pid, tab character, window title in double quotes.

## $REQ_HELP_006: Window ID Format

**Source:** ./readme/HELP_TEXT.md (Section: "Window ID Format")

Window IDs must be alphanumeric hexadecimal values without 0x prefix.

## $REQ_HELP_007: PID Format

**Source:** ./readme/HELP_TEXT.md (Section: "Field Descriptions")

Process IDs must be numeric values.

## $REQ_HELP_008: Tab-Separated Fields

**Source:** ./readme/HELP_TEXT.md (Section: "Field Descriptions")

Fields in window list must be separated by tab characters.

## $REQ_HELP_009: Exit With Success

**Source:** ./readme/HELP_TEXT.md (Section: "Exit Code")

Help mode must exit with status code 0.
