# Test TruthNet API End-to-End
# This script tests the complete pipeline: API -> Agents -> Verdict

Write-Host "=" * 60
Write-Host "🧪 TRUTHNET END-TO-END TEST"
Write-Host "=" * 60

# Check if services are running
Write-Host "`n📡 Checking services..."

try {
    $visual = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing
    Write-Host "   ✓ Visual Agent: Running" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Visual Agent: Not running" -ForegroundColor Red
    exit 1
}

try {
    $metadata = Invoke-WebRequest -Uri "http://localhost:8002/health" -UseBasicParsing
    Write-Host "   ✓ Metadata Agent: Running" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Metadata Agent: Not running" -ForegroundColor Red
    exit 1
}

try {
    $api = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
    Write-Host "   ✓ API Server: Running" -ForegroundColor Green
} catch {
    Write-Host "   ✗ API Server: Not running" -ForegroundColor Red
    exit 1
}

# Create a test image
Write-Host "`n📸 Creating test image..."
$testDir = "C:\truthnet\test_data"
if (-not (Test-Path $testDir)) {
    New-Item -ItemType Directory -Path $testDir | Out-Null
}

$testImage = "$testDir\test_upload.jpg"

# Create a simple test image using Python
$pythonScript = @"
from PIL import Image
img = Image.new('RGB', (800, 600), color='blue')
img.save('$testImage', 'JPEG')
print('Test image created')
"@

python -c $pythonScript
Write-Host "   ✓ Test image created: $testImage" -ForegroundColor Green

# Upload and analyze
Write-Host "`n🚀 Uploading file to API..."
Write-Host "   File: $testImage"

try {
    # PowerShell multipart form upload
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBytes = [System.IO.File]::ReadAllBytes($testImage)
    $fileName = [System.IO.Path]::GetFileName($testImage)
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
        "Content-Type: image/jpeg",
        "",
        [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($fileBytes),
        "--$boundary--"
    )
    
    $body = $bodyLines -join "`r`n"
    
    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/analyze" `
        -Method POST `
        -Body $body `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -UseBasicParsing
    
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "`n" + ("=" * 60)
    Write-Host "✅ ANALYSIS COMPLETE"
    Write-Host ("=" * 60)
    
    Write-Host "`n🎯 VERDICT: $($result.verdict)" -ForegroundColor $(
        if ($result.verdict -eq "AUTHENTIC") { "Green" }
        elseif ($result.verdict -eq "SUSPICIOUS") { "Yellow" }
        else { "Red" }
    )
    
    Write-Host "📊 Risk Score: $([math]::Round($result.risk_score, 2))"
    Write-Host "🎲 Confidence: $([math]::Round($result.confidence, 2))"
    Write-Host "⏱️  Processing Time: $($result.processing_time_ms)ms"
    
    Write-Host "`n📋 Agent Breakdown:"
    foreach ($agent in $result.agent_breakdown) {
        Write-Host "   • $($agent.agent_type): Risk=$([math]::Round($agent.risk_score, 2)), Signals=$($agent.signals.Count)"
    }
    
    Write-Host "`n💡 Top Reasons:"
    foreach ($reason in $result.reasons) {
        Write-Host "   • $reason"
    }
    
    Write-Host "`n" + ("=" * 60)
    Write-Host "✅ TEST PASSED - Full pipeline working!"
    Write-Host ("=" * 60)
    
} catch {
    Write-Host "`n❌ API call failed:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}
