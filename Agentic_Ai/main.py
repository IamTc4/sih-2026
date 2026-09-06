"""
main.py
────────
Entry point for the WalletTrace Agentic Orchestration Service.

Usage:
  python main.py                  # Start the API server on port 8000
  python main.py --port 9000      # Custom port
"""

import argparse
import uvicorn
from walletrace.case_store import init_db

def main():
    parser = argparse.ArgumentParser(description="WalletTrace Agentic Orchestration Service")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable hot reload (dev mode)")
    args = parser.parse_args()

    init_db()
    
    print(f"\n{'='*60}")
    print("  WalletTrace — Agentic Orchestration Module")
    print("  SIH26183 | Real-time Crypto Fraud Investigation")
    print(f"{'='*60}")
    print(f"  API server: http://{args.host}:{args.port}")
    print(f"  Docs:       http://{args.host}:{args.port}/docs")
    print(f"  Reload:     {args.reload}")
    print(f"{'='*60}\n")

    uvicorn.run(
        "walletrace.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
