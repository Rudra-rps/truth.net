package main

import (
	"fmt"
	"time"

	"truthnet/api-go/contracts"
)

// Agent weights for consensus calculation (from SCOPE.md)
const (
	VisualWeight   = 0.45
	MetadataWeight = 0.55
)

// calculateVerdict combines agent responses into final verdict
func calculateVerdict(
	requestID string,
	visualResp *contracts.AgentResponse,
	metadataResp *contracts.AgentResponse,
	startTime time.Time,
) contracts.OrchestratorResponse {

	agentBreakdown := []contracts.AgentResponse{}

	// Add successful responses to breakdown
	if visualResp != nil {
		agentBreakdown = append(agentBreakdown, *visualResp)
	}
	if metadataResp != nil {
		agentBreakdown = append(agentBreakdown, *metadataResp)
	}

	// Calculate weighted risk score
	totalWeight := 0.0
	weightedScore := 0.0

	if visualResp != nil && visualResp.Status == contracts.StatusSuccess {
		weightedScore += visualResp.RiskScore * VisualWeight
		totalWeight += VisualWeight
	}

	if metadataResp != nil && metadataResp.Status == contracts.StatusSuccess {
		weightedScore += metadataResp.RiskScore * MetadataWeight
		totalWeight += MetadataWeight
	}

	// Normalize score
	finalScore := 0.0
	if totalWeight > 0 {
		finalScore = weightedScore / totalWeight
	}

	// Determine verdict based on score
	verdict := determineVerdict(finalScore)

	// Calculate confidence (higher when both agents agree)
	confidence := calculateConfidence(visualResp, metadataResp, finalScore)

	// Collect top reasons
	reasons := collectReasons(visualResp, metadataResp, verdict)

	// Calculate processing time
	processingTime := time.Since(startTime).Milliseconds()

	fmt.Printf("\n🎯 Final Verdict: %s (Risk: %.2f, Confidence: %.2f)\n", verdict, finalScore, confidence)
	fmt.Printf("⏱️  Processing time: %dms\n\n", processingTime)

	return contracts.OrchestratorResponse{
		RequestID:        requestID,
		Verdict:          verdict,
		RiskScore:        finalScore,
		Confidence:       confidence,
		Reasons:          reasons,
		AgentBreakdown:   agentBreakdown,
		ProcessingTimeMs: processingTime,
		Timestamp:        time.Now(),
	}
}

// determineVerdict maps risk score to verdict level
func determineVerdict(riskScore float64) contracts.Verdict {
	if riskScore < 0.3 {
		return contracts.VerdictAuthentic
	} else if riskScore < 0.6 {
		return contracts.VerdictSuspicious
	}
	return contracts.VerdictHighRisk
}

// calculateConfidence determines confidence in verdict
func calculateConfidence(
	visualResp *contracts.AgentResponse,
	metadataResp *contracts.AgentResponse,
	finalScore float64,
) float64 {
	// Base confidence
	confidence := 0.5

	// Increase confidence if both agents succeeded
	successCount := 0
	if visualResp != nil && visualResp.Status == contracts.StatusSuccess {
		successCount++
	}
	if metadataResp != nil && metadataResp.Status == contracts.StatusSuccess {
		successCount++
	}

	if successCount == 2 {
		confidence = 0.8

		// Check if agents agree (within 0.2 risk score)
		if visualResp != nil && metadataResp != nil {
			scoreDiff := abs(visualResp.RiskScore - metadataResp.RiskScore)
			if scoreDiff < 0.2 {
				confidence = 0.95 // High confidence when agents agree
			} else if scoreDiff < 0.4 {
				confidence = 0.85 // Medium confidence
			}
		}
	} else if successCount == 1 {
		confidence = 0.6 // Lower confidence with only one agent
	}

	return confidence
}

// collectReasons gathers top reasons from agent signals
func collectReasons(
	visualResp *contracts.AgentResponse,
	metadataResp *contracts.AgentResponse,
	verdict contracts.Verdict,
) []string {
	reasons := []string{}

	// Add base reason for verdict
	switch verdict {
	case contracts.VerdictAuthentic:
		reasons = append(reasons, "No significant manipulation indicators detected")
	case contracts.VerdictSuspicious:
		reasons = append(reasons, "Some manipulation indicators detected")
	case contracts.VerdictHighRisk:
		reasons = append(reasons, "Multiple strong manipulation indicators detected")
	}

	// Collect high-confidence signals from visual agent
	if visualResp != nil && visualResp.Status == contracts.StatusSuccess {
		for _, signal := range visualResp.Signals {
			if signal.Confidence > 0.6 && len(reasons) < 5 {
				reasons = append(reasons, fmt.Sprintf("Visual: %s", signal.Description))
			}
		}
	}

	// Collect high-confidence signals from metadata agent
	if metadataResp != nil && metadataResp.Status == contracts.StatusSuccess {
		for _, signal := range metadataResp.Signals {
			if signal.Confidence > 0.6 && len(reasons) < 5 {
				reasons = append(reasons, fmt.Sprintf("Metadata: %s", signal.Description))
			}
		}
	}

	return reasons
}

// abs returns absolute value of float64
func abs(x float64) float64 {
	if x < 0 {
		return -x
	}
	return x
}
