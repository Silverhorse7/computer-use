<#
Example 05: Native PowerShell Automation (Zero External Dependencies)
#>

$modulePath = Join-Path $PSScriptRoot "..\powershell\ComputerUse.psd1"
Import-Module $modulePath -Force

Write-Host "=== 1. Capture Screen ===" -ForegroundColor Cyan
Invoke-CUCapture -Path "$PSScriptRoot\ps_screen.png"

Write-Host "=== 2. Scan Form Fields ===" -ForegroundColor Cyan
Invoke-CUBatchScan -ImagePath "$PSScriptRoot\ps_screen.png"

Write-Host "=== 3. DOM Injection Click ===" -ForegroundColor Cyan
Invoke-CUDOMClick -ButtonText "continue"

Write-Host "PowerShell Native Automation Complete!" -ForegroundColor Green
