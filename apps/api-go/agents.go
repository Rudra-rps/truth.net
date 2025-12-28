package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"truthnet/api-go/contracts"
)

// callVisualAgent sends request to visual agent and returns response
func callVisualAgent(requestID, mediaPath string, mediaType contracts.MediaType) *contracts.AgentResponse {
	fmt.Printf("🎨 Calling Visual Agent for request %s\n", requestID)

	request := contracts.AgentRequest{
		RequestID: requestID,
		MediaPath: mediaPath,
		MediaType: mediaType,
		AgentType: contracts.AgentTypeVisual,
		Options:   make(map[string]interface{}),
	}

	response := callAgent(VisualAgentURL+"/analyze", request)
	if response != nil {
		fmt.Printf("   ✓ Visual Agent: Risk %.2f, %d signals\n", response.RiskScore, len(response.Signals))
	}
	return response
}

// callMetadataAgent sends request to metadata agent and returns response
func callMetadataAgent(requestID, mediaPath string, mediaType contracts.MediaType) *contracts.AgentResponse {
	fmt.Printf("📋 Calling Metadata Agent for request %s\n", requestID)

	request := contracts.AgentRequest{
		RequestID: requestID,
		MediaPath: mediaPath,
		MediaType: mediaType,
		AgentType: contracts.AgentTypeMetadata,
		Options:   make(map[string]interface{}),
	}

	response := callAgent(MetadataAgentURL+"/analyze", request)
	if response != nil {
		fmt.Printf("   ✓ Metadata Agent: Risk %.2f, %d signals\n", response.RiskScore, len(response.Signals))
	}
	return response
}

// callAgent is a generic HTTP client for calling agent services
func callAgent(url string, request contracts.AgentRequest) *contracts.AgentResponse {
	// Marshal request to JSON
	jsonData, err := json.Marshal(request)
	if err != nil {
		return createErrorResponse(request, "MARSHAL_ERROR", err.Error())
	}

	// Create HTTP request with timeout
	client := &http.Client{
		Timeout: 30 * time.Second,
	}

	httpReq, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return createErrorResponse(request, "REQUEST_CREATE_ERROR", err.Error())
	}

	httpReq.Header.Set("Content-Type", "application/json")

	// Send request
	resp, err := client.Do(httpReq)
	if err != nil {
		return createErrorResponse(request, "NETWORK_ERROR", err.Error())
	}
	defer resp.Body.Close()

	// Read response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return createErrorResponse(request, "READ_ERROR", err.Error())
	}

	// Check status code
	if resp.StatusCode != http.StatusOK {
		return createErrorResponse(request, "HTTP_ERROR", fmt.Sprintf("Status: %d, Body: %s", resp.StatusCode, string(body)))
	}

	// Parse response
	var agentResp contracts.AgentResponse
	if err := json.Unmarshal(body, &agentResp); err != nil {
		return createErrorResponse(request, "UNMARSHAL_ERROR", err.Error())
	}

	return &agentResp
}

// createErrorResponse creates an error response when agent call fails
func createErrorResponse(request contracts.AgentRequest, code, message string) *contracts.AgentResponse {
	return &contracts.AgentResponse{
		RequestID: request.RequestID,
		AgentType: request.AgentType,
		Status:    contracts.StatusFailed,
		RiskScore: 0.0,
		Signals:   []contracts.Signal{},
		Error: &contracts.AgentError{
			Code:    code,
			Message: message,
		},
	}
}
