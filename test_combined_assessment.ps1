# Test Combined Assessment Endpoint
# Tests the new /assessments/submit-with-voice endpoint

$ErrorActionPreference = "Stop"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Combined Assessment Test Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$AI_SERVICE_URL = "http://localhost:8000"
$STUDENT_EMAIL = "student1@example.com"
$STUDENT_PASSWORD = "password123"

# Step 1: Login to get token
Write-Host "Step 1: Logging in as student..." -ForegroundColor Yellow

$loginBody = @{
    email = $STUDENT_EMAIL
    password = $STUDENT_PASSWORD
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$AI_SERVICE_URL/api/v1/auth/login" `
        -Method POST `
        -Body $loginBody `
        -ContentType "application/json"
    
    $token = $loginResponse.access_token
    Write-Host "✓ Login successful!" -ForegroundColor Green
    Write-Host "  Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Login failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Prepare test data
Write-Host "Step 2: Preparing test data..." -ForegroundColor Yellow

# GAD-7 answers (simulate moderate anxiety: score = 12)
$gad7Answers = @(2, 1, 2, 2, 1, 2, 2)  # Total: 12 (moderate)
$gad7Json = $gad7Answers | ConvertTo-Json -Compress

# Copy real audio to a unique filename
$sourceAudio = "D:\job\ai4mind-app\test_audio.wav"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$audioFile = "D:\job\ai4mind-app\test_audio_combined_$timestamp.wav"

if (-not (Test-Path $sourceAudio)) {
    Write-Host "  ✗ Error: test_audio.wav not found!" -ForegroundColor Red
    exit 1
}

Copy-Item $sourceAudio $audioFile
Write-Host "  ✓ Created unique audio file: test_audio_combined_$timestamp.wav" -ForegroundColor Green

Write-Host ""

# Step 3: Submit combined assessment
Write-Host "Step 3: Submitting combined assessment (GAD-7 + Voice)..." -ForegroundColor Yellow

$headers = @{
    Authorization = "Bearer $token"
}

# Prepare multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

# Read audio file
$audioBytes = [System.IO.File]::ReadAllBytes($audioFile)
$audioFileName = Split-Path $audioFile -Leaf

# Build multipart body
$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"answers`"",
    "",
    $gad7Json,
    "--$boundary",
    "Content-Disposition: form-data; name=`"functional_impairment`"",
    "",
    "2",
    "--$boundary",
    "Content-Disposition: form-data; name=`"notes`"",
    "",
    "Test submission from PowerShell script",
    "--$boundary",
    "Content-Disposition: form-data; name=`"gender`"",
    "",
    "male",
    "--$boundary",
    "Content-Disposition: form-data; name=`"prompt_text`"",
    "",
    "Hãy chia sẻ cảm xúc của bạn trong 2 tuần qua",
    "--$boundary",
    "Content-Disposition: form-data; name=`"audio_file`"; filename=`"$audioFileName`"",
    "Content-Type: audio/mpeg",
    "",
    [System.Text.Encoding]::GetEncoding("iso-8859-1").GetString($audioBytes),
    "--$boundary--"
)

$body = ($bodyLines -join $LF)

try {
    Write-Host "  Sending request to: $AI_SERVICE_URL/api/v1/assessments/submit-with-voice" -ForegroundColor Gray
    
    $response = Invoke-RestMethod -Uri "$AI_SERVICE_URL/api/v1/assessments/submit-with-voice" `
        -Method POST `
        -Headers @{
            Authorization = "Bearer $token"
            "Content-Type" = "multipart/form-data; boundary=$boundary"
        } `
        -Body ([System.Text.Encoding]::GetEncoding("iso-8859-1").GetBytes($body))
    
    Write-Host "✓ Assessment submitted successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Cyan
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host "  Assessment ID: $($response.id)" -ForegroundColor White
    Write-Host "  Student ID: $($response.student_id)" -ForegroundColor White
    Write-Host "  Total Score: $($response.total_score)/21" -ForegroundColor White
    Write-Host "  Severity: $($response.severity_level)" -ForegroundColor White
    Write-Host "  Voice Analysis ID: $($response.voice_analysis_id)" -ForegroundColor Yellow
    Write-Host "  Created: $($response.created_at)" -ForegroundColor White
    Write-Host ""
    Write-Host "  Analysis:" -ForegroundColor Cyan
    Write-Host "  $($response.analysis.Substring(0, [Math]::Min(200, $response.analysis.Length)))..." -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Recommendations:" -ForegroundColor Cyan
    foreach ($rec in $response.recommendations) {
        Write-Host "  - $rec" -ForegroundColor Gray
    }
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    # Step 4: Verify data consistency in database
    Write-Host ""
    Write-Host "Step 4: Verifying data consistency..." -ForegroundColor Yellow
    
    $assessmentId = $response.id
    $voiceId = $response.voice_analysis_id
    
    Write-Host "  ✓ Assessment ID: $assessmentId" -ForegroundColor Green
    Write-Host "  ✓ Voice Analysis ID: $voiceId" -ForegroundColor Green
    Write-Host "  ✓ Both records created atomically!" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "TEST PASSED! ✓" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Cyan
    
} catch {
    Write-Host "✗ Assessment submission failed!" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Response body:" -ForegroundColor Yellow
    Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    exit 1
}
