"""
TruthNet Agent Contracts
Universal interface definitions for all agents
"""
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


class MediaType(str, Enum):
    """Media type enumeration"""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"


class AgentType(str, Enum):
    """Agent type enumeration"""
    VISUAL = "visual"
    METADATA = "metadata"
    AUDIO = "audio"
    LIPSYNC = "lipsync"


class Status(str, Enum):
    """Analysis status enumeration"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


class Severity(str, Enum):
    """Signal severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Verdict(str, Enum):
    """Final verdict enumeration"""
    AUTHENTIC = "AUTHENTIC"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"


class AgentRequest(BaseModel):
    """Request payload sent to an agent"""
    request_id: str = Field(..., description="Unique identifier for this analysis request")
    media_path: str = Field(..., description="Absolute path to the media file to analyze")
    media_type: MediaType = Field(..., description="Type of media being analyzed")
    agent_type: AgentType = Field(..., description="Agent performing the analysis")
    options: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Agent-specific configuration")

    class Config:
        use_enum_values = True


class Signal(BaseModel):
    """Detected anomaly or indicator"""
    signal_type: str = Field(..., description="Type of signal detected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0.0 to 1.0)")
    description: str = Field(..., description="Human-readable description")
    severity: Optional[Severity] = Field(None, description="Severity of the signal")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")

    class Config:
        use_enum_values = True


class AgentError(BaseModel):
    """Error information from an agent"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional error details")


class AgentResponse(BaseModel):
    """Response payload from an agent"""
    request_id: str = Field(..., description="Matching request ID")
    agent_type: AgentType = Field(..., description="Agent that performed the analysis")
    status: Status = Field(..., description="Analysis completion status")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk assessment (0.0 = authentic, 1.0 = high risk)")
    signals: List[Signal] = Field(..., description="List of detected signals/anomalies")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    error: Optional[AgentError] = Field(None, description="Error information if status is 'failed'")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Agent-specific output metadata")

    class Config:
        use_enum_values = True


class OrchestratorResponse(BaseModel):
    """Final aggregated response from the orchestrator"""
    request_id: str = Field(..., description="Request identifier")
    verdict: Verdict = Field(..., description="Final verdict on the media")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Weighted aggregate risk score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the verdict")
    reasons: List[str] = Field(..., description="Top reasons for the verdict")
    agent_breakdown: List[AgentResponse] = Field(..., description="Individual agent responses")
    processing_time_ms: Optional[int] = Field(None, description="Total processing time")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")

    class Config:
        use_enum_values = True


class AgentWeights(BaseModel):
    """Weights for each agent in consensus calculation"""
    visual: float = Field(0.45, ge=0.0, le=1.0)
    metadata: float = Field(0.55, ge=0.0, le=1.0)
    audio: float = Field(0.30, ge=0.0, le=1.0)
    lipsync: float = Field(0.00, ge=0.0, le=1.0)

    @validator('visual', 'metadata', 'audio', 'lipsync')
    def validate_weight(cls, v):
        """Ensure weights are between 0 and 1"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Weight must be between 0.0 and 1.0')
        return v


# Default weights for MVP
DEFAULT_WEIGHTS = AgentWeights(
    visual=0.45,
    metadata=0.55,
    audio=0.30,
    lipsync=0.00
)
