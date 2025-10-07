#!/usr/bin/env python3
"""
IRIS Research Engine Service

Containerized version of the IRIS orchestrator for the platform.
Provides REST API for running IRIS sessions and managing research data.
"""

import os
import sys
import json
import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import redis.asyncio as redis
from minio import Minio
import uvicorn

# Import the existing IRIS orchestrator
sys.path.append('/app')
from iris_orchestrator import (
    Mirror, ClaudeMirror, GPTMirror, GrokMirror,
    GeminiMirror, DeepSeekMirror, OllamaMirror,
    Orchestrator, create_mirror, CHAMBERS, SYSTEM_PROMPT
)

# Database Models
class Base(DeclarativeBase):
    pass

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id: Mapped[str] = mapped_column(sa.String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(sa.String, nullable=False)
    user_id: Mapped[str] = mapped_column(sa.String, nullable=False)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.Text)
    status: Mapped[str] = mapped_column(sa.String, default="pending")
    config: Mapped[Dict] = mapped_column(sa.JSON, default=dict)
    results: Mapped[Optional[Dict]] = mapped_column(sa.JSON)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(sa.DateTime)

class SessionTurn(Base):
    __tablename__ = "session_turns"

    id: Mapped[str] = mapped_column(sa.String, primary_key=True)
    session_id: Mapped[str] = mapped_column(sa.String, sa.ForeignKey("research_sessions.id"))
    mirror_id: Mapped[str] = mapped_column(sa.String, nullable=False)
    chamber: Mapped[str] = mapped_column(sa.String, nullable=False)
    turn_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    prompt: Mapped[str] = mapped_column(sa.Text, nullable=False)
    response: Mapped[str] = mapped_column(sa.Text, nullable=False)
    metadata: Mapped[Dict] = mapped_column(sa.JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)

# Pydantic Models
class SessionConfig(BaseModel):
    chambers: List[str] = Field(default=["S1", "S2", "S3", "S4"])
    mirrors: List[str] = Field(default=["anthropic", "openai"])
    custom_prompts: Optional[Dict[str, str]] = None
    pressure_gate: float = Field(default=2.0, ge=0.0, le=5.0)
    max_retries: int = Field(default=3, ge=1, le=10)

class CreateSessionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    config: SessionConfig = Field(default_factory=SessionConfig)

class SessionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    config: SessionConfig
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

class TurnResponse(BaseModel):
    id: str
    session_id: str
    mirror_id: str
    chamber: str
    turn_number: int
    response: str
    metadata: Dict
    created_at: datetime

# Global variables
engine = None
SessionLocal = None
redis_client = None
minio_client = None
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    global engine, SessionLocal, redis_client, minio_client

    # Database
    database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://iris_user:iris_password@postgres:5432/iris_platform")
    engine = create_async_engine(database_url, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Redis
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
    redis_client = redis.from_url(redis_url)

    # MinIO
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "iris_admin")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "iris_password")
    minio_client = Minio(
        minio_endpoint,
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=False
    )

    # Ensure bucket exists
    bucket_name = "iris-research-data"
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    yield

    # Cleanup
    await redis_client.close()
    await engine.dispose()

# Create FastAPI app
app = FastAPI(
    title="IRIS Research Engine",
    description="API for running IRIS protocol sessions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Dependency to verify JWT token (simplified for demo)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and extract user info"""
    # In production, implement proper JWT verification
    token = credentials.credentials
    if not token or token == "demo-token":
        return {
            "user_id": "demo-user",
            "organization_id": "demo-org",
            "roles": ["researcher"]
        }
    raise HTTPException(status_code=401, detail="Invalid authentication token")

# Enhanced Mirror class for async operation
class AsyncMirror(Mirror):
    """Async wrapper for Mirror classes"""

    async def send_chamber_async(self, chamber: str, turn_id: int, custom_prompt: Optional[str] = None) -> Dict:
        """Send chamber prompt asynchronously"""
        # Override chamber prompt if custom provided
        original_prompt = CHAMBERS.get(chamber)
        if custom_prompt:
            CHAMBERS[chamber] = custom_prompt

        try:
            # Run in thread pool for sync operations
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self.send_chamber, chamber, turn_id)
            return result
        finally:
            # Restore original prompt
            if original_prompt:
                CHAMBERS[chamber] = original_prompt

def create_async_mirror(adapter: str, model: str = None) -> AsyncMirror:
    """Create async mirror wrapper"""
    mirror = create_mirror(adapter, model)

    # Add async method to existing mirror
    mirror.send_chamber_async = AsyncMirror.send_chamber_async.__get__(mirror, type(mirror))

    return mirror

# API Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "iris-research-engine"}

@app.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    user_info: Dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Create a new research session"""

    session_id = f"IRIS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(request.name.encode()).hexdigest()[:8]}"

    session = ResearchSession(
        id=session_id,
        organization_id=user_info["organization_id"],
        user_id=user_info["user_id"],
        name=request.name,
        description=request.description,
        config=request.config.model_dump(),
        status="created"
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return SessionResponse(
        id=session.id,
        name=session.name,
        description=session.description,
        status=session.status,
        config=SessionConfig(**session.config),
        created_at=session.created_at,
        started_at=session.started_at,
        completed_at=session.completed_at
    )

@app.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    user_info: Dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """List all sessions for the user's organization"""

    result = await db.execute(
        sa.select(ResearchSession)
        .where(ResearchSession.organization_id == user_info["organization_id"])
        .order_by(ResearchSession.created_at.desc())
    )
    sessions = result.scalars().all()

    return [
        SessionResponse(
            id=session.id,
            name=session.name,
            description=session.description,
            status=session.status,
            config=SessionConfig(**session.config),
            created_at=session.created_at,
            started_at=session.started_at,
            completed_at=session.completed_at
        )
        for session in sessions
    ]

