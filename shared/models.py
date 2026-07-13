import uuid
import enum
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, JSON, ARRAY
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

# Enums
class JobType(str, enum.Enum):
    COMPUTE = "COMPUTE"
    IO_BOUND = "IO_BOUND"
    ML_INFERENCE = "ML_INFERENCE"

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    DISPATCHED = "DISPATCHED"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"

class NodeTier(str, enum.Enum):
    LOW = "LOW"
    MID = "MID"
    HIGH = "HIGH"

class NodeHealth(str, enum.Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"

# SQLAlchemy Models
class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(Enum(JobType), nullable=False)
    payload = Column(JSON, nullable=False, default=dict)
    priority = Column(Integer, nullable=False, default=3)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.PENDING)
    assigned_node = Column(String, nullable=True) # Node UUID
    submitted_at = Column(DateTime(timezone=True), default=get_utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    latency_ms = Column(Integer, nullable=True)

class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    hostname = Column(String, nullable=False)
    tier = Column(Enum(NodeTier), nullable=False, default=NodeTier.MID)
    supported_types = Column(ARRAY(Enum(JobType)), nullable=False, default=list)
    cpu_util = Column(Float, nullable=False, default=0.0)
    mem_available_mb = Column(Integer, nullable=False, default=0)
    health = Column(Enum(NodeHealth), nullable=False, default=NodeHealth.HEALTHY)
    last_heartbeat = Column(DateTime(timezone=True), default=get_utc_now)
    success_rate = Column(Float, nullable=False, default=1.0)

# Pydantic Models for API
class NodeRegistration(BaseModel):
    hostname: str
    tier: NodeTier
    supported_types: List[JobType]
    cpu_util: float = Field(0.0, ge=0.0, le=1.0)
    mem_available_mb: int

class NodeHeartbeat(BaseModel):
    cpu_util: float = Field(..., ge=0.0, le=1.0)
    mem_available_mb: int

class NodeResponse(BaseModel):
    id: str
    hostname: str
    tier: NodeTier
    supported_types: List[JobType]
    cpu_util: float
    mem_available_mb: int
    health: NodeHealth
    last_heartbeat: datetime
    success_rate: float

    model_config = {'from_attributes': True}

class JobCreate(BaseModel):
    type: JobType
    payload: Dict[str, Any]
    priority: int = Field(3, ge=1, le=5)

class JobResponse(BaseModel):
    id: str
    type: JobType
    payload: Dict[str, Any]
    priority: int
    status: JobStatus
    assigned_node: Optional[str]
    submitted_at: datetime
    completed_at: Optional[datetime]
    latency_ms: Optional[int]

    model_config = {'from_attributes': True}
