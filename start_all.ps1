# ============================================================
# WalletTrace - Single-Machine Startup Script (PowerShell)
# SIH 2026 Problem Statement: 26183
# ============================================================
# Starts all 5 services in separate terminal windows:
#   Blockchain   -> http://localhost:8000
#   ML           -> http://localhost:8002
#   Agentic AI   -> http://localhost:8001
#   Cybersecurity-> http://localhost:8003
#   Dashboard    -> http://localhost:3000
#
# Usage:
#   cd C:\work\sih2026
#   .\start_all.ps1
#
# To stop all: close the terminal windows or run:
#   .\stop_all.ps1
# ============================================================

$ROOT = $PSScriptRoot
if (-not $ROOT) { $ROOT = (Get-Location).Path }

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  WalletTrace - Starting All Services" -ForegroundColor Cyan
Write-Host "  SIH 2026 | Problem Statement 26183" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

function Start-Service-Window {
    param(
        [string]$Name,
        [string]$Dir,
        [string]$Command,
        [string]$Color = "Cyan"
    )
    Write-Host "  > Starting $Name ..." -ForegroundColor $Color
    $cmdArg = "cd '$Dir'; Write-Host '=== $Name ===' -ForegroundColor $Color; $Command"
    Start-Process powershell.exe -ArgumentList "-NoExit", "-Command", $cmdArg
}

# 1. Blockchain Service (port 8000)
Start-Service-Window -Name "Blockchain (port 8000)" -Dir "$ROOT\blockchain" -Command "python main.py" -Color "Blue"
Start-Sleep -Seconds 2

# 2. ML Risk Scoring (port 8002)
Start-Service-Window -Name "ML Risk Scoring (port 8002)" -Dir "$ROOT\ML" -Command "if (-not (Test-Path 'ml\data\model.pkl')) { Write-Host 'Training ML model...' -ForegroundColor Yellow; python train.py }; python main.py" -Color "Magenta"
Start-Sleep -Seconds 2

# 3. Agentic AI (port 8001)
Start-Service-Window -Name "Agentic AI (port 8001)" -Dir "$ROOT\Agentic_Ai" -Command "python -m uvicorn walletrace.api:app --host 0.0.0.0 --port 8001 --reload" -Color "Green"
Start-Sleep -Seconds 2

# 4. Cybersecurity (port 8003)
Start-Service-Window -Name "Cybersecurity & Evidence Vault (port 8003)" -Dir "$ROOT\Cybersecurity" -Command "python main.py" -Color "DarkYellow"
Start-Sleep -Seconds 2

# 5. Dashboard (port 3000)
Start-Service-Window -Name "Dashboard (port 3000)" -Dir "$ROOT\Dashboard" -Command "if (-not (Test-Path 'node_modules')) { Write-Host 'Installing packages...' -ForegroundColor Yellow; npm install }; npm run dev" -Color "Yellow"
Start-Sleep -Seconds 3

# Summary
Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  All 5 services started! URLs:" -ForegroundColor Green
Write-Host ""
Write-Host "  Dashboard         -> http://localhost:3000" -ForegroundColor Yellow
Write-Host "  Blockchain API    -> http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "  Agentic AI API    -> http://localhost:8001/docs" -ForegroundColor Green
Write-Host "  ML Risk Scoring   -> http://localhost:8002/docs" -ForegroundColor Magenta
Write-Host "  Cybersecurity     -> http://localhost:8003/docs" -ForegroundColor DarkYellow
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

Start-Sleep -Seconds 4
Start-Process "http://localhost:3000"
