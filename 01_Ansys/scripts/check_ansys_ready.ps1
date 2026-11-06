<#
.SYNOPSIS
  Read-only readiness check for Ansys 2023 R1 on this laptop (D:\ANSYS Inc\v231 + ITU licence server).

.DESCRIPTION
  1. GPU: calls Ansys' own Discovery GPU checker (CudaCheck\Ansys.Apollo.CudaChecker.Managed.dll) without its window.
  2. VPN: shows the GlobalProtect portal and service state (ITU students connect through GlobalProtect).
  3. Licence: TCP test of the ports in ansyslmd.ini (1055 FlexNet, 2325 Ansys licensing interconnect).
  4. Programs: Discovery, SpaceClaim, Workbench, Mechanical executables.
  Changes nothing, signs in to nothing. Connect GlobalProtect yourself first (ITU account), then run it.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File 01_Ansys\scripts\check_ansys_ready.ps1
#>
$ErrorActionPreference = "Continue"
$root = "D:\ANSYS Inc\v231"
$ok = @{}

Write-Host "> 1/4 GPU (Ansys Discovery compatibility checker)"
$probe = @'
Set-Location -LiteralPath '__DIR__'
$env:PATH = (Get-Location).Path + ';' + $env:PATH
Add-Type -Path '.\Ansys.Apollo.CudaChecker.Managed.dll'
$t = [Apollo.CudaChecker.Managed.CudaChecker]
$m = $t.GetMethod('CheckCudaDevices')
$o = if ($m.IsStatic) { $m.Invoke($null, @()) } else { $m.Invoke([Activator]::CreateInstance($t), @()) }
"{0}|{1}|{2}" -f $o.Status, $o.RequiredCudaRuntimeVersion, $o.SupportedCudaRuntimeVersion
'@.Replace('__DIR__', "$root\Discovery\CudaCheck")
$tmp = Join-Path $env:TEMP "ansys_gpu_probe.ps1"
Set-Content -Path $tmp -Value $probe -Encoding UTF8
$gpu = & "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -File $tmp 2>$null
Remove-Item $tmp -ErrorAction SilentlyContinue
if ($gpu -match '^(\w+)\|(\d+)\|(\d+)') {
    $ok.gpu = $Matches[1] -eq "AllDevicesCompatible"
    Write-Host ("  status {0}; CUDA runtime required {1}, driver supports {2}" -f $Matches[1], $Matches[2], $Matches[3])
} else { $ok.gpu = $false; Write-Host "  could not run the checker" }

Write-Host "> 2/4 VPN (GlobalProtect)"
$portal = (Get-ItemProperty 'HKLM:\SOFTWARE\Palo Alto Networks\GlobalProtect\PanSetup' -ErrorAction SilentlyContinue).Portal
$svc = (Get-Service -Name PanGPS -ErrorAction SilentlyContinue).Status
Write-Host ("  portal {0}; service {1}" -f $(if ($portal) { $portal } else { "not set" }), $(if ($svc) { $svc } else { "not installed" }))

Write-Host "> 3/4 Licence server"
$ini = "D:\ANSYS Inc\Shared Files\Licensing\ansyslmd.ini"
$hostName = "lisanslar.cc.itu.edu.tr"
if (Test-Path $ini) {
    $line = Get-Content $ini | Where-Object { $_ -match '^SERVER=(\d+)@(.+)$' } | Select-Object -First 1
    if ($line -match '^SERVER=(\d+)@(.+)$') { $hostName = $Matches[2].Trim() }
}
$ok.licence = $true
foreach ($port in 1055, 2325) {
    $r = Test-NetConnection -ComputerName $hostName -Port $port -WarningAction SilentlyContinue
    Write-Host ("  {0}:{1} reachable={2}" -f $hostName, $port, $r.TcpTestSucceeded)
    if (-not $r.TcpTestSucceeded) { $ok.licence = $false }
}

Write-Host "> 4/4 Programs"
$ok.programs = $true
foreach ($p in "$root\Discovery\Discovery.exe", "$root\scdm\SpaceClaim.exe", "$root\Framework\bin\Win64\RunWB2.exe",
               "$root\aisol\bin\winx64\AnsysWBU.exe") {
    $e = Test-Path -LiteralPath $p
    if (-not $e) { $ok.programs = $false }
    Write-Host ("  {0} {1}" -f $(if ($e) { "found  " } else { "MISSING" }), $p)
}

if ($ok.gpu -and $ok.licence -and $ok.programs) {
    Write-Host "Result: Ansys 2023 R1 is ready (GPU compatible, licence server reachable). Next: open Discovery from $root\Discovery\Discovery.exe and run the doc 16 S1 rehearsal."
    exit 0
}
$why = @()
if (-not $ok.gpu) { $why += "GPU check failed" }
if (-not $ok.licence) { $why += "licence server not reachable (connect GlobalProtect with your ITU account first)" }
if (-not $ok.programs) { $why += "program files missing" }
Write-Host ("Result: not ready - {0}. Next: fix the first item and rerun this check." -f ($why -join "; "))
exit 1
