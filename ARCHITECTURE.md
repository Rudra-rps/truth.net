# TruthNet Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    (Next.js - Port 3000)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐ │
│  │  Upload  │  │ Progress │  │   Results Dashboard      │ │
│  │   UI     │  │   Bar    │  │  • Verdict Badge         │ │
│  └──────────┘  └──────────┘  │  • Risk Score Gauge      │ │
│                               │  • Agent Breakdown       │ │
│                               │  • Explanation Panel     │ │
│                               └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP/JSON
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Go API Server                          │
│                    (Gin - Port 8080)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              HTTP Handlers                            │  │
│  │  • POST /api/v1/analyze (file upload)               │  │
│  │  • GET  /api/v1/results/:id                         │  │
│  │  • GET  /health                                      │  │
│  │  • GET  /agents/status                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Media Processing Pipeline                    │  │
│  │  1. Save file to /tmp/media/{uuid}/                  │  │
│  │  2. Extract frames (FFmpeg)                          │  │
│  │  3. Extract audio track                              │  │
│  │  4. Extract metadata                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                              │                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               Orchestrator                            │  │
│  │  • Fan-out to agents (sync.WaitGroup)               │  │
│  │  • Parallel execution (timeout: 30s)                │  │
│  │  • Fan-in results collection                        │  │
│  │  • Weighted consensus engine                        │  │
│  │  • Verdict determination logic                      │  │
│  │  • Explainability generator                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │                              │
          │ HTTP/JSON                    │ HTTP/JSON
          │ POST /analyze                │ POST /analyze
          ▼                              ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│    Visual Agent          │   │   Metadata Agent         │
│  (Python - Port 50051)   │   │  (Python - Port 50052)   │
├──────────────────────────┤   ├──────────────────────────┤
│ • Face Detection         │   │ • EXIF Extraction        │
│ • Frame Sampling         │   │ • Encoding Analysis      │
│ • Artifact Detection     │   │ • Timestamp Validation   │
│   - Face warping         │   │ • Software Detection     │
│   - Blending artifacts   │   │ • Provenance Check       │
│   - Edge inconsistencies │   │ • GPS Validation         │
│ • Texture Analysis       │   │                          │
│                          │   │                          │
│ Weight: 45%              │   │ Weight: 55%              │
└──────────────────────────┘   └──────────────────────────┘
```

---

## Data Flow

### 1. Upload & Ingestion
```
User → Frontend → POST /api/v1/analyze
                    ↓
                File Saved: /tmp/media/{uuid}/original.mp4
                    ↓
                FFmpeg Processing
                    ↓
           ┌────────┴────────┐
           ↓                 ↓
    frames/           audio/
    001.jpg           track.mp3
    002.jpg
    ...
```

### 2. Agent Orchestration
```
Orchestrator creates AgentRequest
    ↓
┌───┴────┬─────────────┐
│        │             │
↓        ↓             ↓
Visual   Metadata   (Audio - Future)
Agent    Agent       Agent
    ↓        ↓             ↓
AgentResponse × 2 (or 3)
    ↓
Consensus Engine
    ↓
OrchestratorResponse
    ↓
Frontend Display
```

### 3. Consensus Calculation
```python
weighted_risk_score = (
    visual_score * 0.45 +
    metadata_score * 0.55
)

if weighted_risk_score < 0.3:
    verdict = "AUTHENTIC"
elif weighted_risk_score < 0.7:
    verdict = "SUSPICIOUS"
else:
    verdict = "HIGH_RISK"
```

---

## API Contract Flow

### 1. Frontend → API
```http
POST /api/v1/analyze
Content-Type: multipart/form-data

file: [binary]
```

### 2. API → Agents
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "media_path": "/tmp/media/550e8400.../video.mp4",
  "media_type": "video",
  "agent_type": "visual",
  "options": {}
}
```

### 3. Agent → API
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_type": "visual",
  "status": "success",
  "risk_score": 0.82,
  "signals": [
    {
      "signal_type": "face_warp",
      "confidence": 0.85,
      "description": "Face warping artifacts detected in frames 45-67",
      "severity": "high"
    }
  ],
  "processing_time_ms": 1250
}
```

### 4. API → Frontend
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
  "agent_breakdown": [...],
  "processing_time_ms": 2500,
  "timestamp": "2025-12-25T10:30:00Z"
}
```

---

## Component Responsibilities

### Go API Server
- **File handling** - Accept uploads, save to disk
- **Media preprocessing** - FFmpeg extraction
- **Orchestration** - Coordinate agents
- **Consensus** - Calculate weighted scores
- **Verdict logic** - Determine final classification
- **Response formatting** - Build API responses

