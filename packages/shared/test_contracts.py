"""
Test suite for TruthNet agent contracts
Run with: pytest test_contracts.py -v
"""
import pytest
from datetime import datetime
from contracts import (
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


class TestAgentRequest:
    """Test AgentRequest model"""
    
    def test_valid_request(self):
        """Test creating a valid agent request"""
        request = AgentRequest(
            request_id="550e8400-e29b-41d4-a716-446655440000",
            media_path="/tmp/media/test.mp4",
            media_type=MediaType.VIDEO,
            agent_type=AgentType.VISUAL,
            options={"extract_frames": True}
        )
        
        assert request.request_id == "550e8400-e29b-41d4-a716-446655440000"
        assert request.media_path == "/tmp/media/test.mp4"
        assert request.media_type == MediaType.VIDEO
        assert request.agent_type == AgentType.VISUAL
        assert request.options["extract_frames"] is True
    
    def test_request_json_serialization(self):
        """Test JSON serialization"""
        request = AgentRequest(
            request_id="test-123",
            media_path="/path/to/file.jpg",
            media_type=MediaType.IMAGE,
            agent_type=AgentType.METADATA
        )
        
        json_data = request.model_dump_json()
        assert "test-123" in json_data
        assert "image" in json_data
        assert "metadata" in json_data
    
    def test_request_missing_fields(self):
        """Test validation with missing required fields"""
        with pytest.raises(Exception):  # Pydantic validation error
            AgentRequest(
                request_id="test-123",
                media_path="/path/to/file.jpg"
                # Missing media_type and agent_type
            )


class TestSignal:
    """Test Signal model"""
    
    def test_valid_signal(self):
        """Test creating a valid signal"""
        signal = Signal(
            signal_type="face_warp",
            confidence=0.85,
            description="Face warping detected in frames 45-67",
            severity=Severity.HIGH,
            metadata={"frames": [45, 46, 47], "region": "lower_face"}
        )
        
        assert signal.signal_type == "face_warp"
        assert signal.confidence == 0.85
        assert signal.severity == Severity.HIGH
    
    def test_confidence_validation(self):
        """Test confidence must be between 0 and 1"""
        with pytest.raises(Exception):
            Signal(
                signal_type="test",
                confidence=1.5,  # Invalid: > 1.0
                description="Test"
            )
        
        with pytest.raises(Exception):
            Signal(
                signal_type="test",
                confidence=-0.5,  # Invalid: < 0.0
                description="Test"
            )


class TestAgentResponse:
    """Test AgentResponse model"""
    
    def test_successful_response(self):
        """Test creating a successful agent response"""
        response = AgentResponse(
            request_id="test-123",
            agent_type=AgentType.VISUAL,
            status=Status.SUCCESS,
            risk_score=0.75,
            signals=[
                Signal(
                    signal_type="face_warp",
                    confidence=0.82,
                    description="Face artifacts detected"
                )
            ],
            processing_time_ms=1250
        )
        
        assert response.status == Status.SUCCESS
        assert response.risk_score == 0.75
        assert len(response.signals) == 1
        assert response.processing_time_ms == 1250
    
    def test_failed_response_with_error(self):
        """Test creating a failed response with error details"""
        response = AgentResponse(
            request_id="test-456",
            agent_type=AgentType.METADATA,
            status=Status.FAILED,
            risk_score=0.0,
            signals=[],
            error=AgentError(
                code="FILE_NOT_FOUND",
                message="Media file does not exist",
                details={"path": "/invalid/path.mp4"}
            )
        )
        
        assert response.status == Status.FAILED
        assert response.error is not None
        assert response.error.code == "FILE_NOT_FOUND"


class TestOrchestratorResponse:
    """Test OrchestratorResponse model"""
    
    def test_complete_orchestrator_response(self):
        """Test creating a complete orchestrator response"""
        agent_responses = [
            AgentResponse(
                request_id="test-789",
                agent_type=AgentType.VISUAL,
                status=Status.SUCCESS,
                risk_score=0.80,
                signals=[
                    Signal(
                        signal_type="face_warp",
                        confidence=0.85,
                        description="Face warping detected"
                    )
                ]
            ),
            AgentResponse(
                request_id="test-789",
                agent_type=AgentType.METADATA,
                status=Status.SUCCESS,
                risk_score=0.65,
                signals=[
                    Signal(
                        signal_type="missing_exif",
                        confidence=0.70,
                        description="Camera metadata missing"
                    )
                ]
            )
        ]
        
        response = OrchestratorResponse(
            request_id="test-789",
            verdict=Verdict.HIGH_RISK,
            risk_score=0.74,  # Weighted average
            confidence=0.88,
            reasons=[
                "Face warping artifacts detected",
                "Missing camera metadata"
            ],
            agent_breakdown=agent_responses,
            processing_time_ms=2500
        )
        
        assert response.verdict == Verdict.HIGH_RISK
        assert response.risk_score == 0.74
        assert len(response.reasons) == 2
        assert len(response.agent_breakdown) == 2
    
    def test_orchestrator_json_output(self):
        """Test JSON serialization of orchestrator response"""
        response = OrchestratorResponse(
            request_id="test-999",
            verdict=Verdict.AUTHENTIC,
            risk_score=0.15,
            confidence=0.95,
            reasons=["No anomalies detected"],
            agent_breakdown=[]
        )
        
        json_str = response.model_dump_json()
        assert "AUTHENTIC" in json_str
        assert "0.15" in json_str


class TestAgentWeights:
    """Test AgentWeights model"""
    
    def test_default_weights(self):
        """Test default weights are correct"""
        assert DEFAULT_WEIGHTS.visual == 0.45
        assert DEFAULT_WEIGHTS.metadata == 0.55
        assert DEFAULT_WEIGHTS.audio == 0.30
        assert DEFAULT_WEIGHTS.lipsync == 0.00
    
    def test_custom_weights(self):
        """Test creating custom weights"""
        weights = AgentWeights(
            visual=0.50,
            metadata=0.50,
            audio=0.00,
            lipsync=0.00
        )
        
        assert weights.visual == 0.50
        assert weights.metadata == 0.50
    
    def test_weight_validation(self):
        """Test weight values must be between 0 and 1"""
        with pytest.raises(Exception):
            AgentWeights(
                visual=1.5,  # Invalid
                metadata=0.5,
                audio=0.0,
                lipsync=0.0
            )


class TestEnums:
    """Test enum types"""
    
    def test_media_types(self):
        """Test MediaType enum"""
        assert MediaType.VIDEO == "video"
        assert MediaType.IMAGE == "image"
        assert MediaType.AUDIO == "audio"
    
    def test_verdicts(self):
        """Test Verdict enum"""
        assert Verdict.AUTHENTIC == "AUTHENTIC"
        assert Verdict.SUSPICIOUS == "SUSPICIOUS"
        assert Verdict.HIGH_RISK == "HIGH_RISK"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
