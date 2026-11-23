$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$bin = Join-Path $root "bin"
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$entries = @($userPath -split ';' | Where-Object {
    $_ -and $_.TrimEnd('\') -ine $bin.TrimEnd('\')
})
[Environment]::SetEnvironmentVariable("Path", ($entries -join ';'), "User")
Write-Host "Removed only this repository's bin entry from user PATH."
Write-Host "Repository, config, documents, Python and dependencies were not deleted."
Write-Host "Open a new terminal for the PATH change to take effect."
