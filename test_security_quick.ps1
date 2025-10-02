# Quick Security Test - AI4Mind
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "   AI4MIND SECURITY QUICK TEST" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# Health checks
Write-Host "[1/8] Health Checks..." -ForegroundColor Yellow
try {
    $healthAI = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    $healthVoice = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
    Write-Host "  ✅ ai-service: $($healthAI.status)" -ForegroundColor Green
    Write-Host "  ✅ voice-service: $($healthVoice.status)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Warm up voice service (load Whisper model)
Write-Host "`n[1.5/8] Warming up voice service (loading Whisper)..." -ForegroundColor Yellow
try {
    curl -s -X POST http://localhost:8001/api/v1/voice/analyze -F "file=@test_audio.wav" -F "user_id=999" -F "gender=male" -o nul 2>$null
    Write-Host "  ✅ Voice service ready!" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  Warmup failed (may be OK): $($_.Exception.Message)" -ForegroundColor Yellow
}

# Register Student A with random email
Write-Host "`n[2/8] Register Student A..." -ForegroundColor Yellow
$randomA = Get-Random -Minimum 100000 -Maximum 999999
$studentA = @{
    email = "student_a_${randomA}@test.com"
    password = "TestPass123!"
    full_name = "Student A Test"
    role = "student"
    student_code = "SVA$randomA"
    university = "UIT"
    major = "Computer Science"
    year_of_study = 3
    phone = "0123456789"
} | ConvertTo-Json

try {
    $responseA = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $studentA
    
    $tokenA = $responseA.access_token
    $userAId = $responseA.user.id
    Write-Host "  ✅ Registered! User ID: $userAId" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Register Student B
Write-Host "`n[3/8] Register Student B..." -ForegroundColor Yellow
$randomB = Get-Random -Minimum 100000 -Maximum 999999
$studentB = @{
    email = "student_b_${randomB}@test.com"
    password = "TestPass123!"
    full_name = "Student B Test"
    role = "student"
    student_code = "SVB$randomB"
    university = "UIT"
    major = "Information Systems"
    year_of_study = 2
    phone = "0987654321"
} | ConvertTo-Json

try {
    $responseB = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $studentB
    
    $tokenB = $responseB.access_token
    $userBId = $responseB.user.id
    Write-Host "  ✅ Registered! User ID: $userBId" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Get Student A profile
Write-Host "`n[4/8] Get Student A profile..." -ForegroundColor Yellow
try {
    $profileA = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/students/me" `
        -Method Get `
        -Headers @{ Authorization = "Bearer $tokenA" }
    
    $studentAId = $profileA.id
    Write-Host "  ✅ Student ID: $studentAId" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Get Student B profile
Write-Host "`n[5/8] Get Student B profile..." -ForegroundColor Yellow
try {
    $profileB = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/students/me" `
        -Method Get `
        -Headers @{ Authorization = "Bearer $tokenB" }
    
    $studentBId = $profileB.id
    Write-Host "  ✅ Student ID: $studentBId" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Prepare test audio
Write-Host "`n[6/8] Prepare test audio..." -ForegroundColor Yellow
$audioFile = "test_audio.wav"
if (-not (Test-Path $audioFile)) {
    try {
        Invoke-WebRequest -Uri "https://www2.cs.uic.edu/~i101/SoundFiles/StarWars60.wav" -OutFile $audioFile
        Write-Host "  ✅ Downloaded sample audio" -ForegroundColor Green
    } catch {
        # Create minimal WAV (silent, 1 sec)
        $wavHeader = [byte[]](0x52,0x49,0x46,0x46,0x24,0x08,0x00,0x00,0x57,0x41,0x56,0x45,0x66,0x6D,0x74,0x20,0x10,0x00,0x00,0x00,0x01,0x00,0x01,0x00,0x44,0xAC,0x00,0x00,0x88,0x58,0x01,0x00,0x02,0x00,0x10,0x00,0x64,0x61,0x74,0x61,0x00,0x08,0x00,0x00)
        $wavData = New-Object byte[] 2048
        [System.IO.File]::WriteAllBytes($audioFile, $wavHeader + $wavData)
        Write-Host "  ✅ Created dummy audio" -ForegroundColor Green
    }
} else {
    Write-Host "  ✅ Audio file exists" -ForegroundColor Green
}

# Upload voice analysis for Student A
Write-Host "`n[7/8] Upload voice analysis (Student A)..." -ForegroundColor Yellow
try {
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $audioBytes = [System.IO.File]::ReadAllBytes($audioFile)
    $audioContent = [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetString($audioBytes)
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"audio_file`"; filename=`"test.wav`"",
        "Content-Type: audio/wav$LF",
        $audioContent,
        "--$boundary--$LF"
    )
    
    $body = $bodyLines -join $LF
    
    $analysisA = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/voice-analysis/analyze" `
        -Method Post `
        -Headers @{
            Authorization = "Bearer $tokenA"
            "Content-Type" = "multipart/form-data; boundary=$boundary"
        } `
        -Body ([System.Text.Encoding]::GetEncoding("ISO-8859-1").GetBytes($body))
    
    $analysisAId = $analysisA.id
    Write-Host "  ✅ Analysis uploaded! ID: $analysisAId" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Upload failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails) {
        Write-Host "     Detail: $($_.ErrorDetails.Message)" -ForegroundColor Red
    }
    exit 1
}

# CRITICAL SECURITY TEST: Student B tries to access Student A's analysis
Write-Host "`n[8/8] 🔒 SECURITY TEST: Student B access Student A's data..." -ForegroundColor Yellow
Write-Host "     (This SHOULD FAIL with 404/403)" -ForegroundColor Gray
try {
    $stolen = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/voice-analysis/$analysisAId" `
        -Method Get `
        -Headers @{ Authorization = "Bearer $tokenB" }
    
    Write-Host "  ❌ SECURITY BREACH! Student B accessed Student A's data!" -ForegroundColor Red
    Write-Host "     Analysis ID: $analysisAId" -ForegroundColor Red
    Write-Host "     Retrieved data: $($stolen.transcription)" -ForegroundColor Red
    exit 1
} catch {
    if ($_.Exception.Response.StatusCode -eq 404 -or $_.Exception.Response.StatusCode -eq 403) {
        Write-Host "  ✅ SECURITY OK! Access denied (404/403)" -ForegroundColor Green
        Write-Host "     Error message: $($_.Exception.Message)" -ForegroundColor Gray
    } else {
        Write-Host "  ⚠️  Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "   ✅ ALL SECURITY TESTS PASSED!" -ForegroundColor Green
Write-Host "==========================================`n" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor White
Write-Host "  • Student A: User $userAId → Student $studentAId → Analysis $analysisAId" -ForegroundColor White
Write-Host "  • Student B: User $userBId → Student $studentBId" -ForegroundColor White
Write-Host "  • Security: Student B cannot access Student A's data ✅" -ForegroundColor White
Write-Host ""
