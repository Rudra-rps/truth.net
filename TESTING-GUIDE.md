# TruthNet Testing & Development Guide

## 🧪 Testing the Contracts

### Python Tests

```bash
# Navigate to shared package
cd packages/shared

# Install dependencies
pip install -r requirements.txt
pip install pytest

# Run tests
pytest test_contracts.py -v

# Run with coverage
pytest test_contracts.py -v --cov=contracts --cov-report=html
```

**Expected Output:**
```
test_contracts.py::TestAgentRequest::test_valid_request PASSED
test_contracts.py::TestAgentRequest::test_request_json_serialization PASSED
test_contracts.py::TestSignal::test_valid_signal PASSED
test_contracts.py::TestAgentResponse::test_successful_response PASSED
...
```

### Go Tests

```bash
# Navigate to api-go
cd apps/api-go

# Run tests
go test ./contracts -v

# Run with coverage
go test ./contracts -cover -coverprofile=coverage.out
go tool cover -html=coverage.out
```

**Expected Output:**
```
=== RUN   TestAgentRequest
=== RUN   TestAgentRequest/Valid_Request
=== RUN   TestAgentRequest/JSON_Serialization
--- PASS: TestAgentRequest (0.00s)
...
PASS
```

---

## 🏗️ What You Need to Build Next

### Phase 2: Media Ingestion Pipeline

#### 1. **Go API Server** (apps/api-go/)

**File:** `apps/api-go/main.go`
```go
package main

import (
    "github.com/gin-gonic/gin"
    "truthnet/api-go/handlers"
)

func main() {
    router := gin.Default()
    
    // Health check
    router.GET("/health", handlers.HealthCheck)
    
    // Upload & analyze endpoint
    router.POST("/api/v1/analyze", handlers.AnalyzeMedia)
    
    // Get analysis result
    router.GET("/api/v1/results/:request_id", handlers.GetResult)
    
    router.Run(":8080")
}
```

**File:** `apps/api-go/handlers/analyze.go`
```go
package handlers

import (
    "github.com/gin-gonic/gin"
    "github.com/google/uuid"
    "truthnet/api-go/contracts"
)

func AnalyzeMedia(c *gin.Context) {
    // 1. Accept file upload
    file, _ := c.FormFile("file")
    
    // 2. Generate request ID
    requestID := uuid.New().String()
    
    // 3. Save to /tmp/media/{uuid}
    mediaPath := fmt.Sprintf("/tmp/media/%s/%s", requestID, file.Filename)
    c.SaveUploadedFile(file, mediaPath)
    
    // 4. Determine media type
    mediaType := detectMediaType(file.Filename)
    
    // 5. Call orchestrator
    result := orchestrate(requestID, mediaPath, mediaType)
    
    c.JSON(200, result)
}
```

**Dependencies needed:**
```bash
cd apps/api-go
go mod init truthnet/api-go
go get github.com/gin-gonic/gin
go get github.com/google/uuid
```

#### 2. **Python Visual Agent** (services/visual-agent/)

**File:** `services/visual-agent/src/main.py`
```python
from fastapi import FastAPI
from shared import AgentRequest, AgentResponse, Signal, Status, AgentType

app = FastAPI()

@app.post("/analyze")
async def analyze(request: AgentRequest) -> AgentResponse:
    """Analyze media for visual anomalies"""
    
    # 1. Load media file
    media = load_media(request.media_path)
    
    # 2. Extract frames (if video)
    frames = extract_frames(media) if request.media_type == "video" else [media]
    
    # 3. Run face detection
    faces = detect_faces(frames)
    
    # 4. Check for artifacts
    signals = []
    risk_score = 0.0
    
    # Example: Face warping check
    if has_face_warping(faces):
        signals.append(Signal(
            signal_type="face_warp",
            confidence=0.85,
            description="Face warping artifacts detected"
        ))
        risk_score += 0.4
    
    # 5. Return response
    return AgentResponse(
        request_id=request.request_id,
        agent_type=AgentType.VISUAL,
        status=Status.SUCCESS,
        risk_score=min(risk_score, 1.0),
        signals=signals
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=50051)
```

**Dependencies:**
```bash
cd services/visual-agent
pip install fastapi uvicorn opencv-python pillow face-recognition numpy
```

#### 3. **Python Metadata Agent** (services/metadata-agent/)

**File:** `services/metadata-agent/src/main.py`
```python
from fastapi import FastAPI
from PIL import Image
from shared import AgentRequest, AgentResponse, Signal, Status, AgentType

app = FastAPI()

@app.post("/analyze")
async def analyze(request: AgentRequest) -> AgentResponse:
    """Analyze metadata for anomalies"""
    
    signals = []
    risk_score = 0.0
    
    # 1. Extract EXIF data
    exif = extract_exif(request.media_path)
    
    # 2. Check for missing camera metadata
    if not exif.get("Make") or not exif.get("Model"):
        signals.append(Signal(
            signal_type="missing_camera_metadata",
            confidence=0.70,
            description="Camera information is missing"
        ))
        risk_score += 0.3
    
    # 3. Check for software manipulation
    if exif.get("Software"):
        signals.append(Signal(
            signal_type="editing_software_detected",
            confidence=0.60,
            description=f"Edited with: {exif.get('Software')}"
        ))
        risk_score += 0.2
    
    # 4. Timestamp validation
    if not validate_timestamp(exif):
        signals.append(Signal(
            signal_type="invalid_timestamp",
            confidence=0.75,
            description="Timestamp inconsistencies detected"
        ))
        risk_score += 0.25
    
    return AgentResponse(
        request_id=request.request_id,
        agent_type=AgentType.METADATA,
        status=Status.SUCCESS,
        risk_score=min(risk_score, 1.0),
        signals=signals
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=50052)
```

