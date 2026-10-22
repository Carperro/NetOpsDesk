$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot

try {
    $pipAuditAvailable = python -c "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('pip_audit') else 1)"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Running pip-audit against requirements.lock..."
        python -m pip_audit --require-hashes -r requirements.lock
        exit $LASTEXITCODE
    }

    Write-Warning "pip-audit is not installed; running pip check. This does not scan known vulnerabilities."
    python -m pip check
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
