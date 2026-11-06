<#
.SYNOPSIS
  Shows (default) or frees disk space on C: for the Ansys Student install. Nothing is deleted without -Apply.

.DESCRIPTION
  Dry run (default): lists every candidate with its size, the C: free space now and after, and the folders that
  can only be MOVED to D: by hand (never touched by this script).
  -Apply: deletes only the "safe to delete" group below, after a final Y/N confirmation.

  Safe to delete (all re-creatable):
    1. Claude Code session temp folders under %TEMP%\claude not modified for -KeepDays days (default 3),
       except the session given with -KeepSession.
    2. Other %TEMP% items not modified for -KeepDays days.
    3. Windows crash dumps (%LOCALAPPDATA%\CrashDumps).
    4. The uv package cache (via "uv cache clean").
  Optional (-IncludeOptional): %USERPROFILE%\.cache\codex-runtimes (re-downloaded by the Codex CLI when needed).
  Move by hand (reported only): .minecraft, Documents, Downloads.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File 01_Ansys\scripts\free_c_for_ansys.ps1
  powershell -ExecutionPolicy Bypass -File 01_Ansys\scripts\free_c_for_ansys.ps1 -Apply
#>
param(
    [switch]$Apply,
    [switch]$IncludeOptional,
    [int]$KeepDays = 3,
    [string]$KeepSession = "5b6739d5-84c2-4008-bc95-72d94cabd8d3"
)
$ErrorActionPreference = "Stop"
$cutoff = (Get-Date).AddDays(-$KeepDays)
$needGB = 50.0

function SizeGB($path) {
    if (-not (Test-Path -LiteralPath $path)) { return 0.0 }
    $item = Get-Item -Force -LiteralPath $path
    if (-not $item.PSIsContainer) { return [math]::Round($item.Length / 1GB, 2) }
    $sum = (Get-ChildItem -Force -Recurse -File -LiteralPath $path -ErrorAction SilentlyContinue |
            Measure-Object Length -Sum).Sum
    return [math]::Round([double]$sum / 1GB, 2)
}

function FreeGB { [math]::Round((Get-PSDrive C).Free / 1GB, 1) }

Write-Host "> measuring candidates (read-only, may take a minute)"
$plan = New-Object System.Collections.Generic.List[object]

# 1. old Claude session temp folders
$claudeTemp = Join-Path $env:TEMP "claude"
if (Test-Path $claudeTemp) {
    Get-ChildItem -Force -Directory $claudeTemp | ForEach-Object {
        Get-ChildItem -Force -Directory $_.FullName | Where-Object {
            $_.Name -ne $KeepSession -and $_.LastWriteTime -lt $cutoff
        } | ForEach-Object {
            $short = $_.Name.Substring(0, [math]::Min(8, $_.Name.Length))
            $plan.Add([pscustomobject]@{Group = "delete"; What = "Claude temp: " + $_.Parent.Name + "\" + $short
                                        Path = $_.FullName; GB = (SizeGB $_.FullName); Modified = $_.LastWriteTime })
        }
    }
}
# 2. other old temp items
Get-ChildItem -Force $env:TEMP | Where-Object { $_.Name -ne "claude" -and $_.LastWriteTime -lt $cutoff } | ForEach-Object {
    $plan.Add([pscustomobject]@{Group = "delete"; What = "Temp: " + $_.Name; Path = $_.FullName
                                GB = (SizeGB $_.FullName); Modified = $_.LastWriteTime })
}
# 3. crash dumps
$dumps = Join-Path $env:LOCALAPPDATA "CrashDumps"
if (Test-Path $dumps) {
    $plan.Add([pscustomobject]@{Group = "delete"; What = "Crash dumps"; Path = $dumps; GB = (SizeGB $dumps)
                                Modified = (Get-Item $dumps).LastWriteTime })
}
# 4. uv cache
$uv = Get-Command uv -ErrorAction SilentlyContinue
if ($uv) {
    $uvDir = (& $uv.Source cache dir).Trim()
    $plan.Add([pscustomobject]@{Group = "delete"; What = "uv cache (uv cache clean)"; Path = $uvDir; GB = (SizeGB $uvDir)
                                Modified = (Get-Item $uvDir).LastWriteTime })
}
# optional
$codex = Join-Path $env:USERPROFILE ".cache\codex-runtimes"
if (Test-Path $codex) {
    $plan.Add([pscustomobject]@{Group = $(if ($IncludeOptional) { "delete" } else { "optional" })
                                What = "Codex runtimes (re-downloadable)"; Path = $codex; GB = (SizeGB $codex)
                                Modified = (Get-Item $codex).LastWriteTime })
}
# move by hand
foreach ($m in @(@("Minecraft (launcher > Game directory)", "$env:APPDATA\.minecraft"),
                 @("Documents (Properties > Location)", [Environment]::GetFolderPath("MyDocuments")),
                 @("Downloads (Properties > Location)", "$env:USERPROFILE\Downloads"))) {
    if (Test-Path $m[1]) {
        $plan.Add([pscustomobject]@{Group = "move to D: by hand"; What = $m[0]; Path = $m[1]; GB = (SizeGB $m[1])
                                    Modified = (Get-Item $m[1]).LastWriteTime })
    }
}

