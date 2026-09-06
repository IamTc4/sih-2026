"""
CryptoSentinel Cybersecurity & Threat Intelligence Service — Port 8003
Modules: Fraud Patterns · Evidence Trail · RBAC · Threat Intel Feeds · UPI Bridge
"""
import sys
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger("cryptosentinel.cyber")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: initialize threat intel feed in background."""
    try:
        from threat_intel.feed import get_threat_feed
        feed = get_threat_feed()
        logger.info("Threat intel feed initialized — performing initial refresh...")
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, feed.refresh)
        logger.info("Threat intel background refresh started")
    except Exception as e:
        logger.warning(f"Threat intel feed startup failed (non-fatal): {e}")
    yield
    logger.info("CryptoSentinel Cybersecurity service shutting down")


app = FastAPI(
    title="CryptoSentinel — Cybersecurity & Threat Intelligence API",
    description="""
## CryptoSentinel Cybersecurity Module

**Advanced crypto-crime detection, evidence management, and Indian law enforcement intelligence.**

### Capabilities
- **Graph-Based Fraud Detection**: 5 pattern detectors (Mixer/Tumbler, Peel Chain, Rapid Hopping, Scam Proximity, Structuring)
- **Live Threat Intel**: OFAC SDN sanctions list + CryptoScamDB + internal I4C/ED/CBI watchlist
- **Tamper-Evident Evidence Trail**: SQLite hash-chain with full verification and court-export
- **RBAC Policy Engine**: 5 roles, 4 data classification levels, PII redaction
- **UPI → Crypto Bridge**: Map Indian banking fraud complaints to crypto investigation leads
- **Legal Notice Intelligence**: Auto-suggest Section 91 BNSS / PMLA / IT Act notices

### Authentication
Pass `Authorization: Bearer <role>:<user_id>` for role-based access:
- `viewer:officer001` — Public data only
- `analyst:analyst001` — Internal + public
- `investigator:inv001` — Full access including PII
- `admin:admin001` — Full system access
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routes import router
app.include_router(router)


if __name__ == "__main__":
    print("=" * 60)
    print(" CryptoSentinel Cybersecurity & Threat Intelligence")
    print(" Port    : 8003")
    print(" Docs    : http://127.0.0.1:8003/docs")
    print(" Modules : Fraud Detection · Evidence Trail · RBAC")
    print("           Threat Intel · UPI Bridge")
    print("=" * 60)
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
