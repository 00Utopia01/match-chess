$root = git rev-parse --show-toplevel
Set-Location $root  # Ti sposta automaticamente nella radice
$f = git ls-files '*.py'

if ($f) {
    Write-Host "------------------------- Eseguendo Pylint -------------------------" -ForegroundColor Cyan
    pylint $f
    Write-Host "------------------------- Eseguendo Flake8 -------------------------" -ForegroundColor Cyan
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=venv
    Write-Host "------------------------- Eseguendo MyPy ---------------------------" -ForegroundColor Cyan
    mypy $f --explicit-package-bases --namespace-packages
    Write-Host "------------------------- Eseguendo Black --------------------------" -ForegroundColor Cyan
    black --check --diff $f
    Write-Host "------------------------- Eseguendo ISort --------------------------" -ForegroundColor Cyan
    isort --check-only --profile black --diff $f
}