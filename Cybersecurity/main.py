"""
Cybersecurity Module Server — Port 8003
Provides threat signature detection, blacklist checks, and SHA-256 evidence chain anchoring.
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="WalletTrace Cybersecurity & Evidence Trail API",
    description="Threat signature engine (mixers, peel chains, rapid hops, structuring) and tamper-evident SHA-256 audit ledger.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    print("=========================================================")
    print(" Starting WalletTrace Cybersecurity Service...")
    print(" Port: 8003")
    print(" Docs: http://127.0.0.1:8003/docs")
    print("=========================================================")
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
