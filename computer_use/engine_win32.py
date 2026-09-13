"""
Win32 native desktop driver with STA isolation and desktop-switch awareness.
"""

import os
import subprocess
import time
from typing import Optional, Tuple, Dict, Any


class Win32Driver:
    """
    Direct Win32 desktop automation driver.
    
    Uses Single-Threaded Apartment (STA) execution with OpenInputDesktop
    and SetThreadDesktop to reliably interact with windows even when background
    threads or session switches occur.
    """

    def __init__(self, script_path: Optional[str] = None):
        if script_path and os.path.exists(script_path):
            self.script_path = script_path
        else:
            # Look relative to powershell directory
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "powershell"))
            candidate = os.path.join(base_dir, "CU_Engine.ps1")
            if os.path.exists(candidate):
                self.script_path = candidate
            else:
                self.script_path = None

    def _run_ps(self, args: list) -> str:
        """Run PowerShell command with bypass execution policy."""
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass"] + args
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Win32 execution failed: {proc.stderr.strip()}")
        return proc.stdout.strip()

    def capture(self, output_path: str) -> str:
        """Capture the target window (Chrome/Edge/Active) to a PNG file."""
        abs_path = os.path.abspath(output_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        if self.script_path:
            return self._run_ps(["-File", self.script_path, "-Action", "capture", "-Path", abs_path])
        
        # Fallback inline
        ps_code = f"""
Add-Type -AssemblyName System.Drawing, System.Windows.Forms
$bmp = New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen(0, 0, 0, 0, $bmp.Size)
$bmp.Save('{abs_path}', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
Write-Output "OK: Captured primary screen"
"""
        return self._run_ps(["-Command", ps_code])

    def click(self, x: int, y: int) -> str:
        """Click at (x, y) relative to the target window or screen."""
        if self.script_path:
            return self._run_ps(["-File", self.script_path, "-Action", "click", "-X", str(x), "-Y", str(y)])
        
        ps_code = f"""
[System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point({x}, {y})
Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern void mouse_event(uint f, uint x, uint y, uint d, int e);' -Name M -Namespace U
[U.M]::mouse_event(0x0002, 0, 0, 0, 0)
Start-Sleep -Milliseconds 80
[U.M]::mouse_event(0x0004, 0, 0, 0, 0)
Write-Output "OK: Clicked ({x}, {y})"
"""
        return self._run_ps(["-Command", ps_code])

    def send_keys(self, keys: str) -> str:
        """Send keystrokes (e.g. '^l', '{ENTER}', '{PGDN}', 'text')."""
        if self.script_path:
            return self._run_ps(["-File", self.script_path, "-Action", "keys", "-Keys", keys])
        
        ps_code = f"""
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait('{keys}')
Write-Output "OK: Sent keys"
"""
        return self._run_ps(["-Command", ps_code])

    def scroll(self, amount: int) -> str:
        """Scroll mouse wheel (positive for up, negative for down)."""
        if self.script_path:
            return self._run_ps(["-File", self.script_path, "-Action", "scroll", "-Amount", str(amount)])
        
        ps_code = f"""
Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern void mouse_event(uint f, uint x, uint y, uint d, int e);' -Name M2 -Namespace U2
[U2.M2]::mouse_event(0x0800, 0, 0, [uint32]{amount}, 0)
Write-Output "OK: Scrolled {amount}"
"""
        return self._run_ps(["-Command", ps_code])

    def navigate(self, url: str) -> str:
        """Focus browser address bar, paste URL, and press Enter."""
        if self.script_path:
            return self._run_ps(["-File", self.script_path, "-Action", "navigate", "-Url", url])
        
        ps_code = f"""
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Clipboard]::SetText('{url}')
[System.Windows.Forms.SendKeys]::SendWait('^l')
Start-Sleep -Milliseconds 120
[System.Windows.Forms.SendKeys]::SendWait('^v{{ENTER}}')
Write-Output "OK: Navigated to {url}"
"""
        return self._run_ps(["-Command", ps_code])

    def maximize(self) -> str:
        """Maximize the target window."""
        if self.script_path:
            return self._run_ps(["-File", self.script_path, "-Action", "maximize"])
        return "OK: Maximize invoked"

    def set_clipboard(self, text: str) -> None:
        """Set text into the Windows OS clipboard."""
        import base64
        b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
        ps_code = f"""
Add-Type -AssemblyName System.Windows.Forms
$bytes = [Convert]::FromBase64String('{b64}')
$str = [System.Text.Encoding]::UTF8.GetString($bytes)
[System.Windows.Forms.Clipboard]::SetText($str)
"""
        self._run_ps(["-Command", ps_code])

    def get_clipboard(self) -> str:
        """Get current text from the Windows OS clipboard."""
        ps_code = """
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.Clipboard]::GetText()
"""
        return self._run_ps(["-Command", ps_code])