$big = $plan | Where-Object { $_.GB -ge 0.05 }
$small = @($plan | Where-Object { $_.GB -lt 0.05 })
$big | Sort-Object Group, @{Expression = "GB"; Descending = $true} |
    Format-Table Group, GB, @{Label = "Modified"; Expression = { $_.Modified.ToString("yyyy-MM-dd") }}, What -AutoSize |
    Out-String -Width 160 | Write-Host
if ($small.Count) {
    Write-Host ("plus {0} small items under 0.05 GB each ({1} GB together), deleted with the same group" -f `
        $small.Count, [math]::Round(($small | Measure-Object GB -Sum).Sum, 2))
}

$del = ($plan | Where-Object Group -eq "delete" | Measure-Object GB -Sum).Sum
$mov = ($plan | Where-Object Group -eq "move to D: by hand" | Measure-Object GB -Sum).Sum
$opt = ($plan | Where-Object Group -eq "optional" | Measure-Object GB -Sum).Sum
$now = FreeGB
Write-Host ("C: free now {0} GB. After deleting: ~{1} GB. After also moving by hand: ~{2} GB{3}. Ansys Student asks {4} GB." -f `
    $now, [math]::Round($now + $del, 1), [math]::Round($now + $del + $mov, 1),
    $(if ($opt) { " (+{0} GB with -IncludeOptional)" -f [math]::Round($opt, 1) } else { "" }), $needGB)

if (-not $Apply) {
    Write-Host "Dry run: nothing was deleted. Next: rerun with -Apply to delete the 'delete' group."
    exit 0
}

$answer = Read-Host ("Delete the 'delete' group ({0} GB)? Type Y to confirm" -f [math]::Round($del, 1))
if ($answer -ne "Y") { Write-Host "Cancelled: nothing was deleted."; exit 1 }
foreach ($p in ($plan | Where-Object Group -eq "delete")) {
    Write-Host ("> deleting {0} ({1} GB)" -f $p.What, $p.GB)
    try {
        if ($p.What -like "uv cache*") { & $uv.Source cache clean | Out-Null }
        elseif ($p.What -eq "Crash dumps") { Get-ChildItem -Force $p.Path | Remove-Item -Recurse -Force -ErrorAction Stop }
        else { Remove-Item -LiteralPath $p.Path -Recurse -Force -ErrorAction Stop }
    } catch { Write-Host ("  skipped (in use or denied): " + $_.Exception.Message) }
}
Write-Host ("Done. C: free now {0} GB. Next: move the 'move to D: by hand' folders, then run the Ansys installer." -f (FreeGB))
