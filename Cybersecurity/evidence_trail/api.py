"""
FastAPI REST API for Evidence Trail Service
Endpoints: POST /log-event, GET /verify/{entry_id}, GET /chain/verify
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import json

from .service import EvidenceTrailService, LogEntry


class LogEventRequest(BaseModel):
    """Request model for logging an event."""
    event_type: str = Field(..., description="Type of event (e.g., wallet_trace, cluster_result)")
    payload: dict = Field(..., description="Event data payload")


class LogEventResponse(BaseModel):
    """Response model for logged event."""
    entry_id: int
    timestamp: str
    event_type: str
    content_hash: str
    previous_hash: str
    chain_hash: str


class VerifyResponse(BaseModel):
    """Response model for verification."""
    valid: bool
    entry_id: int
    content_hash_valid: bool
    chain_link_valid: bool
    chain_hash_valid: bool
    entry: Optional[dict] = None
    error: Optional[str] = None


class ChainVerifyResponse(BaseModel):
    """Response model for chain verification."""
    valid: bool
    entries_checked: int
    errors: List[str]
    final_chain_hash: str


class EntryResponse(BaseModel):
    """Response model for log entry."""
    entry_id: int
    timestamp: str
    event_type: str
    payload: dict
    content_hash: str
    previous_hash: str
    chain_hash: str


# Global service instance (in production, use dependency injection)
_service: EvidenceTrailService | None = None


def get_service() -> EvidenceTrailService:
    global _service
    if _service is None:
        _service = EvidenceTrailService()
    return _service


# Security
security = HTTPBearer(auto_error=False)


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Simple token verification - replace with proper auth in production."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    # In production, validate JWT or API key here
    return credentials.credentials


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Evidence Trail Service",
        description="Tamper-evident hash-chain logging for fraud detection pipeline",
        version="1.0.0"
    )

    @app.post("/log-event", response_model=LogEventResponse, status_code=status.HTTP_201_CREATED)
    async def log_event(
        request: LogEventRequest,
        service: EvidenceTrailService = Depends(get_service),
        token: str = Depends(verify_token)
    ):
        """
        Serialize an event, hash it, append to the immutable hash-chain log.
        """
        entry = service.log_event(request.event_type, request.payload)
        return LogEventResponse(
            entry_id=entry.entry_id,
            timestamp=entry.timestamp,
            event_type=entry.event_type,
            content_hash=entry.content_hash,
            previous_hash=entry.previous_hash,
            chain_hash=entry.chain_hash
        )

    @app.get("/verify/{entry_id}", response_model=VerifyResponse)
    async def verify_entry(
        entry_id: int,
        service: EvidenceTrailService = Depends(get_service),
        token: str = Depends(verify_token)
    ):
        """
        Confirm the hash matches and the chain is unbroken for a specific entry.
        """
        result = service.verify_entry(entry_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return VerifyResponse(**result)

    @app.get("/chain/verify", response_model=ChainVerifyResponse)
    async def verify_chain(
        start_id: int = 1,
        end_id: Optional[int] = None,
        service: EvidenceTrailService = Depends(get_service),
        token: str = Depends(verify_token)
    ):
        """
        Verify the entire hash-chain integrity from start_id to end_id.
        """
        result = service.verify_chain(start_id, end_id)
        return ChainVerifyResponse(**result)

    @app.get("/entries", response_model=List[EntryResponse])
    async def list_entries(
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        service: EvidenceTrailService = Depends(get_service),
        token: str = Depends(verify_token)
    ):
        """List log entries with optional filtering."""
        entries = service.get_entries(event_type, limit, offset)
        return [EntryResponse(**e.to_dict()) for e in entries]

    @app.get("/entries/{entry_id}", response_model=EntryResponse)
    async def get_entry(
        entry_id: int,
        service: EvidenceTrailService = Depends(get_service),
        token: str = Depends(verify_token)
    ):
        """Get a specific log entry by ID."""
        entry = service.get_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        return EntryResponse(**entry.to_dict())

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "evidence_trail"}

    return app


# For direct running
if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8001)