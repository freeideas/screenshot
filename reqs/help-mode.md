# Help Mode Flow

**Source:** ./README.md

Run screenshot.exe without arguments to display usage information and list of currently open windows.

## $REQ_HELP_001: Display Usage on Insufficient Arguments
**Source:** ./README.md (Section: "Help Mode")

When screenshot.exe is run without exactly two command-line arguments, it must print usage information.

## $REQ_HELP_002: List Currently Open Windows
**Source:** ./README.md (Section: "Help Mode")

When screenshot.exe is run without exactly two command-line arguments, it must print a list of all currently open windows.

## $REQ_HELP_003: Window List Format
**Source:** ./README.md (Section: "Help Mode")

Each line in the window list must show an alphanumeric window ID, followed by a space, followed by the quoted window title.

Format: `<id> "window title"`
