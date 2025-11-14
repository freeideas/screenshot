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
    static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll")]
    static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    [DllImport("user32.dll")]
    static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);

    [StructLayout(LayoutKind.Sequential)]
    struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    class WindowInfo
    {
        public IntPtr Handle { get; set; }
        public string Title { get; set; }
        public uint ProcessId { get; set; }
        public string WindowId { get; set; }
    }

    static List<WindowInfo> GetAllWindows()
    {
        var windows = new List<WindowInfo>();

        EnumWindows((hWnd, lParam) =>
        {
            if (IsWindowVisible(hWnd))
            {
                int length = GetWindowTextLength(hWnd);
                if (length > 0)
                {
                    var sb = new StringBuilder(length + 1);
                    GetWindowText(hWnd, sb, sb.Capacity);
                    string title = sb.ToString();

                    uint processId;
                    GetWindowThreadProcessId(hWnd, out processId);

                    windows.Add(new WindowInfo
                    {
                        Handle = hWnd,
                        Title = title,
                        ProcessId = processId,
                        WindowId = hWnd.ToInt64().ToString("X")
                    });
                }
            }
            return true;
        }, IntPtr.Zero);

        return windows;
    }

    static void ShowHelp()
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

        var windows = GetAllWindows();
        foreach (var window in windows)
        {
            Console.WriteLine($"{window.WindowId}\t{window.ProcessId}\t\"{window.Title}\"");
        }
    }

    static string GenerateTimestampedFilename()
    {
        var now = DateTime.Now;
        return $"{now:yyyy-MM-dd-HH-mm-ss-ffffff}_screenshot.png";
    }

    static string DetermineOutputPath(string outputArg)
    {
        if (string.IsNullOrEmpty(outputArg))
        {
            // No output specified: use current directory with timestamped filename
            return Path.Combine(".", GenerateTimestampedFilename());
        }

        if (outputArg.EndsWith(".png", StringComparison.OrdinalIgnoreCase))
        {
            // Explicit .png file
            return outputArg;
        }

        // Assume it's a directory
        if (!Directory.Exists(outputArg))
        {
            Directory.CreateDirectory(outputArg);
        }
        return Path.Combine(outputArg, GenerateTimestampedFilename());
    }

    static bool CaptureWindow(IntPtr hWnd, string outputPath)
    {
        RECT rect;
        if (!GetWindowRect(hWnd, out rect))
        {
            return false;
        }

        int width = rect.Right - rect.Left;
        int height = rect.Bottom - rect.Top;

        if (width <= 0 || height <= 0)
        {
            return false;
        }

        using (Bitmap bitmap = new Bitmap(width, height, PixelFormat.Format32bppArgb))
        {
            using (Graphics graphics = Graphics.FromImage(bitmap))
            {
                IntPtr hdc = graphics.GetHdc();
                try
                {
                    PrintWindow(hWnd, hdc, 0);
                }
                finally
                {
                    graphics.ReleaseHdc(hdc);
                }
            }

            // Ensure output directory exists
            string directory = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            bitmap.Save(outputPath, ImageFormat.Png);
        }

        return true;
    }

    static int Main(string[] args)
    {
        if (args.Length == 0)
        {
            ShowHelp();
            return 0;
        }

        if (args.Length < 2)
        {
            Console.Error.WriteLine("Error: Missing required arguments");
            return 1;
        }

        string flag = args[0];
        string value = args[1];
        string outputArg = args.Length > 2 ? args[2] : "";

        var windows = GetAllWindows();
        WindowInfo targetWindow = null;

        if (flag == "--title")
        {
            targetWindow = windows.FirstOrDefault(w => w.Title == value);
        }
        else if (flag == "--pid")
        {
            if (uint.TryParse(value, out uint pid))
            {
                targetWindow = windows.FirstOrDefault(w => w.ProcessId == pid);
            }
            else
            {
                Console.Error.WriteLine($"Error: Invalid PID '{value}'");
                return 1;
            }
        }
        else if (flag == "--id")
        {
            targetWindow = windows.FirstOrDefault(w =>
                w.WindowId.Equals(value, StringComparison.OrdinalIgnoreCase));
        }
        else
        {
            Console.Error.WriteLine($"Error: Unknown flag '{flag}'");
            return 1;
        }

        if (targetWindow == null)
        {
            Console.Error.WriteLine($"Error: No window found matching {flag} {value}");
            return 1;
        }

        string outputPath = DetermineOutputPath(outputArg);

        if (!CaptureWindow(targetWindow.Handle, outputPath))
        {
            Console.Error.WriteLine("Error: Failed to capture window");
            return 1;
        }

        Console.WriteLine($"Wrote {outputPath}");
        return 0;
    }
}
