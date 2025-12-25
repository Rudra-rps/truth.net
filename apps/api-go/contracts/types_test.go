package contracts

import (
	"encoding/json"
	"testing"
	"time"
)

func TestAgentRequest(t *testing.T) {
	t.Run("Valid Request", func(t *testing.T) {
		req := AgentRequest{
			RequestID: "550e8400-e29b-41d4-a716-446655440000",
			MediaPath: "/tmp/media/test.mp4",
			MediaType: MediaTypeVideo,
			AgentType: AgentTypeVisual,
			Options: map[string]interface{}{
				"extract_frames": true,
			},
		}

		if req.RequestID != "550e8400-e29b-41d4-a716-446655440000" {
			t.Errorf("Expected request_id to match")
		}
		if req.MediaType != MediaTypeVideo {
			t.Errorf("Expected MediaType to be video")
		}
	})

	t.Run("JSON Serialization", func(t *testing.T) {
		req := AgentRequest{
			RequestID: "test-123",
			MediaPath: "/path/to/file.jpg",
			MediaType: MediaTypeImage,
			AgentType: AgentTypeMetadata,
		}

		jsonData, err := json.Marshal(req)
		if err != nil {
			t.Fatalf("Failed to marshal request: %v", err)
		}

		var decoded AgentRequest
		err = json.Unmarshal(jsonData, &decoded)
		if err != nil {
			t.Fatalf("Failed to unmarshal request: %v", err)
		}

		if decoded.RequestID != req.RequestID {
			t.Errorf("RequestID mismatch after JSON round-trip")
		}
	})
}

func TestSignal(t *testing.T) {
	t.Run("Valid Signal", func(t *testing.T) {
		signal := Signal{
			SignalType:  "face_warp",
			Confidence:  0.85,
			Description: "Face warping detected in frames 45-67",
			Severity:    SeverityHigh,
			Metadata: map[string]interface{}{
				"frames": []int{45, 46, 47},
				"region": "lower_face",
			},
		}

		if signal.SignalType != "face_warp" {
			t.Errorf("Expected signal_type to be face_warp")
		}
		if signal.Confidence != 0.85 {
			t.Errorf("Expected confidence to be 0.85")
		}
		if signal.Severity != SeverityHigh {
			t.Errorf("Expected severity to be high")
		}
	})
}

func TestAgentResponse(t *testing.T) {
	t.Run("Successful Response", func(t *testing.T) {
		response := AgentResponse{
			RequestID: "test-123",
			AgentType: AgentTypeVisual,
			Status:    StatusSuccess,
			RiskScore: 0.75,
			Signals: []Signal{
				{
					SignalType:  "face_warp",
					Confidence:  0.82,
					Description: "Face artifacts detected",
				},
			},
			ProcessingTimeMs: 1250,
		}

		if response.Status != StatusSuccess {
			t.Errorf("Expected status to be success")
		}
		if response.RiskScore != 0.75 {
			t.Errorf("Expected risk_score to be 0.75")
		}
		if len(response.Signals) != 1 {
			t.Errorf("Expected 1 signal")
		}
	})

	t.Run("Failed Response with Error", func(t *testing.T) {
		response := AgentResponse{
			RequestID: "test-456",
			AgentType: AgentTypeMetadata,
			Status:    StatusFailed,
			RiskScore: 0.0,
			Signals:   []Signal{},
			Error: &AgentError{
				Code:    "FILE_NOT_FOUND",
				Message: "Media file does not exist",
				Details: map[string]interface{}{
					"path": "/invalid/path.mp4",
				},
			},
		}

		if response.Status != StatusFailed {
			t.Errorf("Expected status to be failed")
		}
		if response.Error == nil {
			t.Errorf("Expected error to be present")
		}
		if response.Error.Code != "FILE_NOT_FOUND" {
			t.Errorf("Expected error code to be FILE_NOT_FOUND")
		}
	})

	t.Run("JSON Serialization", func(t *testing.T) {
		response := AgentResponse{
			RequestID: "test-789",
			AgentType: AgentTypeVisual,
			Status:    StatusSuccess,
			RiskScore: 0.80,
			Signals: []Signal{
				{
					SignalType:  "face_warp",
					Confidence:  0.85,
					Description: "Face warping detected",
				},
			},
		}

		jsonData, err := json.Marshal(response)
		if err != nil {
			t.Fatalf("Failed to marshal response: %v", err)
		}

		var decoded AgentResponse
		err = json.Unmarshal(jsonData, &decoded)
		if err != nil {
			t.Fatalf("Failed to unmarshal response: %v", err)
		}

		if decoded.RiskScore != response.RiskScore {
			t.Errorf("RiskScore mismatch after JSON round-trip")
		}
	})
}

