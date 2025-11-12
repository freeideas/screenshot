# Help Mode Flow

**Source:** ./README.md

Run screenshot.exe without arguments to display usage information and list of currently open windows.

## $REQ_HELP_001: Display Usage on No Arguments
**Source:** ./README.md (Section: "Help Mode")

When screenshot.exe is run without arguments, it must print usage information.

## $REQ_HELP_002: List Currently Open Windows
**Source:** ./README.md (Section: "Help Mode")

When screenshot.exe is run without arguments, it must print a list of all currently open windows.

## $REQ_HELP_003: Window List Format with PID
**Source:** ./README.md (Section: "Help Mode")

Each line in the window list must show an alphanumeric window ID, followed by a tab character, followed by the numeric process ID, followed by a tab character, followed by the quoted window title.

Format: `<window-id>\t<pid>\t"window title"`

## $REQ_HELP_004: Tab-Separated Fields
**Source:** ./README.md (Section: "Help Mode")

Fields in the window list must be separated by tab characters (`\t`).
