<#
.SYNOPSIS
    ComputerUse PowerShell Module for High-Speed Hybrid Automation.
.DESCRIPTION
    Combines DevTools DOM Injection (<20ms), In-Memory Batched Pixel Detection (~150ms),
    and Native Win32 STA OS Primitives.
#>

$EngineScript = Join-Path $PSScriptRoot "CU_Engine.ps1"
$BatchScript = Join-Path $PSScriptRoot "BatchEngine.ps1"
$DOMScript = Join-Path $PSScriptRoot "DOMInjection.ps1"

function Invoke-CUCapture {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )
    & $EngineScript -Action capture -Path $Path
}

function Invoke-CUClick {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [int]$X,
        [Parameter(Mandatory=$true)]
        [int]$Y
    )
    & $EngineScript -Action click -X $X -Y $Y
}

function Invoke-CUSendKeys {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Keys
    )
    & $EngineScript -Action keys -Keys $Keys
}

function Invoke-CUNavigate {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Url
    )
    & $EngineScript -Action navigate -Url $Url
}

function Invoke-CUScroll {
    [CmdletBinding()]
    param(
        [int]$Amount = -500
    )
    & $EngineScript -Action scroll -Amount $Amount
}

function Invoke-CUDOMClick {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ButtonText
    )
    & $DOMScript -Action click_button -TargetText $ButtonText
}

function Invoke-CUDOMRadio {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$LabelText
    )
    & $DOMScript -Action select_radio -TargetText $LabelText
}

function Invoke-CUBatchScan {
    [CmdletBinding()]
    param(
        [string]$ImagePath = ""
    )
    & $BatchScript -Action scan -ImagePath $ImagePath
}

Export-ModuleMember -Function Invoke-CUCapture, Invoke-CUClick, Invoke-CUSendKeys, Invoke-CUNavigate, Invoke-CUScroll, Invoke-CUDOMClick, Invoke-CUDOMRadio, Invoke-CUBatchScan
