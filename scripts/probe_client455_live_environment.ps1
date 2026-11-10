[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$rfWorkspace=Split-Path -Parent $PSScriptRoot
$rfPaths=Get-Content -Raw -LiteralPath (Join-Path $rfWorkspace 'config/paths.json') | ConvertFrom-Json
$rfServerRoot=[IO.Path]::GetFullPath($rfPaths.server_bundle)
$rfClientRoot=[IO.Path]::GetFullPath($rfPaths.client_455)
function Get-RfPublicFile([string]$File) {
    $rfFileInfo=Get-Item -LiteralPath $File
    $rfBytes=[IO.File]::ReadAllBytes($File)
    $rfPeOffset=[BitConverter]::ToInt32($rfBytes,0x3c)
    $rfMachine=[BitConverter]::ToUInt16($rfBytes,$rfPeOffset+4)
    [ordered]@{file=$rfFileInfo.FullName;bytes=$rfFileInfo.Length;sha256=(Get-FileHash -LiteralPath $File -Algorithm SHA256).Hash.ToLowerInvariant();architecture=$(if($rfMachine -eq 0x14c){'x86'}elseif($rfMachine -eq 0x8664){'x64'}else{'unknown'})}
}
$rfListeners=@(Get-NetTCPConnection -State Listen | Where-Object {$_.LocalPort -in @(27830,27831,8080)})
$rfEndpoints=@(foreach($rfSocket in $rfListeners) {
    $rfProcess=Get-CimInstance Win32_Process -Filter "ProcessId=$($rfSocket.OwningProcess)"
    [ordered]@{address=$rfSocket.LocalAddress;port=$rfSocket.LocalPort;pid=$rfSocket.OwningProcess;executable=$rfProcess.ExecutablePath;path_matches_reference=$rfProcess.ExecutablePath.StartsWith($rfServerRoot+'\',[StringComparison]::OrdinalIgnoreCase)}
})
$rfClient=Get-RfPublicFile (Join-Path $rfClientRoot 'RF_Online.bin')
$rfLauncher=Get-RfPublicFile (Join-Path $rfClientRoot 'rflauncher.exe')
$rfBundledLauncher=Get-RfPublicFile (Join-Path $rfServerRoot 'client/rflauncher.exe')
$rfPins=Get-Content -Raw -LiteralPath (Join-Path $rfWorkspace 'config/client-target.json') | ConvertFrom-Json
$rfReport=[ordered]@{
    scope='Read-only live test environment;GoMMO behavior is not a substitute for pinned455client evidence'
    time_utc=[DateTime]::UtcNow.ToString('o')
    server_reference=$rfServerRoot
    endpoints=$rfEndpoints
    all_expected_ports_listening=@(27830,27831,8080 | Where-Object {$_ -notin $rfListeners.LocalPort}).Count -eq 0
    client=$rfClient
    client_matches_primary_pin=$rfClient.sha256 -eq $rfPins.behavior_reference.sha256
    launcher=$rfLauncher
    launcher_matches_server_bundle=$rfLauncher.sha256 -eq $rfBundledLauncher.sha256
    server_binaries=@((Get-RfPublicFile (Join-Path $rfServerRoot 'server/windows/gameserver.exe')),(Get-RfPublicFile (Join-Path $rfServerRoot 'server/windows/webserver.exe')))
    user_confirmation='User reports original client successfully entered this server world on2026-11-10;not an agent-observed game frame'
    script_sha256=(Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLowerInvariant()
    server_files_modified=$false
    credentials_or_packets_recorded=$false
}
$rfReport | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $rfWorkspace 'inventory/client455-live-server.json') -Encoding utf8
[pscustomobject]@{ports_available=$rfReport.all_expected_ports_listening;process_paths_match=@($rfEndpoints | Where-Object {-not $_.path_matches_reference}).Count -eq 0;client_pin_match=$rfReport.client_matches_primary_pin;launcher_match=$rfReport.launcher_matches_server_bundle;server_files_modified=$false} | ConvertTo-Json -Compress
