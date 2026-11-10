[CmdletBinding()]
param([switch]$Restore,[string]$BackupPath)
$ErrorActionPreference='Stop'
$rfWorkspace=Split-Path -Parent $PSScriptRoot
$rfSettings=@(
    @{Path='HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR';Name='AppCaptureEnabled'},
    @{Path='HKCU:\System\GameConfigStore';Name='GameDVR_Enabled'}
)
if($Restore){
    if(-not $BackupPath){throw 'Supply the saved backup path'}
    $rfBackup=Get-Content -LiteralPath $BackupPath -Raw|ConvertFrom-Json
    if($rfBackup.schema -ne 1 -or $rfBackup.values.Count -ne 2){throw 'Invalid capture-settings backup'}
    foreach($rfRow in $rfBackup.values){
        if(-not ($rfSettings|Where-Object{$_.Path -eq $rfRow.Path -and $_.Name -eq $rfRow.Name})){throw 'Unexpected registry setting in backup'}
        if($rfRow.Exists -and $rfRow.Kind -ne 'DWord'){throw 'Unexpected saved value kind'}
    }
    foreach($rfRow in $rfBackup.values){
        if($rfRow.Exists){New-ItemProperty -LiteralPath $rfRow.Path -Name $rfRow.Name -PropertyType DWord -Value ([int]$rfRow.Value) -Force|Out-Null}
        elseif(Get-ItemProperty -LiteralPath $rfRow.Path -Name $rfRow.Name -ErrorAction SilentlyContinue){Remove-ItemProperty -LiteralPath $rfRow.Path -Name $rfRow.Name}
    }
    Write-Output 'Restored previous current-user game capture settings'
    return
}
$rfRows=@(foreach($rfSetting in $rfSettings){
    $rfKey=Get-Item -LiteralPath $rfSetting.Path
    $rfExists=$rfKey.GetValueNames() -contains $rfSetting.Name
    $rfKind=if($rfExists){$rfKey.GetValueKind($rfSetting.Name).ToString()}else{$null}
    if($rfExists -and $rfKind -ne 'DWord'){throw 'Unexpected existing capture value kind'}
    [ordered]@{Path=$rfSetting.Path;Name=$rfSetting.Name;Exists=$rfExists;Kind=$rfKind;Value=$(if($rfExists){$rfKey.GetValue($rfSetting.Name)}else{$null})}
})
$rfBackupRoot=Join-Path $rfWorkspace 'artifacts/environment'
New-Item -ItemType Directory -Path $rfBackupRoot -Force|Out-Null
$rfBackupFile=Join-Path $rfBackupRoot ('game-capture-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss-fff')+'.json')
[ordered]@{schema=1;scope='Current user game capture only';values=$rfRows}|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $rfBackupFile -Encoding utf8
foreach($rfSetting in $rfSettings){New-ItemProperty -LiteralPath $rfSetting.Path -Name $rfSetting.Name -PropertyType DWord -Value 0 -Force|Out-Null}
$rfVerified=@(foreach($rfSetting in $rfSettings){
    $rfValue=Get-ItemPropertyValue -LiteralPath $rfSetting.Path -Name $rfSetting.Name
    if($rfValue -ne 0){throw 'Capture setting verification failed'}
    [ordered]@{Path=$rfSetting.Path;Name=$rfSetting.Name;Value=$rfValue}
})
[ordered]@{scope='Current user';backup=$rfBackupFile;settings=$rfVerified;popup_absence_not_yet_observed=$true}|ConvertTo-Json -Depth 5
