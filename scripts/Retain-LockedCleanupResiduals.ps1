$ErrorActionPreference='Stop'
$workspaceRoot=[IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)).TrimEnd('\')
$resultPath=Join-Path $workspaceRoot 'inventory/workspace-cleanup-result-20261113.json'
$plan=Get-Content -LiteralPath (Join-Path $workspaceRoot 'inventory/workspace-cleanup-plan-20261113.json') -Raw | ConvertFrom-Json
$result=Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
if ($result.PSObject.Properties.Name -contains 'locked_residuals') {throw 'Residuals already separated; use Invoke-WorkspaceCleanup.ps1 -LockedResiduals'}
$pendingRoot=Join-Path $workspaceRoot 'work\cleanup-pending-fonts'
New-Item -ItemType Directory -Path $pendingRoot -Force | Out-Null
$residuals=@();$remaining=@()
foreach($failure in $result.failures) {
    $sourcePath=[IO.Path]::GetFullPath($failure.path).TrimEnd('\')
    if ($sourcePath -notin $plan.targets -or -not $sourcePath.StartsWith($workspaceRoot+'\work\m9\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected obsolete target' }
    $relative=$sourcePath.Substring(($workspaceRoot+'\work\m9\').Length)
    $destinationPath=[IO.Path]::GetFullPath((Join-Path $pendingRoot $relative))
    if (-not $destinationPath.StartsWith($pendingRoot+'\',[StringComparison]::OrdinalIgnoreCase)) {throw 'Unexpected destination'}
    try {
        if(Test-Path -LiteralPath $sourcePath) {
            if ((Resolve-Path -LiteralPath $sourcePath).Path.TrimEnd('\') -ne $sourcePath) {throw 'Resolved target differs'}
            $items=@(Get-ChildItem -LiteralPath $sourcePath -Force -Recurse)
            if ($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) {throw 'Unexpected reparse point'}
            $files=@($items | Where-Object {-not $_.PSIsContainer})
            if ($files | Where-Object {$_.Name -ne '010.TTF'}) {throw 'Residual contains more than locked fonts'}
            if (Test-Path -LiteralPath $destinationPath) {throw 'Destination already exists'}
            New-Item -ItemType Directory -Path (Split-Path -Parent $destinationPath) -Force | Out-Null
            Move-Item -LiteralPath $sourcePath -Destination $destinationPath
        }
        $fonts=@(Get-ChildItem -LiteralPath $destinationPath -File -Recurse)
        $residuals += [pscustomobject]@{original=$sourcePath;pending=$destinationPath;files=$fonts.Count;bytes=($fonts | Measure-Object Length -Sum).Sum}
    } catch {$remaining += [pscustomobject]@{path=$sourcePath;error=$_.Exception.Message}}
}
foreach ($row in $plan.preserved_files) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspaceRoot $row.file) -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) {throw 'Preserved file changed'}
}
$result.failures=$remaining
$result | Add-Member -NotePropertyName locked_residuals -NotePropertyValue $residuals -Force
$result.free_bytes_after=(Get-PSDrive -Name E).Free
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resultPath -Encoding utf8
[pscustomobject]@{pending_directories=$residuals.Count;remaining=$remaining;pending_files=($residuals | Measure-Object files -Sum).Sum;pending_bytes=($residuals | Measure-Object bytes -Sum).Sum;freed_GiB=($result.free_bytes_after-$result.free_bytes_before)/1GB} | ConvertTo-Json -Depth 4
if($remaining.Count){exit 1}
