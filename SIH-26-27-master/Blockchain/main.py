"""
main.py — WalletTrace Blockchain Analytics Service
"""
import argparse
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="WalletTrace Blockchain Analytics Service")
    parser.add_argument("--host",   default="0.0.0.0")
    parser.add_argument("--port",   type=int, default=8001)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--csv",    action="store_true",
                        help="Run in offline CSV mode (no live Tronscan API calls)")
    args = parser.parse_args()

    if args.csv:
        import os
        os.environ["CSV_MODE"] = "1"

    print(f"\n{'='*60}")
    print("  WalletTrace — Blockchain Analytics Module")
    print("  SIH26183 | Tron/USDT-TRC20 On-chain Tracing")
    print(f"{'='*60}")
    print(f"  API:    http://{args.host}:{args.port}")
    print(f"  Docs:   http://{args.host}:{args.port}/docs")
    print(f"  Mode:   {'OFFLINE CSV' if args.csv else 'LIVE Tronscan API'}")
    print(f"{'='*60}\n")

    uvicorn.run("blockchain.api:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
