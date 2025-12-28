"""
Metadata Agent Main Server
FastAPI server for metadata analysis
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
from shared.contracts import (
    AgentRequest,
    AgentResponse,
    Signal,
    AgentType,
    Status,
    Severity,
    MediaType
)
from analyzer import MetadataAnalyzer

app = FastAPI(title="TruthNet Metadata Agent")

# Enable CORS for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = MetadataAnalyzer()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "TruthNet Metadata Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "agent_type": "metadata"}


@app.post("/analyze", response_model=AgentResponse)
async def analyze(request: AgentRequest) -> AgentResponse:
    """
    Analyze media file metadata for manipulation indicators
    
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
                agent_type=AgentType.METADATA,
                status=Status.FAILED,
                risk_score=0.0,
                signals=[],
                error={
                    "code": "FILE_NOT_FOUND",
                    "message": f"Media file not found: {request.media_path}"
                }
            )
        
        # Analyze based on media type
        if request.media_type == MediaType.IMAGE:
            result = analyzer.analyze_image(request.media_path)
        elif request.media_type == MediaType.VIDEO:
            result = analyzer.analyze_video(request.media_path)
        else:
            return AgentResponse(
                request_id=request.request_id,
                agent_type=AgentType.METADATA,
                status=Status.FAILED,
                risk_score=0.0,
                signals=[],
                error={
                    "code": "UNSUPPORTED_MEDIA_TYPE",
                    "message": f"Unsupported media type: {request.media_type}"
                }
            )
        
        # Convert signals to proper Signal objects
        signals = []
        for sig in result.get("signals", []):
            signals.append(Signal(
                signal_type=sig["type"],
                confidence=sig["confidence"],
                description=sig["description"],
                severity=Severity.HIGH if sig["confidence"] > 0.7 else 
                         Severity.MEDIUM if sig["confidence"] > 0.4 else Severity.LOW
            ))
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        return AgentResponse(
            request_id=request.request_id,
            agent_type=AgentType.METADATA,
            status=Status.SUCCESS,
            risk_score=result["risk_score"],
            signals=signals,
            processing_time_ms=processing_time,
            metadata=result.get("metadata", {})
        )
    
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        
        return AgentResponse(
            request_id=request.request_id,
            agent_type=AgentType.METADATA,
            status=Status.FAILED,
            risk_score=0.0,
            signals=[],
            processing_time_ms=processing_time,
            error={
                "code": "ANALYSIS_ERROR",
                "message": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8002"))
    
    print(f"🔍 Starting Metadata Agent on port {port}")
    print(f"📊 Analyzer: EXIF & File Metadata Analysis")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
