package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"time"

	"truthnet/api-go/contracts"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

const (
	MaxFileSize      = 100 * 1024 * 1024 // 100MB
	MediaTempDir     = "./tmp/media"
	VisualAgentURL   = "http://localhost:8001"
	MetadataAgentURL = "http://localhost:8002"
)

func main() {
	// Ensure temp directory exists
	if err := os.MkdirAll(MediaTempDir, 0755); err != nil {
		log.Fatalf("Failed to create temp directory: %v", err)
	}

	// Initialize Gin router
	router := gin.Default()

	// Configure max multipart memory
	router.MaxMultipartMemory = MaxFileSize

	// Health check
	router.GET("/health", healthHandler)

	// Upload and analyze endpoint
	router.POST("/analyze", analyzeHandler)

	// Get result endpoint
	router.GET("/result/:request_id", getResultHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}

	fmt.Printf("🚀 TruthNet API Server starting on port %s\n", port)
	fmt.Printf("📁 Media temp directory: %s\n", MediaTempDir)
	fmt.Printf("🔗 Visual Agent: %s\n", VisualAgentURL)
	fmt.Printf("🔗 Metadata Agent: %s\n", MetadataAgentURL)

	if err := router.Run(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func healthHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "healthy",
		"service": "TruthNet API Server",
		"version": "1.0.0",
	})
}

func analyzeHandler(c *gin.Context) {
	startTime := time.Now()

	// Parse multipart form
	file, err := c.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "No file uploaded",
			"details": err.Error(),
		})
		return
	}

	// Validate file size
	if file.Size > MaxFileSize {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": fmt.Sprintf("File too large. Max size: %d MB", MaxFileSize/(1024*1024)),
		})
		return
	}

	// Determine media type from extension
	mediaType := detectMediaType(file.Filename)
	if mediaType == "" {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "Unsupported file type. Please upload an image or video.",
		})
		return
	}

	// Generate unique request ID
	requestID := uuid.New().String()

	// Create request-specific directory
	requestDir := filepath.Join(MediaTempDir, requestID)
	if err := os.MkdirAll(requestDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Failed to create storage directory",
		})
		return
	}

	// Save uploaded file
	mediaPath := filepath.Join(requestDir, file.Filename)
	if err := c.SaveUploadedFile(file, mediaPath); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error":   "Failed to save file",
			"details": err.Error(),
		})
		return
	}

	// Get absolute path
	absPath, err := filepath.Abs(mediaPath)
	if err != nil {
		absPath = mediaPath
	}

	fmt.Printf("📁 File saved: %s (%.2f MB)\n", file.Filename, float64(file.Size)/(1024*1024))
	fmt.Printf("🔍 Request ID: %s\n", requestID)
	fmt.Printf("📊 Media Type: %s\n", mediaType)

	// Call agents in parallel
	visualResponse := callVisualAgent(requestID, absPath, mediaType)
	metadataResponse := callMetadataAgent(requestID, absPath, mediaType)

	// Calculate orchestrator response
	orchestratorResp := calculateVerdict(requestID, visualResponse, metadataResponse, startTime)

	c.JSON(http.StatusOK, orchestratorResp)
}

func getResultHandler(c *gin.Context) {
	requestID := c.Param("request_id")

	// For now, this is a placeholder
	// In production, you'd store results in a database
	c.JSON(http.StatusOK, gin.H{
		"request_id": requestID,
		"message":    "Result retrieval not yet implemented",
	})
}

func detectMediaType(filename string) contracts.MediaType {
	ext := filepath.Ext(filename)
	switch ext {
	case ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp":
		return contracts.MediaTypeImage
	case ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm":
		return contracts.MediaTypeVideo
	default:
		return ""
	}
}
