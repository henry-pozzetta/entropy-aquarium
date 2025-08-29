<#
  setup.ps1 — Windows/PowerShell bootstrap for Entropy Aquarium
  -------------------------------------------------------------
  One-command local setup for contributors:
    - Creates (or recreates) Python venv
    - Activates venv
    - Upgrades pip
    - Runs project scaffold (setup.py)
    - Installs requirements.txt

  Usage examples (run from repo root):
    PS> .\setup.ps1
    PS> .\setup.ps1 -RecreateVenv
    PS> .\setup.ps1 -PythonExe python3
    PS> .\setup.ps1 -SkipScaffold -SkipDeps
#>

param(
  [switch]$RecreateVenv,
  [string]$PythonExe = "python",
  [switch]$SkipDeps,
  [switch]$SkipScaffold
)

$ErrorActionPreference = 'Stop'

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "[ OK ] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[ERR ] $msg" -ForegroundColor Red }

# Verify repo root (expect setup.py here)
if (-not (Test-Path -Path .\setup.py)) {
  Write-Err "setup.py not found. Run this script from the repository root."
  exit 1
}

Write-Info "Entropy Aquarium setup starting…"

# Optional: recreate venv
if ($RecreateVenv -and (Test-Path .\venv)) {
  Write-Warn "Removing existing venv…"
  Remove-Item -Recurse -Force .\venv
}

# Create venv if missing
if (-not (Test-Path .\venv)) {
  Write-Info "Creating virtual environment (venv)…"
  & $PythonExe -m venv venv
  if ($LASTEXITCODE -ne 0) { Write-Err "Failed to create venv"; exit 2 }
} else {
  Write-Info "Using existing venv" 
}

# Activate venv
Write-Info "Activating venv…"
. .\venv\Scripts\Activate.ps1
if (-not $env:VIRTUAL_ENV) { Write-Err "Venv activation failed"; exit 3 }
Write-Ok "Venv: $env:VIRTUAL_ENV"

# Upgrade pip
Write-Info "Upgrading pip…"
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

# Run scaffold (setup.py) unless skipped
if (-not $SkipScaffold) {
  Write-Info "Running project scaffold (python setup.py)…"
  python .\setup.py
} else {
  Write-Warn "Skipping scaffold (per flag)"
}

# Install dependencies unless skipped
if (-not $SkipDeps) {
  if (Test-Path .\requirements.txt) {
    Write-Info "Installing dependencies from requirements.txt…"
    python -m pip install -r .\requirements.txt
  } else {
    Write-Warn "requirements.txt not found; skipping dependency install"
  }
} else {
  Write-Warn "Skipping dependency installation (per flag)"
}

# Print versions
Write-Info "Python / pip versions:"
python -V
python -m pip --version

Write-Ok "Setup complete. You can now start coding."
