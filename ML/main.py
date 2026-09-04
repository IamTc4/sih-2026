"""
main.py — ML Risk Scoring Module entry point
"""
import uvicorn
from ml.api import app
from ml.config import settings

if __name__ == "__main__":
    print("=" * 60)
    print(" WalletTrace — ML Risk Scoring Service")
    print(f" Port         : {settings.PORT}")
    print(f" Docs (Swagger): http://127.0.0.1:{settings.PORT}/docs")
    print("=" * 60)
    uvicorn.run("ml.api:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG_MODE)
