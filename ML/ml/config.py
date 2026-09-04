"""
ml/config.py
─────────────
Central settings for the WalletTrace ML Risk Scoring module.
Reads from environment variables / .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()


class Settings:
    HOST: str   = os.getenv("HOST", "0.0.0.0")
    PORT: int   = int(os.getenv("PORT", "8002"))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"

    MODEL_PATH: str = os.getenv("MODEL_PATH", str(BASE_DIR / "ml" / "data" / "model.pkl"))

    HIGH_CONFIDENCE_THRESHOLD: float  = float(os.getenv("HIGH_CONFIDENCE_THRESHOLD",  "0.75"))
    MEDIUM_CONFIDENCE_THRESHOLD: float= float(os.getenv("MEDIUM_CONFIDENCE_THRESHOLD","0.45"))
    BEHAVIORAL_SIMILARITY_THRESHOLD: float = float(os.getenv("BEHAVIORAL_SIMILARITY_THRESHOLD","0.85"))

    BLOCKCHAIN_API_URL: str     = os.getenv("BLOCKCHAIN_API_URL",     "").rstrip("/")
    CYBERSECURITY_API_URL: str  = os.getenv("CYBERSECURITY_API_URL",  "").rstrip("/")


settings = Settings()
