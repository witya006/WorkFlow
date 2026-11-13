$ErrorActionPreference='Stop'
$workspaceRoot=[IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot)).TrimEnd('\')
$resultPath=Join-Path $workspaceRoot 'inventory/workspace-cleanup-result-20261113.json'
$plan=Get-Content -LiteralPath (Join-Path $workspaceRoot 'inventory/workspace-cleanup-plan-20261113.json') -Raw | ConvertFrom-Json
$result=Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
Add-Type -TypeDefinition @'
using System.Runtime.InteropServices;
public static class OwnedTestFonts {
    [DllImport("gdi32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    public static extern bool RemoveFontResourceW(string file);
}
'@
$remaining=@();$registrations=0
foreach ($failure in $result.failures) {
    $target=[IO.Path]::GetFullPath($failure.path).TrimEnd('\')
    if ($target -notin $plan.targets -or -not $target.StartsWith($workspaceRoot+'\work\m9\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Unexpected retry target' }
    if (-not (Test-Path -LiteralPath $target)) { $result.deleted_targets++; continue }
    $resolved=(Resolve-Path -LiteralPath $target).Path.TrimEnd('\')
    if ($resolved -ne $target) {throw 'Resolved retry target differs'}
    foreach ($font in Get-ChildItem -LiteralPath $target -Filter 010.TTF -Recurse -File -Force) {
        $fontPath=[IO.Path]::GetFullPath($font.FullName)
        if (-not $fontPath.StartsWith($target+'\',[StringComparison]::OrdinalIgnoreCase)) {throw 'Font outside obsolete run'}
        for ($i=0; $i -lt 4096; $i++) {
            if (-not [OwnedTestFonts]::RemoveFontResourceW($fontPath)) {break}
            $registrations++
        }
    }
    # A locked font must not prevent deletion of unrelated disposable assets.
    Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction Continue 2>$null
    if (Test-Path -LiteralPath $target) {
        $remaining += [pscustomobject]@{path=$target;error='Locked residual files; inspect before retry'}
    } else { $result.deleted_targets++ }
}
foreach ($row in $plan.preserved_files) {
    if ((Get-FileHash -LiteralPath (Join-Path $workspaceRoot $row.file) -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) {throw 'Preserved file changed'}
}
$result.failures=$remaining
$result.free_bytes_after=(Get-PSDrive -Name E).Free
$result | Add-Member -NotePropertyName removed_owned_font_registrations -NotePropertyValue $registrations -Force
$result | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resultPath -Encoding utf8
[pscustomobject]@{removed=$result.deleted_targets;remaining=$remaining.Count;font_registrations=$registrations;freed_GiB=($result.free_bytes_after-$result.free_bytes_before)/1GB} | ConvertTo-Json
if ($remaining.Count) {exit 1}
