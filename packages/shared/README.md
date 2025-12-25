# TruthNet Shared Package

Universal agent contracts and shared utilities for TruthNet.

## Installation

```bash
pip install -e .
```

## Usage

### Python Services

```python
from shared import (
    AgentRequest,
    AgentResponse,
    Signal,
    MediaType,
    AgentType,
    Status,
    DEFAULT_WEIGHTS
)

# Create a request
request = AgentRequest(
    request_id="uuid-here",
    media_path="/path/to/media",
    media_type=MediaType.VIDEO,
    agent_type=AgentType.VISUAL
)

# Create a response
response = AgentResponse(
    request_id=request.request_id,
    agent_type=AgentType.VISUAL,
    status=Status.SUCCESS,
    risk_score=0.75,
    signals=[
        Signal(
            signal_type="face_warp",
            confidence=0.82,
            description="Face warping artifacts detected in frames 45-67"
        )
    ]
)
```

### Go Services

```go
import "truthnet/api-go/contracts"

// Create a request
req := contracts.AgentRequest{
    RequestID: "uuid-here",
    MediaPath: "/path/to/media",
    MediaType: contracts.MediaTypeVideo,
    AgentType: contracts.AgentTypeVisual,
}

// Create a response
resp := contracts.AgentResponse{
    RequestID: req.RequestID,
    AgentType: contracts.AgentTypeVisual,
    Status:    contracts.StatusSuccess,
    RiskScore: 0.75,
    Signals: []contracts.Signal{
        {
            SignalType:  "face_warp",
            Confidence:  0.82,
            Description: "Face warping artifacts detected",
        },
    },
}
```

## Contract Schema

The JSON schema is available at `agent-contracts.schema.json` for validation purposes.

## Types

### Request/Response
- `AgentRequest` - Request to an agent
- `AgentResponse` - Response from an agent
- `OrchestratorResponse` - Final aggregated response

### Enums
- `MediaType`: video | image | audio
- `AgentType`: visual | metadata | audio | lipsync
- `Status`: success | partial | failed
- `Severity`: low | medium | high
- `Verdict`: AUTHENTIC | SUSPICIOUS | HIGH_RISK

### Data Models
- `Signal` - Detected anomaly/indicator
- `AgentError` - Error information
- `AgentWeights` - Consensus weights
