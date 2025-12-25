# Windows Installation Guide

## Common Issues & Solutions

### ❌ Problem: dlib installation fails (cmake required)

**Error:**
```
ERROR: Failed building wheel for dlib
cmake is not installed or not in PATH
```

**Solution:** We've replaced `dlib` with `mediapipe` (no cmake needed!)

---

## Installing Python Dependencies

### Visual Agent
```powershell
cd services\visual-agent

# Create virtual environment
python -m venv venv

# Activate (PowerShell)
.\venv\Scripts\Activate.ps1

# If execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Metadata Agent
```powershell
cd services\metadata-agent
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Audio Agent (Optional)
```powershell
cd services\audio-agent
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Alternative: If MediaPipe Has Issues

### Option 1: Use OpenCV Only (No Face Detection)
```powershell
# Install only opencv
pip install opencv-python pillow numpy fastapi uvicorn
```

Then use basic image analysis without face detection.

### Option 2: Install Pre-built dlib (Advanced)
```powershell
# Install cmake first
winget install cmake

# Restart terminal, then:
pip install dlib
pip install face-recognition
```

---

## Verifying Installation

### Test Python Packages
```powershell
# In activated venv
python -c "import cv2; print('OpenCV:', cv2.__version__)"
python -c "import mediapipe; print('MediaPipe OK')"
python -c "import fastapi; print('FastAPI OK')"
```

### Test Go Installation
```powershell
cd apps\api-go
go version
go test ./contracts -v
```

---

## Quick Start (After Installation)

### 1. Start Visual Agent
```powershell
cd services\visual-agent
.\venv\Scripts\Activate.ps1
python -m src.main
# Should show: Uvicorn running on http://0.0.0.0:50051
```

### 2. Start Metadata Agent
```powershell
cd services\metadata-agent
.\venv\Scripts\Activate.ps1
python -m src.main
# Should show: Uvicorn running on http://0.0.0.0:50052
```

### 3. Start Go API
```powershell
cd apps\api-go
go run main.go
# Should show: Listening on :8080
```

---

## Troubleshooting

### PowerShell Execution Policy
```powershell
# If you can't activate venv:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use
```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Python Not Found
```powershell
# Install Python 3.10+
winget install Python.Python.3.11

# Verify
python --version
```

### Go Not Found
```powershell
# Install Go 1.21+
winget install GoLang.Go

# Verify
go version
```

---

## Package Versions (Tested on Windows)

- Python: 3.10+ or 3.11
- Go: 1.21+
- Node.js: 18+ (for frontend)
- pnpm: 8+

All Python packages use versions without cmake dependencies.
