param(
    [string]$ImagePath,
    [string]$Action = "scan", # scan or fill
    [int]$ScanXStart = 1200,
    [int]$ScanXEnd = 1600,
    [int]$OptionOffset = 42,
    [int]$DelayMs = 180
)

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

$cuEngine = Join-Path $PSScriptRoot "CU_Engine.ps1"

if (-not (Test-Path $ImagePath)) {
    # If no image provided, capture current screen
    $ImagePath = Join-Path $PSScriptRoot "temp_batch.png"
    & $cuEngine -Action capture -Path $ImagePath | Out-Null
}

$sw = [System.Diagnostics.Stopwatch]::StartNew()
$img = [System.Drawing.Bitmap]::FromFile($ImagePath)

$borders = New-Object System.Collections.Generic.List[int]
for ($y = 250; $y -lt $img.Height - 100; $y++) {
    $match = 0
    for ($x = $ScanXStart; $x -lt $ScanXEnd; $x += 2) {
        $c = $img.GetPixel($x, $y)
        if ($c.R -gt 100 -and $c.R -lt 215 -and [Math]::Abs($c.R - $c.G) -le 6 -and [Math]::Abs($c.G - $c.B) -le 6) {
            $match++
        }
    }
    if ($match -gt 100) {
        $borders.Add($y)
    }
}

$boxes = New-Object System.Collections.Generic.List[PSCustomObject]
for ($i = 0; $i -lt $borders.Count; $i++) {
    $top = $borders[$i]
    for ($j = $i + 1; $j -lt $borders.Count; $j++) {
        $bot = $borders[$j]
        if ($bot - $top -ge 32 -and $bot - $top -le 52) {
            $center = [int](($top + $bot) / 2)
            $boxes.Add([PSCustomObject]@{
                Top = $top
                Bottom = $bot
                CenterY = $center
                CenterX = [int](($ScanXStart + $ScanXEnd) / 2)
            })
            $i = $j
            break
        }
    }
}

$img.Dispose()
$detectTime = $sw.ElapsedMilliseconds
Write-Output "=== [BATCH VISION] Detected $($boxes.Count) fields in $detectTime ms ==="

if ($Action -eq "fill" -and $boxes.Count -gt 0) {
    $tFillStart = $sw.ElapsedMilliseconds
    foreach ($box in $boxes) {
        # Click dropdown to open
        & $cuEngine -Action click -X $box.CenterX -Y $box.CenterY | Out-Null
        Start-Sleep -Milliseconds $DelayMs
        # Click option offset
        & $cuEngine -Action click -X $box.CenterX -Y ($box.CenterY + $OptionOffset) | Out-Null
        Start-Sleep -Milliseconds $DelayMs
    }
    $totalTime = $sw.ElapsedMilliseconds
    Write-Output "=== [BATCH FILL] Filled $($boxes.Count) fields in $(($totalTime - $tFillStart)/1000.0) seconds ==="
}

$boxes | Format-Table
