"""
Visual Agent Main Server
FastAPI server for visual deepfake detection
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from shared import (
    AgentRequest,
    AgentResponse,
    Signal,
    AgentType,
    Status,
    Severity
)
from analyzer import VisualAnalyzer

app = FastAPI(title="TruthNet Visual Agent")

# Enable CORS for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = VisualAnalyzer()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "TruthNet Visual Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "agent_type": "visual"}


@app.post("/analyze", response_model=AgentResponse)
async def analyze(request: AgentRequest) -> AgentResponse:
    """
    Analyze media for visual deepfake artifacts
    
    Args:
        request: AgentRequest with media path and type
        
    Returns:
        AgentResponse with risk score and detected signals
    """
    start_time = time.time()
    
    try:
        # Validate media file exists
        if not os.path.exists(request.media_path):
            return AgentResponse(
                request_id=request.request_id,
                agent_type=AgentType.VISUAL,
                status=Status.FAILED,
                risk_score=0.0,
                signals=[],
                error={
                    "code": "FILE_NOT_FOUND",
                    "message": f"Media file not found: {request.media_path}"
                }
            )
        
        # Analyze based on media type
        if request.media_type == "video":
            result = analyzer.analyze_video(request.media_path)
        elif request.media_type == "image":
            result = analyzer.analyze_image(request.media_path)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported media type: {request.media_type}"
            )
        
        # Convert artifacts to signals
        signals = []
        for artifact in result.get("artifacts", []):
            severity = Severity.HIGH if artifact["confidence"] > 0.7 else \
                      Severity.MEDIUM if artifact["confidence"] > 0.4 else \
                      Severity.LOW
            
            signals.append(Signal(
                signal_type=artifact["type"],
                confidence=artifact["confidence"],
                description=artifact["description"],
                severity=severity,
                metadata={
                    "faces_detected": result.get("faces_detected", 0),
                    "analyzed_frames": result.get("analyzed_frames", 1)
                }
            ))
        
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Return response
        return AgentResponse(
            request_id=request.request_id,
            agent_type=AgentType.VISUAL,
            status=Status.SUCCESS,
            risk_score=result["risk_score"],
            signals=signals,
            processing_time_ms=processing_time_ms,
            metadata={
                "faces_detected": result.get("faces_detected", 0),
                "total_frames": result.get("total_frames", 1),
                "analyzed_frames": result.get("analyzed_frames", 1)
            }
        )
        
    except Exception as e:
        # Handle unexpected errors
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return AgentResponse(
            request_id=request.request_id,
            agent_type=AgentType.VISUAL,
            status=Status.FAILED,
            risk_score=0.0,
            signals=[],
            processing_time_ms=processing_time_ms,
            error={
                "code": "ANALYSIS_ERROR",
                "message": str(e)
            }
        )


@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown"""
    analyzer.cleanup()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=50051,
        log_level="info"
    )
