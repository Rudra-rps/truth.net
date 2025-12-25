# Visual Agent

Python service for visual deepfake detection using computer vision.

## Features

- Face detection using MediaPipe (no cmake required!)
- Blur detection
- Edge artifact detection
- Color inconsistency analysis
- Video frame sampling

## Installation

### Windows
```powershell
cd services\visual-agent
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Linux/Mac
```bash
cd services/visual-agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
python -m src.main
```

Service runs on: http://localhost:50051

## API Endpoints

### POST /analyze
Analyze media for visual artifacts

**Request:**
```json
{
  "request_id": "uuid",
  "media_path": "/path/to/media.mp4",
  "media_type": "video",
  "agent_type": "visual"
}
```

**Response:**
```json
{
  "request_id": "uuid",
  "agent_type": "visual",
  "status": "success",
  "risk_score": 0.75,
  "signals": [
    {
      "signal_type": "face_blur",
      "confidence": 0.82,
      "description": "Unusual blur detected in face region",
      "severity": "high"
    }
  ],
  "processing_time_ms": 1250
}
```

### GET /health
Health check

## Detection Methods

1. **Face Detection** - MediaPipe face detection
2. **Blur Analysis** - Laplacian variance
3. **Edge Artifacts** - Canny edge detection
4. **Color Artifacts** - HSV analysis

## Testing

```bash
pytest tests/
```
