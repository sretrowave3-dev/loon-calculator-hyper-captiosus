# PowerShell Launcher for Smart AI Calculator
Set-Location -LiteralPath $PSScriptRoot
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$pyFound = $false

# 1. Try py -3.15
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3.15 smart_calculator.py $args
    if ($LASTEXITCODE -eq 0) { exit 0 }
    & py smart_calculator.py $args
    if ($LASTEXITCODE -eq 0) { exit 0 }
    $pyFound = $true
}

# 2. Try python
if (Get-Command python -ErrorAction SilentlyContinue) {
    & python smart_calculator.py $args
    exit $LASTEXITCODE
}

# 3. Direct path fallback
$directPath = "$env:LOCALAPPDATA\Programs\Python\Python315\python.exe"
if (Test-Path $directPath) {
    & $directPath smart_calculator.py $args
    exit $LASTEXITCODE
}

Write-Error "[ERROR] Python 3.15 or py launcher could not be located in your environment."
