#!/bin/bash
# ============================================================
# CryptoSentinel — Oracle Cloud Deploy Script
# Run this ONCE on a fresh Ubuntu 22.04 Oracle Cloud VM
# Usage: bash deploy.sh
# ============================================================

set -e

echo "╔══════════════════════════════════════════════╗"
echo "║   CryptoSentinel — Oracle Cloud Deployment  ║"
echo "╚══════════════════════════════════════════════╝"

# ── 1. Install Docker ──────────────────────────────────────
echo ""
echo "▶ [1/5] Installing Docker..."
sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose-plugin git curl
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
echo "    Docker installed ✓"

# ── 2. Open OS Firewall ────────────────────────────────────
echo ""
echo "▶ [2/5] Opening OS firewall ports..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 3000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000:8003 -j ACCEPT
sudo apt-get install -y iptables-persistent
sudo netfilter-persistent save
echo "    Firewall ports opened ✓"

# ── 3. Check for .env.docker ───────────────────────────────
echo ""
echo "▶ [3/5] Checking environment config..."
if [ ! -f ".env.docker" ]; then
    echo ""
    echo "⚠  .env.docker not found!"
    echo "   Create it from the example:"
    echo "   cp .env.example .env.docker"
    echo "   nano .env.docker   # Fill in your real API keys"
    echo ""
    echo "   Then re-run: bash deploy.sh"
    exit 1
fi
echo "    .env.docker found ✓"

# ── 4. Build & Launch Containers ──────────────────────────
echo ""
echo "▶ [4/5] Building & starting all 5 services (this takes 5-15 min first time)..."
docker compose --env-file .env.docker up --build -d
echo "    Containers started ✓"

# ── 5. Health Check ────────────────────────────────────────
echo ""
echo "▶ [5/5] Waiting for health checks..."
sleep 30
docker compose ps

# ── Done ───────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║             Deployment Complete! ✅           ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
PUBLIC_IP=$(curl -s ifconfig.me)
echo "  Dashboard:    http://$PUBLIC_IP:3000"
echo "  Blockchain:   http://$PUBLIC_IP:8000/docs"
echo "  Agentic AI:   http://$PUBLIC_IP:8001/docs"
echo "  ML Risk:      http://$PUBLIC_IP:8002/docs"
echo "  Cybersecurity:http://$PUBLIC_IP:8003/docs"
echo ""
echo "  Manage:"
echo "  docker compose ps        # status"
echo "  docker compose logs -f   # all logs"
echo "  docker compose down      # stop all"