**Dependencies:**
```bash
cd services/metadata-agent
pip install fastapi uvicorn pillow exifread
```

#### 4. **Orchestrator** (apps/api-go/orchestrator/)

**File:** `apps/api-go/orchestrator/orchestrator.go`
```go
package orchestrator

import (
    "sync"
    "time"
    "truthnet/api-go/contracts"
)

type Orchestrator struct {
    VisualAgentURL   string
    MetadataAgentURL string
    Weights          contracts.AgentWeights
}

func (o *Orchestrator) Orchestrate(requestID, mediaPath string, mediaType contracts.MediaType) contracts.OrchestratorResponse {
    start := time.Now()
    
    // Create requests for each agent
    request := contracts.AgentRequest{
        RequestID: requestID,
        MediaPath: mediaPath,
        MediaType: mediaType,
    }
    
    // Fan-out: Call agents in parallel
    var wg sync.WaitGroup
    results := make(chan contracts.AgentResponse, 2)
    
    wg.Add(2)
    go o.callAgent(request, contracts.AgentTypeVisual, &wg, results)
    go o.callAgent(request, contracts.AgentTypeMetadata, &wg, results)
    
    // Wait for all agents
    wg.Wait()
    close(results)
    
    // Fan-in: Collect results
    var agentResponses []contracts.AgentResponse
    for resp := range results {
        agentResponses = append(agentResponses, resp)
    }
    
    // Calculate weighted risk score
    riskScore := o.calculateRiskScore(agentResponses)
    verdict := o.determineVerdict(riskScore)
    reasons := o.extractReasons(agentResponses)
    
    return contracts.OrchestratorResponse{
        RequestID:        requestID,
        Verdict:          verdict,
        RiskScore:        riskScore,
        Confidence:       0.85,
        Reasons:          reasons,
        AgentBreakdown:   agentResponses,
        ProcessingTimeMs: time.Since(start).Milliseconds(),
        Timestamp:        time.Now(),
    }
}

func (o *Orchestrator) calculateRiskScore(responses []contracts.AgentResponse) float64 {
    score := 0.0
    totalWeight := 0.0
    
    for _, resp := range responses {
        weight := o.getWeight(resp.AgentType)
        score += resp.RiskScore * weight
        totalWeight += weight
    }
    
    return score / totalWeight
}

func (o *Orchestrator) determineVerdict(riskScore float64) contracts.Verdict {
    if riskScore < 0.3 {
        return contracts.VerdictAuthentic
    } else if riskScore < 0.7 {
        return contracts.VerdictSuspicious
    }
    return contracts.VerdictHighRisk
}
```

---

## 📋 API Endpoints You'll Need

### 1. **POST /api/v1/analyze**
Upload and analyze media

**Request:**
```bash
curl -X POST http://localhost:8080/api/v1/analyze \
  -F "file=@/path/to/video.mp4"
```

**Response:**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "verdict": "HIGH_RISK",
  "risk_score": 0.74,
  "confidence": 0.88,
  "reasons": [
    "Face warping artifacts detected",
    "Missing camera metadata"
  ],
  "agent_breakdown": [...]
}
```

### 2. **GET /api/v1/results/:request_id**
Get analysis results

### 3. **GET /health**
Health check endpoint

### 4. **GET /agents/status**
Check agent availability

---

## 🚀 Quick Start Development

### 1. Start Visual Agent
```bash
cd services/visual-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/main.py
# Runs on http://localhost:50051
```

### 2. Start Metadata Agent
```bash
cd services/metadata-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
# Runs on http://localhost:50052
```

### 3. Start Go API
```bash
cd apps/api-go
go run main.go
# Runs on http://localhost:8080
```

### 4. Test End-to-End
```bash
curl -X POST http://localhost:8080/api/v1/analyze \
  -F "file=@test_video.mp4"
```

---

## 🔍 Next Steps (In Order)

1. ✅ **Contracts Done** - You have stable contracts
2. 🔨 **Build Go API Server** - Create upload endpoint
3. 🔨 **Build Visual Agent** - Face detection & artifacts
4. 🔨 **Build Metadata Agent** - EXIF parsing
5. 🔨 **Build Orchestrator** - Parallel execution & consensus
6. 🔨 **Build Frontend** - Upload UI & results display
7. 🎯 **Demo Prep** - Curate test samples

---

## 📦 Required Dependencies Summary

### Go (apps/api-go/)
```bash
go get github.com/gin-gonic/gin
go get github.com/google/uuid
```

### Python Services
```bash
# Visual Agent
pip install fastapi uvicorn opencv-python pillow face-recognition numpy

# Metadata Agent
pip install fastapi uvicorn pillow exifread

# Shared
pip install pydantic python-dateutil
```

### Frontend (apps/frontend/)
```bash
pnpm add next react react-dom
pnpm add -D typescript @types/react @types/node
```

---

## 🧪 Testing Workflow

1. **Unit Tests** - Test contracts (Done ✅)
2. **Integration Tests** - Test agent APIs
3. **E2E Tests** - Test full pipeline
4. **Demo Tests** - Test with real samples

Let me know when you're ready to build Phase 2!