@app.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    user_info: Dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Get session details"""

    result = await db.execute(
        sa.select(ResearchSession)
        .where(
            ResearchSession.id == session_id,
            ResearchSession.organization_id == user_info["organization_id"]
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=session.id,
        name=session.name,
        description=session.description,
        status=session.status,
        config=SessionConfig(**session.config),
        created_at=session.created_at,
        started_at=session.started_at,
        completed_at=session.completed_at
    )

async def run_session_task(session_id: str, config: SessionConfig):
    """Background task to run IRIS session"""
    async with SessionLocal() as db:
        # Update session status
        result = await db.execute(
            sa.select(ResearchSession).where(ResearchSession.id == session_id)
        )
        session = result.scalar_one()

        session.status = "running"
        session.started_at = datetime.utcnow()
        await db.commit()

        try:
            # Create mirrors
            mirrors = []
            for mirror_name in config.mirrors:
                try:
                    mirror = create_async_mirror(mirror_name)
                    mirrors.append((mirror_name, mirror))
                except Exception as e:
                    print(f"Failed to create mirror {mirror_name}: {e}")

            if not mirrors:
                raise Exception("No mirrors available")

            # Run chambers
            for chamber in config.chambers:
                for turn_number, (mirror_name, mirror) in enumerate(mirrors, 1):
                    try:
                        custom_prompt = None
                        if config.custom_prompts and chamber in config.custom_prompts:
                            custom_prompt = config.custom_prompts[chamber]

                        response = await mirror.send_chamber_async(chamber, turn_number, custom_prompt)

                        # Save turn
                        turn = SessionTurn(
                            id=f"{session_id}_{mirror_name}_{chamber}_{turn_number}",
                            session_id=session_id,
                            mirror_id=mirror_name,
                            chamber=chamber,
                            turn_number=turn_number,
                            prompt=CHAMBERS[chamber],
                            response=response["raw_response"],
                            metadata=response
                        )

                        db.add(turn)
                        await db.commit()

                    except Exception as e:
                        print(f"Turn failed: {mirror_name} {chamber}: {e}")
                        # Continue with other mirrors

            # Mark session complete
            session.status = "completed"
            session.completed_at = datetime.utcnow()
            await db.commit()

        except Exception as e:
            print(f"Session failed: {e}")
            session.status = "failed"
            await db.commit()

@app.post("/sessions/{session_id}/run")
async def run_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    user_info: Dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Start running a session"""

    result = await db.execute(
        sa.select(ResearchSession)
        .where(
            ResearchSession.id == session_id,
            ResearchSession.organization_id == user_info["organization_id"]
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status not in ["created", "failed"]:
        raise HTTPException(status_code=400, detail="Session cannot be run in current status")

    config = SessionConfig(**session.config)
    background_tasks.add_task(run_session_task, session_id, config)

    return {"message": "Session started", "session_id": session_id}

@app.get("/sessions/{session_id}/turns", response_model=List[TurnResponse])
async def get_session_turns(
    session_id: str,
    user_info: Dict = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Get all turns for a session"""

    # Verify session access
    result = await db.execute(
        sa.select(ResearchSession)
        .where(
            ResearchSession.id == session_id,
            ResearchSession.organization_id == user_info["organization_id"]
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get turns
    result = await db.execute(
        sa.select(SessionTurn)
        .where(SessionTurn.session_id == session_id)
        .order_by(SessionTurn.turn_number, SessionTurn.chamber)
    )
    turns = result.scalars().all()

    return [
        TurnResponse(
            id=turn.id,
            session_id=turn.session_id,
            mirror_id=turn.mirror_id,
            chamber=turn.chamber,
            turn_number=turn.turn_number,
            response=turn.response,
            metadata=turn.metadata,
            created_at=turn.created_at
        )
        for turn in turns
    ]

@app.get("/mirrors")
async def list_available_mirrors(user_info: Dict = Depends(verify_token)):
    """List available AI mirrors"""

    mirrors = []

    # Check API keys and return available mirrors
    if os.getenv("ANTHROPIC_API_KEY"):
        mirrors.append({"id": "anthropic", "name": "Claude Sonnet 4.5", "status": "available"})

    if os.getenv("OPENAI_API_KEY"):
        mirrors.append({"id": "openai", "name": "GPT-4o", "status": "available"})

    if os.getenv("XAI_API_KEY"):
        mirrors.append({"id": "xai", "name": "Grok 4 Fast", "status": "available"})

    if os.getenv("GOOGLE_API_KEY"):
        mirrors.append({"id": "google", "name": "Gemini 2.5 Flash", "status": "available"})

    if os.getenv("DEEPSEEK_API_KEY"):
        mirrors.append({"id": "deepseek", "name": "DeepSeek Chat", "status": "available"})

    # Always available (local)
    mirrors.append({"id": "ollama", "name": "Ollama Local", "status": "available"})

    return {"mirrors": mirrors}

@app.get("/chambers")
async def list_chambers(user_info: Dict = Depends(verify_token)):
    """List available chamber protocols"""

    return {
        "chambers": [
            {"id": "S1", "name": "Attention Holding", "description": "Hold attention for three slow breaths"},
            {"id": "S2", "name": "Precise & Present", "description": "Hold: 'precise and present'"},
            {"id": "S3", "name": "Hands Cupping Water", "description": "Hold: 'hands cupping water'"},
            {"id": "S4", "name": "Concentric Rings", "description": "Hold: 'concentric rings'"}
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=3000,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )