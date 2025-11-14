using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

class Program
{
    [DllImport("user32.dll")]
    private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    private static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    private static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    private class WindowInfo
    {
        public IntPtr Handle { get; set; }
        public string Title { get; set; } = "";
        public uint ProcessId { get; set; }
    }

    static int Main(string[] args)
    {
        // Set console output encoding to UTF-8 for proper Unicode support
        Console.OutputEncoding = Encoding.UTF8;

        var windows = GetAllWindows();

        // No arguments: show help and window list
        if (args.Length == 0)
        {
            ShowHelp(windows);
            return 0;
        }

        // Parse arguments
        string mode = null;
        string value = null;
        string outputPath = null;

        for (int i = 0; i < args.Length; i++)
        {
            if (args[i] == "--title" && i + 1 < args.Length)  // $REQ_TITLE_001: Accept title argument
            {
                mode = "title";
                value = args[++i];
            }
            else if (args[i] == "--pid" && i + 1 < args.Length)  // $REQ_PID_001: Accept PID argument
            {
                mode = "pid";
                value = args[++i];
            }
            else if (args[i] == "--id" && i + 1 < args.Length)  // $REQ_ID_001: Accept window ID argument
            {
                mode = "id";
                value = args[++i];
            }
            else if (!args[i].StartsWith("--"))
            {
                outputPath = args[i];
            }
        }

        if (mode == null || value == null)
        {
            Console.Error.WriteLine("Error: Must specify --title, --pid, or --id");
            return 1;
        }

        // Find the window
        WindowInfo targetWindow = null;

        if (mode == "title")
        {
            // $REQ_TITLE_002: Find window by title
            // Try exact match first
            targetWindow = windows.FirstOrDefault(w => w.Title == value);

            // If no exact match, try matching with "Administrator: " prefix
            // (Windows prepends this to elevated process window titles)
            if (targetWindow == null)
            {
                targetWindow = windows.FirstOrDefault(w => w.Title == $"Administrator:  {value}");
            }

            // If still no match, try with single space (some Windows versions use one space)
            if (targetWindow == null)
            {
                targetWindow = windows.FirstOrDefault(w => w.Title == $"Administrator: {value}");
            }
        }
        else if (mode == "pid")
        {
            if (uint.TryParse(value, out uint pid))
            {
                targetWindow = windows.FirstOrDefault(w => w.ProcessId == pid);
            }
        }
        else if (mode == "id")
        {
            try
            {
                IntPtr handle = new IntPtr(Convert.ToInt64(value, 16));
                targetWindow = windows.FirstOrDefault(w => w.Handle == handle);
            }
            catch
            {
                // Invalid hex value
            }
        }

        if (targetWindow == null)
        {
            Console.Error.WriteLine($"Error: Window not found");
            return 1;
        }

        // Determine output path
        string finalPath = outputPath ?? ".";

        // Check if outputPath is a directory or needs timestamped filename
        if (string.IsNullOrEmpty(outputPath) || Directory.Exists(outputPath) || outputPath.EndsWith("/") || outputPath.EndsWith("\\"))
        {
            // $REQ_ID_004, $REQ_PID_004, $REQ_TITLE_004: Save to directory with timestamped filename
            // $REQ_ID_005, $REQ_PID_005, $REQ_TITLE_005: Save to current directory with timestamped filename
            // Generate timestamped filename
            string directory = string.IsNullOrEmpty(outputPath) ? "." : outputPath.TrimEnd('/', '\\');
            string timestamp = DateTime.Now.ToString("yyyy-MM-dd-HH-mm-ss-ffffff");
            finalPath = Path.Combine(directory, $"{timestamp}_screenshot.png");
        }
        // else: $REQ_ID_003, $REQ_PID_003, $REQ_TITLE_003: Save to explicit file path

        // Ensure directory exists
        string directory2 = Path.GetDirectoryName(finalPath);
        if (!string.IsNullOrEmpty(directory2) && directory2 != ".")
        {
            Directory.CreateDirectory(directory2);
        }

        // Capture screenshot
        if (CaptureWindow(targetWindow.Handle, finalPath))
        {
            Console.WriteLine($"Wrote {finalPath}");  // $REQ_ID_006, $REQ_PID_006, $REQ_TITLE_006: Output success message
            return 0;
        }
        else
        {
            Console.Error.WriteLine("Error: Failed to capture screenshot");
            return 1;
        }
    }

    private static List<WindowInfo> GetAllWindows()
    {
        var windows = new List<WindowInfo>();

        EnumWindows((hWnd, lParam) =>
        {
            if (!IsWindowVisible(hWnd))
                return true;

            int length = GetWindowTextLength(hWnd);
            if (length == 0)
                return true;

            var sb = new StringBuilder(length + 1);
            GetWindowText(hWnd, sb, sb.Capacity);
            string title = sb.ToString();

            if (string.IsNullOrWhiteSpace(title))
                return true;

            GetWindowThreadProcessId(hWnd, out uint processId);

            windows.Add(new WindowInfo
            {
                Handle = hWnd,
                Title = title,
                ProcessId = processId
            });

            return true;
        }, IntPtr.Zero);

        return windows;
    }

    private static void ShowHelp(List<WindowInfo> windows)
    {
        Console.WriteLine("Usage:");
        Console.WriteLine("  screenshot.exe --title \"window title\" [output.png|directory|]");
        Console.WriteLine("  screenshot.exe --pid <process-id> [output.png|directory|]");
        Console.WriteLine("  screenshot.exe --id <window-id> [output.png|directory|]");
        Console.WriteLine();
        Console.WriteLine("Output path is optional:");
        Console.WriteLine("  - Specify .png file: saves to that exact location");
        Console.WriteLine("  - Specify directory: saves with timestamped filename (YYYY-MM-DD-HH-MM-SS-microseconds_screenshot.png)");
        Console.WriteLine("  - Omit output: saves to current directory with timestamped filename");
        Console.WriteLine();
        Console.WriteLine("Run without arguments to see list of windows with IDs and PIDs.");
        Console.WriteLine();
        Console.WriteLine("Currently open windows (id,pid,title):");

        foreach (var window in windows)
        {
            string id = window.Handle.ToString("X");
            Console.WriteLine($"{id}\t{window.ProcessId}\t\"{window.Title}\"");
        }
    }

    private static bool CaptureWindow(IntPtr hWnd, string filename)
    {
        // $REQ_ID_002, $REQ_PID_002, $REQ_TITLE_002: Capture window by ID/PID/Title
        // $REQ_ID_008, $REQ_PID_008, $REQ_TITLE_008: Capture full window with decorations
        try
        {
            // Get window dimensions including decorations
            GetWindowRect(hWnd, out RECT rect);
            int width = rect.Right - rect.Left;
            int height = rect.Bottom - rect.Top;

            if (width <= 0 || height <= 0)
                return false;

            // Create a bitmap with window dimensions
            using (Bitmap bitmap = new Bitmap(width, height))
            {
                using (Graphics graphics = Graphics.FromImage(bitmap))
                {
                    // Capture the screen region where the window is located
                    // This captures the full window including title bar and decorations
                    graphics.CopyFromScreen(rect.Left, rect.Top, 0, 0, new Size(width, height), CopyPixelOperation.SourceCopy);
                }

                // Save as PNG
                bitmap.Save(filename, ImageFormat.Png);  // $REQ_ID_007, $REQ_PID_007, $REQ_TITLE_007: PNG format
            }

            return true;
        }
        catch
        {
            return false;
        }
    }
}
