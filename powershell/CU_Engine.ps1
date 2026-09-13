param(
    [string]$Action,
    [string]$Path,
    [int]$X = 0,
    [int]$Y = 0,
    [string]$Keys = "",
    [int]$Amount = 0,
    [string]$Url = ""
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$code = @"
using System;
using System.Text;
using System.Drawing;
using System.Drawing.Imaging;
using System.Threading;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Windows.Forms;

public class CU {
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder lpString, int nMaxCount);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern IntPtr OpenInputDesktop(uint dwFlags, bool fInherit, uint dwDesiredAccess);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetThreadDesktop(IntPtr hDesktop);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool CloseDesktop(IntPtr hDesktop);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, uint nFlags);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);

    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);

    private const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
    private const uint MOUSEEVENTF_LEFTUP = 0x0004;
    private const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
    private const uint MOUSEEVENTF_RIGHTUP = 0x0010;
    private const uint MOUSEEVENTF_WHEEL = 0x0800;

    [StructLayout(LayoutKind.Sequential)]
    public struct RECT {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    public static IntPtr FindChromeOnDesktop(out string title, out RECT rect) {
        IntPtr found = IntPtr.Zero;
        string foundTitle = "";
        RECT foundRect = new RECT();

        IntPtr best = IntPtr.Zero;
        string bestTitle = "";
        RECT bestRect = new RECT();

        EnumWindows((hWnd, lParam) => {
            if (IsWindowVisible(hWnd)) {
                StringBuilder sb = new StringBuilder(512);
                GetWindowText(hWnd, sb, 512);
                string t = sb.ToString().Trim();
                if (t.Contains("Google Chrome") || t.Contains("Chrome") || t.Contains("Edge")) {
                    if (t.Contains("Console") || t.Contains("Dashboard") || t.Contains("Portal") || t.Contains("App") || t.Contains("Manager")) {
                        best = hWnd;
                        bestTitle = t;
                        GetWindowRect(hWnd, out bestRect);
                        return false;
                    }
                    if (found == IntPtr.Zero) {
                        found = hWnd;
                        foundTitle = t;
                        GetWindowRect(hWnd, out foundRect);
                    }
                }
            }
            return true;
        }, IntPtr.Zero);

        if (best != IntPtr.Zero) {
            title = bestTitle;
            rect = bestRect;
            return best;
        }

        title = foundTitle;
        rect = foundRect;
        return found;
    }

    public static string Maximize() {
        string res = "";
        Thread t = new Thread(() => {
            IntPtr hDesk = OpenInputDesktop(0, false, 0x01FF);
            if (hDesk == IntPtr.Zero) { res = "Failed desktop open"; return; }
            SetThreadDesktop(hDesk);

            string title;
            RECT r;
            IntPtr hWnd = FindChromeOnDesktop(out title, out r);
            if (hWnd != IntPtr.Zero) {
                ShowWindow(hWnd, 3); // SW_MAXIMIZE
                SetForegroundWindow(hWnd);
                res = "Maximized: " + title;
            } else {
                res = "Window not found";
            }
            CloseDesktop(hDesk);
        });
        t.SetApartmentState(ApartmentState.STA);
        t.Start();
        t.Join();
        return res;
    }

    public static string Navigate(string url) {
        string res = "";
        Thread t = new Thread(() => {
            IntPtr hDesk = OpenInputDesktop(0, false, 0x01FF);
            if (hDesk == IntPtr.Zero) { res = "Failed to open input desktop"; return; }
            SetThreadDesktop(hDesk);

            string title;
            RECT r;
            IntPtr hWnd = FindChromeOnDesktop(out title, out r);
            if (hWnd == IntPtr.Zero) { res = "Window not found"; CloseDesktop(hDesk); return; }

            ShowWindow(hWnd, 3);
            SetForegroundWindow(hWnd);
            Thread.Sleep(200);

            Clipboard.SetText(url);
            Thread.Sleep(100);

            SendKeys.SendWait("^l");
            Thread.Sleep(150);

            SendKeys.SendWait("^v");
            Thread.Sleep(150);

            SendKeys.SendWait("{ENTER}");
            Thread.Sleep(500);

            res = "OK: Navigated to " + url;
            CloseDesktop(hDesk);
        });
        t.SetApartmentState(ApartmentState.STA);
        t.Start();
        t.Join();
        return res;
    }

    public static string Capture(string outputPath) {
        string status = "";
        Thread t = new Thread(() => {
            IntPtr hDesk = OpenInputDesktop(0, false, 0x01FF);
            if (hDesk == IntPtr.Zero) { status = "Error: OpenInputDesktop"; return; }
            SetThreadDesktop(hDesk);

            string title;
            RECT r;
            IntPtr hWnd = FindChromeOnDesktop(out title, out r);
            if (hWnd == IntPtr.Zero) { status = "Error: Window not found"; CloseDesktop(hDesk); return; }

            int width = r.Right - r.Left;
            int height = r.Bottom - r.Top;
            using (Bitmap bmp = new Bitmap(width, height)) {
                using (Graphics g = Graphics.FromImage(bmp)) {
                    IntPtr hdc = g.GetHdc();
                    bool ok = PrintWindow(hWnd, hdc, 2);
                    g.ReleaseHdc(hdc);
                    if (!ok) {
                        hdc = g.GetHdc();
                        PrintWindow(hWnd, hdc, 0);
                        g.ReleaseHdc(hdc);
                    }
                }
                bmp.Save(outputPath, ImageFormat.Png);
            }
            status = string.Format("OK: Captured '{0}' ({1}x{2})", title, width, height);
            CloseDesktop(hDesk);
        });
        t.SetApartmentState(ApartmentState.STA);
        t.Start();
        t.Join();
        return status;
    }

    public static string Click(int relX, int relY) {
        string status = "";
        Thread t = new Thread(() => {
            IntPtr hDesk = OpenInputDesktop(0, false, 0x01FF);
            if (hDesk == IntPtr.Zero) { status = "Error: OpenInputDesktop"; return; }
            SetThreadDesktop(hDesk);

            string title;
            RECT r;
            IntPtr hWnd = FindChromeOnDesktop(out title, out r);
            if (hWnd == IntPtr.Zero) { status = "Error: Window not found"; CloseDesktop(hDesk); return; }

            SetForegroundWindow(hWnd);
            Thread.Sleep(100);

            int absX = r.Left + relX;
            int absY = r.Top + relY;
            SetCursorPos(absX, absY);
            Thread.Sleep(100);
            mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
            Thread.Sleep(100);
            mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);

            status = string.Format("OK: Clicked ({0}, {1}) in '{2}'", relX, relY, title);
            CloseDesktop(hDesk);
        });
        t.SetApartmentState(ApartmentState.STA);
        t.Start();
        t.Join();
        return status;
    }

    public static string SendKeyString(string keys) {
        string status = "";
        Thread t = new Thread(() => {
            IntPtr hDesk = OpenInputDesktop(0, false, 0x01FF);
            if (hDesk == IntPtr.Zero) { status = "Error: OpenInputDesktop"; return; }
            SetThreadDesktop(hDesk);

            string title;
            RECT r;
            IntPtr hWnd = FindChromeOnDesktop(out title, out r);
            if (hWnd == IntPtr.Zero) { status = "Error: Window not found"; CloseDesktop(hDesk); return; }

            SetForegroundWindow(hWnd);
            Thread.Sleep(100);

            SendKeys.SendWait(keys);
            status = string.Format("OK: Sent keys '{0}' to '{1}'", keys, title);
            CloseDesktop(hDesk);
        });
        t.SetApartmentState(ApartmentState.STA);
        t.Start();
        t.Join();
        return status;
    }

    public static string Scroll(int amount) {
        string status = "";
        Thread t = new Thread(() => {
            IntPtr hDesk = OpenInputDesktop(0, false, 0x01FF);
            if (hDesk == IntPtr.Zero) { status = "Error: OpenInputDesktop"; return; }
            SetThreadDesktop(hDesk);

            string title;
            RECT r;
            IntPtr hWnd = FindChromeOnDesktop(out title, out r);
            if (hWnd == IntPtr.Zero) { status = "Error: Window not found"; CloseDesktop(hDesk); return; }

            SetForegroundWindow(hWnd);
            Thread.Sleep(100);

            mouse_event(MOUSEEVENTF_WHEEL, 0, 0, (uint)amount, 0);
            status = string.Format("OK: Scrolled {0} in '{1}'", amount, title);
            CloseDesktop(hDesk);
        });
        t.SetApartmentState(ApartmentState.STA);
        t.Start();
        t.Join();
        return status;
    }
}
"@

Add-Type -TypeDefinition $code -ReferencedAssemblies "System.Drawing.dll", "System.Windows.Forms.dll" -ErrorAction SilentlyContinue

if ($Action -eq "capture") {
    Write-Output ([CU]::Capture($Path))
} elseif ($Action -eq "click") {
    Write-Output ([CU]::Click($X, $Y))
} elseif ($Action -eq "keys") {
    Write-Output ([CU]::SendKeyString($Keys))
} elseif ($Action -eq "navigate") {
    Write-Output ([CU]::Navigate($Url))
} elseif ($Action -eq "maximize") {
    Write-Output ([CU]::Maximize())
} elseif ($Action -eq "scroll") {
    Write-Output ([CU]::Scroll($Amount))
}
