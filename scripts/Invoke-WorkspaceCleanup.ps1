param([string]$Plan = 'inventory/workspace-cleanup-plan-20261113.json', [switch]$LockedResiduals)
$ErrorActionPreference = 'Stop'
$workspaceRoot = [IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)).TrimEnd('\')
$planPath = Join-Path $workspaceRoot $Plan
$data = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json
if ([IO.Path]::GetFullPath($data.workspace).TrimEnd('\') -ne $workspaceRoot) { throw 'Workspace mismatch' }
if ($LockedResiduals) {
    $pendingRoot = Join-Path $workspaceRoot 'work\cleanup-pending-fonts'
    $resultPath = Join-Path $workspaceRoot 'inventory/workspace-cleanup-result-20261113.json'
    $result = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
    $remaining = @()
    foreach ($row in $result.locked_residuals) {
        $target = [IO.Path]::GetFullPath($row.pending).TrimEnd('\')
        if (-not $target.StartsWith($pendingRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Residual outside approved directory' }
        if (-not (Test-Path -LiteralPath $target)) { continue }
        if ((Resolve-Path -LiteralPath $target).Path.TrimEnd('\') -ne $target) { throw 'Residual path changed' }
        $items = @((Get-Item -LiteralPath $target -Force)) + @(Get-ChildItem -LiteralPath $target -Recurse -Force)
        if ($items | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }) { throw 'Residual reparse point rejected' }
        if ($items | Where-Object { -not $_.PSIsContainer -and $_.Name -ne '010.TTF' }) { throw 'New content in residual; preserve it' }
        Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction Continue 2>$null
        if (Test-Path -LiteralPath $target) { $remaining += $row }
    }
    $result.locked_residuals = $remaining
    $result | Add-Member -NotePropertyName residual_retry_time -NotePropertyValue (Get-Date -Format o) -Force
    $result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resultPath -Encoding utf8
    Write-Output "Locked residual directories remaining: $($remaining.Count)"
    if ($remaining.Count) { exit 1 }
    exit 0
}
if ($data.executed) { throw 'Cleanup already executed' }
$archive = Join-Path $workspaceRoot $data.archive.file
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLower() -ne $data.archive.sha256) { throw 'Evidence archive changed' }
$allowed = @('work\m9', 'work\client-graphics-lab') | ForEach-Object { Join-Path $workspaceRoot $_ }
$targets = @($data.targets | ForEach-Object {
    $resolved = (Resolve-Path -LiteralPath $_).Path.TrimEnd('\')
    if (-not ($allowed | Where-Object { $resolved.StartsWith($_ + '\', [StringComparison]::OrdinalIgnoreCase) })) { throw "Outside approved cleanup roots: $resolved" }
    if ((Get-Item -LiteralPath $resolved -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse target rejected' }
    foreach ($preserved in $data.preserved_directories) {
        $kept = [IO.Path]::GetFullPath($preserved).TrimEnd('\')
        if ($kept -eq $resolved -or $kept.StartsWith($resolved+'\',[StringComparison]::OrdinalIgnoreCase) -or $resolved.StartsWith($kept+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Preserved runtime overlaps deletion' }
    }
    foreach ($row in $data.preserved_files) {
        $kept = [IO.Path]::GetFullPath((Join-Path $workspaceRoot $row.file))
        if ($kept -eq $resolved -or $kept.StartsWith($resolved+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Preserved file overlaps deletion' }
    }
    $resolved
})
foreach ($row in $data.preserved_files) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspaceRoot $row.file) -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) { throw "Preservation pin changed: $($row.file)" }
}
$active = Get-Process | Where-Object { $_.Path -and $_.Path.StartsWith($workspaceRoot+'\',[StringComparison]::OrdinalIgnoreCase) }
foreach ($process in $active) {
    foreach ($target in $targets) {
        if ($process.Path -eq $target -or $process.Path.StartsWith($target+'\',[StringComparison]::OrdinalIgnoreCase)) { throw "Running process uses cleanup target: $($process.Id)" }
    }
}
$freeBefore = (Get-PSDrive -Name E).Free
$deleted = 0
$failures = @()
foreach ($target in $targets) {
    try { Remove-Item -LiteralPath $target -Recurse -Force; $deleted++ }
    catch { $failures += [pscustomobject]@{path=$target;error=$_.Exception.Message} }
    if ($deleted % 100 -eq 0) { Write-Output "Removed $deleted of $($targets.Count) obsolete targets" }
}
foreach ($row in $data.preserved_files) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspaceRoot $row.file) -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) { throw "Preserved file changed: $($row.file)" }
}
$result = [ordered]@{workspace=$workspaceRoot;deleted_targets=$deleted;requested_targets=$targets.Count;failures=$failures;preserved_hashes_verified=$true;free_bytes_before=$freeBefore;free_bytes_after=(Get-PSDrive -Name E).Free;archive=$data.archive;source_plan=$Plan;time=(Get-Date -Format o)}
$result | ConvertTo-Json -Depth 7 | Set-Content -LiteralPath (Join-Path $workspaceRoot 'inventory/workspace-cleanup-result-20261113.json') -Encoding utf8
$data.executed = $true
$data | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $planPath -Encoding utf8
$result | ConvertTo-Json -Depth 4
if ($failures.Count) { exit 1 }
