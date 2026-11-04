$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent $PSScriptRoot
$sdkFolder = Join-Path $workspace 'local/directx81b'
$package = Join-Path $sdkFolder 'DX81b_SDK.exe'
$url = 'https://archive.org/download/dx81b_sdk/DX81b_SDK.exe'
New-Item -ItemType Directory -Force -Path $sdkFolder | Out-Null
if (-not (Test-Path -LiteralPath $package)) { Invoke-WebRequest -Uri $url -OutFile $package -TimeoutSec 240 }
$sha1 = (Get-FileHash -LiteralPath $package -Algorithm SHA1).Hash
if ($sha1 -ne '221C60334DA54E8E670741E7090E51255AD0284C') { throw 'SDK archive SHA1 mismatch' }
$signature = Get-AuthenticodeSignature -LiteralPath $package
if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'CN=Microsoft Corporation,') { throw 'SDK Microsoft signature verification failed' }
$extracted = Join-Path $sdkFolder 'extracted'
New-Item -ItemType Directory -Force -Path $extracted | Out-Null
tar.exe -xf $package -C $extracted 'DX8.1b SDK/DXF/DXSDK/include' 'DX8.1b SDK/DXF/DXSDK/lib'
if ($LASTEXITCODE -ne 0) { throw 'SDK extraction failed' }
$sdkRoot = Join-Path $extracted 'DX8.1b SDK/DXF/DXSDK'
$overlay = Join-Path $sdkFolder 'include-overlay'
New-Item -ItemType Directory -Force -Path $overlay | Out-Null
$headers = @(Get-ChildItem -LiteralPath (Join-Path $sdkRoot 'include') -File | Where-Object Name -Match '^(d3d8|d3dx8|dxerr8|dxfile)')
$records = foreach ($header in $headers) {
    Copy-Item -LiteralPath $header.FullName -Destination $overlay
    [ordered]@{ name=$header.Name; sha256=(Get-FileHash -LiteralPath $header.FullName -Algorithm SHA256).Hash.ToLowerInvariant() }
}
$report = [ordered]@{
    package_url=$url; archive_metadata='https://archive.org/metadata/dx81b_sdk'; sha1=$sha1.ToLowerInvariant()
    sha256=(Get-FileHash -LiteralPath $package -Algorithm SHA256).Hash.ToLowerInvariant()
    authenticode_status=[string]$signature.Status; signer=$signature.SignerCertificate.Subject
    sdk_root=$sdkRoot; include_overlay=$overlay; headers=@($records)
    method='Extract headers/libs only. No installer execution. Overlay excludes legacy copies of Windows system headers.'
}
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $workspace 'inventory/directx81b-sdk.json') -Encoding utf8
Write-Output "Verified DirectX 8.1b SDK; overlay headers: $($headers.Count)"
