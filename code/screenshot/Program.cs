using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;

namespace Screenshot;

internal static class Program
{
    private static int Main(string[] args)
    {
        if (args.Length == 0)
        {
            PrintUsage();
            ListWindows();
            return 0;
        }

        try
        {
            return RunWithArgs(args);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Error: {ex.Message}");
            return 1;
        }
    }

    private static int RunWithArgs(string[] args)
    {
        // Expect: one of --title/--pid/--id plus value, then output path
        if (args.Length < 3)
        {
            Console.Error.WriteLine("Invalid arguments. Expected a selection flag, its value, and an output path.");
            PrintUsage();
            return 2;
        }

        string flag = args[0];
        string value = args[1];
        string output = args[2];

        // If output is a directory, generate a timestamped filename
        if (System.IO.Directory.Exists(output))
        {
            var now = DateTime.Now;
            string timestamp = $"{now:yyyy-MM-dd-HH-mm-ss}-{now:ffffff}";
            string filename = $"{timestamp}_screenshot.png";
            output = System.IO.Path.Combine(output, filename);
        }

        IntPtr? hwnd = flag switch
        {
            "--title" => FindByTitle(value),
            "--pid" => int.TryParse(value, out var pid) ? FindByPid(pid) : null,
            "--id" => ParseHandle(value),
            _ => null
        };

        if (hwnd is null || hwnd == IntPtr.Zero)
        {
            Console.Error.WriteLine("Could not locate the requested window.");
            return 3;
        }

        // Best-effort: restore and foreground the window to improve capture reliability
        TryPrepareWindow(hwnd.Value);

        CaptureWindowToFile(hwnd.Value, output);
        return 0;
    }

    private static void PrintUsage()
    {
        Console.WriteLine("Usage:");
        Console.WriteLine("  screenshot.exe --title \"window title\" output.png");
        Console.WriteLine("  screenshot.exe --pid <process-id> output.png");
        Console.WriteLine("  screenshot.exe --id <window-id> output.png");
        Console.WriteLine();
        Console.WriteLine("Run without arguments to see list of windows with IDs and PIDs.");
        Console.WriteLine();
        Console.WriteLine("Currently open windows (id,pid,title):");
    }

    private static void ListWindows()
    {
        var list = new List<WindowInfo>(EnumerateWindows());
        list.Sort((a, b) => string.Compare(a.Title, b.Title, StringComparison.OrdinalIgnoreCase));
        foreach (var w in list)
        {
            Console.WriteLine($"{w.Id}\t{w.Pid}\t\"{w.Title}\"");
        }
    }

    private static IntPtr? FindByTitle(string title)
    {
        foreach (var w in EnumerateWindows())
        {
            if (string.Equals(w.Title, title, StringComparison.OrdinalIgnoreCase))
                return w.Handle;
        }
        return null;
    }

    private static IntPtr? FindByPid(int pid)
    {
        foreach (var w in EnumerateWindows())
        {
            if (w.Pid == pid)
                return w.Handle;
        }
        return null;
    }

    private static IntPtr? ParseHandle(string id)
    {
        // Expect hex string
        try
        {
            if (id.StartsWith("0x", StringComparison.OrdinalIgnoreCase))
                id = id[2..];
            if (ulong.TryParse(id, System.Globalization.NumberStyles.HexNumber, null, out var val))
                return new IntPtr(unchecked((long)val));
        }
        catch
        {
            // ignore
        }
        return null;
    }

    private static IEnumerable<WindowInfo> EnumerateWindows()
    {
        var list = new List<WindowInfo>();
        EnumWindows((hWnd, lParam) =>
        {
            if (!IsWindowVisible(hWnd)) return true;

            var sb = new StringBuilder(512);
            GetWindowText(hWnd, sb, sb.Capacity);
            var title = sb.ToString();
            if (string.IsNullOrWhiteSpace(title)) return true;

            _ = GetWindowThreadProcessId(hWnd, out uint pid);

            // Format handle as hex uppercase without 0x
            string id = ((ulong)(nint)hWnd).ToString("X");

            list.Add(new WindowInfo(hWnd, (int)pid, title, id));
            return true;
        }, IntPtr.Zero);
        return list;
    }

