# ============================================================
# WalletTrace — Stop All Services Script (PowerShell)
# SIH 2026 Problem Statement: 26183
# ============================================================
# Stops processes listening on ports 3000, 8000, 8001, 8002, 8003
# ============================================================

$ports = @(3000, 8000, 8001, 8002, 8003)

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "  Stopping WalletTrace Services..." -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

foreach ($port in $ports) {
    try {
        $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($conns) {
            foreach ($c in $conns) {
                $pidToKill = $c.OwningProcess
                if ($pidToKill -gt 0) {
                    Write-Host "  ▸ Stopping process $pidToKill on port $port..." -ForegroundColor Yellow
                    Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
                }
            }
            Write-Host "  ✓ Port $port freed." -ForegroundColor Green
        } else {
            Write-Host "  • Port $port is already inactive." -ForegroundColor Gray
        }
    } catch {
        Write-Warning "Could not inspect port $port : $_"
    }
}

Write-Host ""
Write-Host "All WalletTrace services stopped." -ForegroundColor Green