func TestOrchestratorResponse(t *testing.T) {
	t.Run("Complete Orchestrator Response", func(t *testing.T) {
		agentResponses := []AgentResponse{
			{
				RequestID: "test-789",
				AgentType: AgentTypeVisual,
				Status:    StatusSuccess,
				RiskScore: 0.80,
				Signals: []Signal{
					{
						SignalType:  "face_warp",
						Confidence:  0.85,
						Description: "Face warping detected",
					},
				},
			},
			{
				RequestID: "test-789",
				AgentType: AgentTypeMetadata,
				Status:    StatusSuccess,
				RiskScore: 0.65,
				Signals: []Signal{
					{
						SignalType:  "missing_exif",
						Confidence:  0.70,
						Description: "Camera metadata missing",
					},
				},
			},
		}

		response := OrchestratorResponse{
			RequestID:  "test-789",
			Verdict:    VerdictHighRisk,
			RiskScore:  0.74,
			Confidence: 0.88,
			Reasons: []string{
				"Face warping artifacts detected",
				"Missing camera metadata",
			},
			AgentBreakdown:   agentResponses,
			ProcessingTimeMs: 2500,
			Timestamp:        time.Now(),
		}

		if response.Verdict != VerdictHighRisk {
			t.Errorf("Expected verdict to be HIGH_RISK")
		}
		if response.RiskScore != 0.74 {
			t.Errorf("Expected risk_score to be 0.74")
		}
		if len(response.Reasons) != 2 {
			t.Errorf("Expected 2 reasons")
		}
		if len(response.AgentBreakdown) != 2 {
			t.Errorf("Expected 2 agent responses")
		}
	})

	t.Run("JSON Serialization", func(t *testing.T) {
		response := OrchestratorResponse{
			RequestID:      "test-999",
			Verdict:        VerdictAuthentic,
			RiskScore:      0.15,
			Confidence:     0.95,
			Reasons:        []string{"No anomalies detected"},
			AgentBreakdown: []AgentResponse{},
			Timestamp:      time.Now(),
		}

		jsonData, err := json.Marshal(response)
		if err != nil {
			t.Fatalf("Failed to marshal orchestrator response: %v", err)
		}

		var decoded OrchestratorResponse
		err = json.Unmarshal(jsonData, &decoded)
		if err != nil {
			t.Fatalf("Failed to unmarshal orchestrator response: %v", err)
		}

		if decoded.Verdict != VerdictAuthentic {
			t.Errorf("Verdict mismatch after JSON round-trip")
		}
	})
}

func TestDefaultWeights(t *testing.T) {
	weights := DefaultWeights()

	if weights.Visual != 0.45 {
		t.Errorf("Expected visual weight to be 0.45")
	}
	if weights.Metadata != 0.55 {
		t.Errorf("Expected metadata weight to be 0.55")
	}
	if weights.Audio != 0.30 {
		t.Errorf("Expected audio weight to be 0.30")
	}
	if weights.Lipsync != 0.00 {
		t.Errorf("Expected lipsync weight to be 0.00")
	}
}

func TestEnumValues(t *testing.T) {
	t.Run("MediaType Enums", func(t *testing.T) {
		if MediaTypeVideo != "video" {
			t.Errorf("Expected MediaTypeVideo to be 'video'")
		}
		if MediaTypeImage != "image" {
			t.Errorf("Expected MediaTypeImage to be 'image'")
		}
	})

	t.Run("Verdict Enums", func(t *testing.T) {
		if VerdictAuthentic != "AUTHENTIC" {
			t.Errorf("Expected VerdictAuthentic to be 'AUTHENTIC'")
		}
		if VerdictSuspicious != "SUSPICIOUS" {
			t.Errorf("Expected VerdictSuspicious to be 'SUSPICIOUS'")
		}
		if VerdictHighRisk != "HIGH_RISK" {
			t.Errorf("Expected VerdictHighRisk to be 'HIGH_RISK'")
		}
	})
}