    private static void CaptureWindowToFile(IntPtr hWnd, string outputPath)
    {
        if (!TryGetWindowBounds(hWnd, out RECT rect))
            throw new InvalidOperationException("Failed to get window rectangle.");

        int width = rect.Right - rect.Left;
        int height = rect.Bottom - rect.Top;
        if (width <= 0 || height <= 0)
            throw new InvalidOperationException("Window has invalid size.");

        using var bmp = new Bitmap(width, height, PixelFormat.Format32bppArgb);
        using var g = Graphics.FromImage(bmp);
        IntPtr hdcDest = g.GetHdc();
        try
        {
            bool ok = false;

            // Try PrintWindow with full content flag first (PW_RENDERFULLCONTENT = 0x00000002)
            ok = PrintWindow(hWnd, hdcDest, 0x00000002);

            if (!ok)
            {
                // Retry without the flag as a fallback
                ok = PrintWindow(hWnd, hdcDest, 0);
            }

            if (!ok)
            {
                // Fallback: BitBlt from screen
                IntPtr hdcSrc = GetWindowDC(hWnd);
                if (hdcSrc != IntPtr.Zero)
                {
                    try
                    {
                        ok = BitBlt(hdcDest, 0, 0, width, height, hdcSrc, 0, 0, SRCCOPY);
                    }
                    finally
                    {
                        ReleaseDC(hWnd, hdcSrc);
                    }
                }
            }

            if (!ok)
                throw new InvalidOperationException("Failed to capture window.");
        }
        finally
        {
            g.ReleaseHdc(hdcDest);
        }

        // Ensure directory exists
        var dir = System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(outputPath));
        if (!string.IsNullOrEmpty(dir) && !System.IO.Directory.Exists(dir))
        {
            System.IO.Directory.CreateDirectory(dir!);
        }

        bmp.Save(outputPath, ImageFormat.Png);
    }

    private record struct WindowInfo(IntPtr Handle, int Pid, string Title, string Id);

    // Win32 interop
    private const int SRCCOPY = 0x00CC0020;

    private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    private static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    private static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);

    [DllImport("user32.dll")]
    private static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    private static extern IntPtr GetWindowDC(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

    [DllImport("user32.dll")]
    private static extern bool PrintWindow(IntPtr hwnd, IntPtr hdcBlt, uint nFlags);

    [DllImport("gdi32.dll")]
    private static extern bool BitBlt(IntPtr hdcDest, int nXDest, int nYDest, int nWidth, int nHeight,
        IntPtr hdcSrc, int nXSrc, int nYSrc, int dwRop);

    [StructLayout(LayoutKind.Sequential)]
    private struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    // DWM/Window helpers
    [DllImport("dwmapi.dll")]
    private static extern int DwmGetWindowAttribute(IntPtr hwnd, int dwAttribute, out RECT pvAttribute, int cbAttribute);

    [DllImport("user32.dll")]
    private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    private static extern bool SetForegroundWindow(IntPtr hWnd);

    private static void TryPrepareWindow(IntPtr hWnd)
    {
        const int SW_RESTORE = 9;
        try { ShowWindow(hWnd, SW_RESTORE); } catch { }
        try { SetForegroundWindow(hWnd); } catch { }
        // Small delay to allow redraw after bringing to foreground
        Thread.Sleep(100);
    }

    private static bool TryGetWindowBounds(IntPtr hWnd, out RECT rect)
    {
        // DWMWA_EXTENDED_FRAME_BOUNDS = 9
        const int DWMWA_EXTENDED_FRAME_BOUNDS = 9;
        try
        {
            if (DwmGetWindowAttribute(hWnd, DWMWA_EXTENDED_FRAME_BOUNDS, out rect, Marshal.SizeOf<RECT>()) == 0)
            {
                return true;
            }
        }
        catch { }

        return GetWindowRect(hWnd, out rect);
    }
}
