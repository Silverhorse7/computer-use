param(
    [string]$Action,      # click_button, select_radio, fill_input, raw
    [string]$TargetText,  # text to match
    [string]$Value = "",  # input value
    [string]$RawJs = ""
)

Add-Type -AssemblyName System.Windows.Forms

$cuEngine = Join-Path $PSScriptRoot "CU_Engine.ps1"

function Get-HelperJs {
    return @"
function triggerEvents(el, val = null) {
    if (!el) return false;
    ['mouseenter', 'mouseover', 'mousedown', 'mouseup', 'click'].forEach(evt => {
        el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
    });
    if (val !== null && ('value' in el)) {
        el.value = val;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        el.dispatchEvent(new Event('change', { bubbles: true }));
    }
    return true;
}
"@
}

$jsPayload = ""

if ($Action -eq "click_button") {
    $clean = $TargetText.ToLower().Trim()
    $jsPayload = @"
(() => {
    $(Get-HelperJs)
    const target = '$clean';
    const btns = Array.from(document.querySelectorAll('button, input[type="submit"], input[type="button"], a[role="button"], div[role="button"]'))
        .filter(b => b.textContent.trim().toLowerCase().includes(target) && !b.disabled);
    if (btns.length > 0) {
        triggerEvents(btns[0]);
        console.log("=== [DOM] Clicked button matching: " + target + " ===");
    }
})();
"@
} elseif ($Action -eq "select_radio") {
    $clean = $TargetText.ToLower().Trim()
    $jsPayload = @"
(() => {
    $(Get-HelperJs)
    const target = '$clean';
    const labels = Array.from(document.querySelectorAll('label, span, div'))
        .filter(l => l.textContent && l.textContent.toLowerCase().includes(target));
    if (labels.length > 0) {
        let el = labels[0];
        let radio = el.closest('label') || el.parentElement;
        let input = (radio ? radio.querySelector('input[type="radio"]') : null) || el.querySelector('input') || el;
        if (input && input.tagName === 'INPUT') {
            input.checked = true;
            triggerEvents(input);
        } else {
            triggerEvents(el);
        }
        console.log("=== [DOM] Checked radio matching: " + target + " ===");
    }
})();
"@
} elseif ($Action -eq "fill_input") {
    $clean = $TargetText.ToLower().Trim()
    $val = $Value.Replace("'", "\'")
    $jsPayload = @"
(() => {
    $(Get-HelperJs)
    const target = '$clean';
    const val = '$val';
    let input = Array.from(document.querySelectorAll('input, textarea'))
        .find(i => (i.placeholder && i.placeholder.toLowerCase().includes(target)) ||
                   (i.name && i.name.toLowerCase().includes(target)) ||
                   (i.id && i.id.toLowerCase().includes(target)));
    if (!input) {
        const labels = Array.from(document.querySelectorAll('label'))
            .filter(l => l.textContent.toLowerCase().includes(target));
        if (labels.length > 0) {
            input = labels[0].querySelector('input, textarea') || document.getElementById(labels[0].htmlFor);
        }
    }
    if (input) {
        triggerEvents(input, val);
        console.log("=== [DOM] Filled input: " + target + " ===");
    }
})();
"@
} elseif ($Action -eq "raw") {
    $jsPayload = $RawJs
}

if ($jsPayload) {
    # 1. Open DevTools Console
    & $cuEngine -Action keys -Keys '^+j' | Out-Null
    Start-Sleep -Milliseconds 1000

    # 2. Copy payload to clipboard and paste
    [System.Windows.Forms.Clipboard]::SetText($jsPayload)
    Start-Sleep -Milliseconds 150
    & $cuEngine -Action keys -Keys '^v{ENTER}' | Out-Null
    Start-Sleep -Milliseconds 800

    # 3. Close DevTools to prevent layout shift
    & $cuEngine -Action keys -Keys '{F12}' | Out-Null
    Start-Sleep -Milliseconds 400
    Write-Output "=== [DOM] Injected payload successfully ==="
}
