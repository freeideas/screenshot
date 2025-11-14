# Help Mode Flow

**Source:** ./README.md (Section: "Help Mode"), ./readme/HELP_TEXT.md

Run without arguments to display usage information and window list.

## $REQ_HELP_001: Display Usage Examples
**Source:** ./readme/HELP_TEXT.md (Section: "Output Format")

When run without arguments, display usage examples showing the three capture modes: by title, by PID, and by window ID.

## $REQ_HELP_002: Display Output Path Instructions
**Source:** ./readme/HELP_TEXT.md (Section: "Output Format")

When run without arguments, display instruction text explaining output path behavior: explicit .png file paths, directory paths with auto-generated timestamped filenames, and omitted paths defaulting to current directory.

## $REQ_HELP_003: Display Window List Header
**Source:** ./readme/HELP_TEXT.md (Section: "Output Format")

When run without arguments, display header text "Currently open windows (id,pid,title):" before the window list.

## $REQ_HELP_004: List Open Windows
**Source:** ./readme/HELP_TEXT.md (Section: "Field Descriptions")

When run without arguments, display one line per currently open window with format: `<window-id>\t<pid>\t"window title"` where fields are separated by tab characters.

## $REQ_HELP_005: Window ID Format
**Source:** ./readme/HELP_TEXT.md (Section: "Window ID Format")

Window IDs are alphanumeric hexadecimal values without 0x prefix.

## $REQ_HELP_006: Process ID Format
**Source:** ./readme/HELP_TEXT.md (Section: "Process IDs")

Process IDs are numeric values that may be shared by multiple windows from the same application.

## $REQ_HELP_007: Window Title Quoting
**Source:** ./readme/HELP_TEXT.md (Section: "Field Descriptions")

Window titles are displayed with double quotes in the window list.

## $REQ_HELP_008: Exit Success
**Source:** ./readme/HELP_TEXT.md (Section: "Exit Code")

Help mode exits with status code 0.
