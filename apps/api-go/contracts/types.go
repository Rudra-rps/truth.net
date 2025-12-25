package contracts

import "time"

// MediaType represents the type of media being analyzed
type MediaType string

const (
	MediaTypeVideo MediaType = "video"
	MediaTypeImage MediaType = "image"
	MediaTypeAudio MediaType = "audio"
)

// AgentType represents the type of agent
type AgentType string

const (
	AgentTypeVisual   AgentType = "visual"
	AgentTypeMetadata AgentType = "metadata"
	AgentTypeAudio    AgentType = "audio"
	AgentTypeLipsync  AgentType = "lipsync"
)

// Status represents the analysis completion status
type Status string

const (
	StatusSuccess Status = "success"
	StatusPartial Status = "partial"
	StatusFailed  Status = "failed"
)

// Severity represents signal severity
type Severity string

const (
	SeverityLow    Severity = "low"
	SeverityMedium Severity = "medium"
	SeverityHigh   Severity = "high"
)

// Verdict represents the final assessment
type Verdict string

const (
	VerdictAuthentic  Verdict = "AUTHENTIC"
	VerdictSuspicious Verdict = "SUSPICIOUS"
	VerdictHighRisk   Verdict = "HIGH_RISK"
)

// AgentRequest represents a request to an agent for analysis
type AgentRequest struct {
	RequestID string                 `json:"request_id" binding:"required"`
	MediaPath string                 `json:"media_path" binding:"required"`
	MediaType MediaType              `json:"media_type" binding:"required"`
	AgentType AgentType              `json:"agent_type" binding:"required"`
	Options   map[string]interface{} `json:"options,omitempty"`
}

// Signal represents a detected anomaly or indicator
type Signal struct {
	SignalType  string                 `json:"signal_type" binding:"required"`
	Confidence  float64                `json:"confidence" binding:"required,min=0,max=1"`
	Description string                 `json:"description" binding:"required"`
	Severity    Severity               `json:"severity,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// AgentError represents an error from an agent
type AgentError struct {
	Code    string                 `json:"code"`
	Message string                 `json:"message"`
	Details map[string]interface{} `json:"details,omitempty"`
}

// AgentResponse represents a response from an agent
type AgentResponse struct {
	RequestID        string                 `json:"request_id" binding:"required"`
	AgentType        AgentType              `json:"agent_type" binding:"required"`
	Status           Status                 `json:"status" binding:"required"`
	RiskScore        float64                `json:"risk_score" binding:"required,min=0,max=1"`
	Signals          []Signal               `json:"signals" binding:"required"`
	ProcessingTimeMs int64                  `json:"processing_time_ms,omitempty"`
	Error            *AgentError            `json:"error,omitempty"`
	Metadata         map[string]interface{} `json:"metadata,omitempty"`
}

// OrchestratorResponse represents the final aggregated response
type OrchestratorResponse struct {
	RequestID        string          `json:"request_id" binding:"required"`
	Verdict          Verdict         `json:"verdict" binding:"required"`
	RiskScore        float64         `json:"risk_score" binding:"required,min=0,max=1"`
	Confidence       float64         `json:"confidence" binding:"required,min=0,max=1"`
	Reasons          []string        `json:"reasons" binding:"required"`
	AgentBreakdown   []AgentResponse `json:"agent_breakdown" binding:"required"`
	ProcessingTimeMs int64           `json:"processing_time_ms"`
	Timestamp        time.Time       `json:"timestamp"`
}

// AgentWeights defines the weights for each agent in consensus
type AgentWeights struct {
	Visual   float64
	Metadata float64
	Audio    float64
	Lipsync  float64
}

// DefaultWeights returns the default agent weights for MVP
func DefaultWeights() AgentWeights {
	return AgentWeights{
		Visual:   0.45,
		Metadata: 0.55,
		Audio:    0.30, // Only if implemented
		Lipsync:  0.00, // Not in MVP
	}
}
