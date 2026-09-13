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
} elseif ($Action -eq "twitter_extract") {
    $count = if ($Value) { [int]$Value } else { 20 }
    $jsPayload = @"
(async () => {
    const targetCount = $count;
    const collected = new Map();
    let scrollAttempts = 0;
    const maxScrolls = 10;

    function harvest() {
        const articles = Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
        for (const article of articles) {
            const userEl = article.querySelector('[data-testid="User-Name"]');
            const textEl = article.querySelector('[data-testid="tweetText"]');
            const linkEl = article.querySelector('a[href*="/status/"]');
            const fullUserText = userEl ? userEl.innerText : '';
            const handleMatch = fullUserText.match(/@([A-Za-z0-9_]+)/);
            const handle = handleMatch ? handleMatch[0] : '';
            const author = fullUserText.split('\n')[0].trim();
            const text = textEl ? textEl.innerText.trim() : '';
            const tweetUrl = linkEl ? linkEl.href : '';
            const tweetIdMatch = tweetUrl.match(/status\/(\d+)/);
            const id = tweetIdMatch ? tweetIdMatch[1] : (handle + '_' + text.slice(0, 30));

            if (id && !collected.has(id) && (text.length > 0 || linkEl)) {
                const likeBtn = article.querySelector('button[data-testid="like"], button[data-testid="unlike"]');
                const retweetBtn = article.querySelector('button[data-testid="retweet"], button[data-testid="unretweet"]');
                const getCount = (btn) => {
                    if (!btn) return '0';
                    const t = btn.innerText.trim();
                    if (t) return t;
                    const label = btn.getAttribute('aria-label') || '';
                    const m = label.match(/([\d,\.]+[KkMm]?)/);
                    return m ? m[1] : '0';
                };
                collected.set(id, {
                    author: author,
                    handle: handle,
                    text: text,
                    likes: getCount(likeBtn),
                    reposts: getCount(retweetBtn)
                });
            }
        }
    }

    harvest();
    while (collected.size < targetCount && scrollAttempts < maxScrolls) {
        window.scrollBy(0, 800);
        await new Promise(r => setTimeout(r, 450));
        harvest();
        scrollAttempts++;
    }

    const results = Array.from(collected.values()).slice(0, targetCount);
    if (typeof copy === 'function') {
        copy(JSON.stringify(results, null, 2));
    }
    console.table(results);
    return results;
})();
"@
} elseif ($Action -eq "twitter_interact") {
    $q = $TargetText.ToLower().Trim()
    $act = if ($Value) { $Value.ToLower().Trim() } else { "like" }
    $jsPayload = @"
(() => {
    $(Get-HelperJs)
    const query = '$q';
    const action = '$act';
    const articles = Array.from(document.querySelectorAll('article[data-testid="tweet"]'));
    const match = articles.find(a => a.innerText.toLowerCase().includes(query));
    if (!match) {
        console.warn('[computer-use] Tweet not found: ' + query);
        return;
    }
    let btn = match.querySelector('button[data-testid="' + action + '"]') || match.querySelector('button[data-testid="like"]');
    if (btn) {
        triggerEvents(btn);
        console.log('[computer-use] Interacted with tweet (' + action + ')');
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