### Visual Agent (Python)
- **Face detection** - Detect faces in frames
- **Artifact analysis** - Find manipulation signs
- **Frame sampling** - Extract key frames
- **Feature extraction** - Detect visual anomalies
- **Signal generation** - Report findings

### Metadata Agent (Python)
- **EXIF parsing** - Extract image metadata
- **Encoding analysis** - Check compression history
- **Timestamp validation** - Verify time consistency
- **Software detection** - Identify editing tools
- **Provenance checks** - Validate authenticity markers

### Frontend (Next.js)
- **Upload interface** - Drag & drop UI
- **Progress tracking** - Real-time status
- **Results display** - Verdict visualization
- **Agent breakdown** - Individual agent views
- **Explanation panel** - Human-readable reasons

---

## Error Handling Strategy

### Partial Agent Failure
```
Visual Agent: ✅ Success (risk: 0.80)
Metadata Agent: ❌ Failed (timeout)
    ↓
Use only Visual Agent result
Reduce confidence score
Still provide verdict
```

### Complete Failure
```
All agents failed
    ↓
Return HTTP 503
Error message: "Analysis service unavailable"
Retry logic on frontend
```

### Invalid Input
```
File too large / Invalid format
    ↓
Return HTTP 400
Error message: "Unsupported file format"
```

---

## Deployment Architecture

### Development (Current)
```
localhost:3000  → Frontend
localhost:8080  → Go API
localhost:50051 → Visual Agent
localhost:50052 → Metadata Agent
```

### Docker Compose (Future)
```yaml
services:
  api:       # Go API (port 8080)
  frontend:  # Next.js (port 3000)
  visual:    # Python (port 50051)
  metadata:  # Python (port 50052)
  
networks:
  truthnet-network
```

### Production (Future)
```
Cloud Load Balancer
    ↓
API Gateway (Authentication)
    ↓
┌─────┬─────┬──────────┐
│     │     │          │
API × 3   Agents × 5   Frontend CDN
(k8s)     (k8s)        (Vercel/S3)
```

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Upload | < 2s | 100MB video |
| Agent processing | < 10s per agent | Visual: 8s, Metadata: 2s |
| Total analysis | < 15s | Including orchestration |
| Frontend render | < 1s | Results display |

---

## Security Considerations

### MVP (Current)
- No authentication
- Local file storage
- No encryption

### Future
- API key authentication
- JWT tokens
- Encrypted storage
- Rate limiting
- Input validation
- File size limits
- Format whitelisting

---

## Monitoring & Observability

### Health Checks
```
GET /health → API alive?
GET /agents/status → Agents reachable?
```

### Metrics (Future)
- Request latency
- Agent response times
- Error rates
- Verdict distribution
- User uploads/day

---

## File Structure Mapping

```
truthnet/
├── apps/
│   ├── api-go/
│   │   ├── main.go              # Entry point
│   │   ├── contracts/           # Type definitions
│   │   ├── handlers/            # HTTP handlers
│   │   ├── orchestrator/        # Agent coordination
│   │   ├── preprocessing/       # FFmpeg, frame extraction
│   │   └── consensus/           # Risk scoring logic
│   │
│   └── frontend/
│       ├── app/                 # Next.js app router
│       ├── components/          # UI components
│       └── lib/                 # API client
│
├── services/
│   ├── visual-agent/
│   │   ├── src/
│   │   │   ├── main.py         # FastAPI server
│   │   │   ├── detection.py    # Face detection
│   │   │   ├── artifacts.py    # Artifact detection
│   │   │   └── models/         # ML models
│   │   └── requirements.txt
│   │
│   └── metadata-agent/
│       ├── src/
│       │   ├── main.py         # FastAPI server
│       │   ├── exif.py         # EXIF parsing
│       │   └── validation.py   # Timestamp checks
│       └── requirements.txt
│
└── packages/
    └── shared/
        ├── contracts.py         # Python contracts
        └── agent-contracts.schema.json
```

---

## Next Implementation Steps

1. **Go API Server** - Handlers & orchestration
2. **Visual Agent** - Face detection & artifacts
3. **Metadata Agent** - EXIF & validation
4. **Consensus Engine** - Weighted scoring
5. **Frontend** - Upload & results UI
6. **Integration Tests** - End-to-end flow
7. **Demo Samples** - Test videos
8. **Documentation** - API docs & README

---

Ready to build Phase 2? Start with the Go API server!
