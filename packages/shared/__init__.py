"""
TruthNet Shared Package
Agent contracts and utilities
"""

__version__ = "1.0.0"

from .contracts import (
    AgentRequest,
    AgentResponse,
    Signal,
    AgentError,
    OrchestratorResponse,
    AgentWeights,
    DEFAULT_WEIGHTS,
    MediaType,
    AgentType,
    Status,
    Severity,
    Verdict,
)

__all__ = [
    "AgentRequest",
    "AgentResponse",
    "Signal",
    "AgentError",
    "OrchestratorResponse",
    "AgentWeights",
    "DEFAULT_WEIGHTS",
    "MediaType",
    "AgentType",
    "Status",
    "Severity",
    "Verdict",
]
