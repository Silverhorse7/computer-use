@{
    RootModule = 'ComputerUse.psm1'
    ModuleVersion = '0.1.0'
    GUID = 'a1e948c2-4a7b-4d43-9821-6c2e39fb7e01'
    Author = 'Yosef Madboly'
    CompanyName = 'Open Source'
    Copyright = '(c) 2026 Yosef Madboly. All rights reserved.'
    Description = 'High-Performance Hybrid Computer Use & Browser Automation Engine for Windows.'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Invoke-CUCapture',
        'Invoke-CUClick',
        'Invoke-CUSendKeys',
        'Invoke-CUNavigate',
        'Invoke-CUScroll',
        'Invoke-CUDOMClick',
        'Invoke-CUDOMRadio',
        'Invoke-CUBatchScan',
        'Invoke-CUTwitterExtract',
        'Invoke-CUTwitterInteract'
    )
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
