param([string]$Python = "python")
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$bin = Join-Path $root "bin"

# Install dependencies only: no editable package or generated sb.exe in Python Scripts.
& $Python -c "import sys; assert sys.version_info >= (3,11), 'Python 3.11+ required'"
if ($LASTEXITCODE -ne 0) { throw "Python check failed" }
& $Python -c "import pathlib,subprocess,sys,tomllib; p=pathlib.Path(sys.argv[1]); deps=tomllib.loads(p.read_text(encoding='utf-8'))['project']['dependencies']; subprocess.check_call([sys.executable,'-m','pip','install',*deps])" (Join-Path $root "pyproject.toml")
if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed; PATH unchanged" }

$config = Join-Path $root "config.yaml"
if (-not (Test-Path $config)) {
    Copy-Item (Join-Path $root "config.example.yaml") $config
}

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$entries = @($userPath -split ';' | Where-Object { $_ })
if (-not ($entries | Where-Object { $_.TrimEnd('\') -ieq $bin.TrimEnd('\') })) {
    [Environment]::SetEnvironmentVariable("Path", (($entries + $bin) -join ';'), "User")
}
$env:Path = "$bin;$env:Path"
Write-Host "Installed repo launcher: $bin\sb.cmd"
Write-Host "Open a NEW terminal and run: sb doctor or sb run"
Write-Host "If another sb command exists, check: where.exe sb"
Write-Host "Custom Python users can set SB_PYTHON to the Python executable path."
