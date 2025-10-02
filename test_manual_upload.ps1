# Manual test upload via curl
$token = (Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
    -Method Post `
    -ContentType "application/json" `
    -Body (@{
        email = "test_$(Get-Random)@test.com"
        password = "TestPass123!"
        full_name = "Test User"
        role = "student"
        student_code = "SV$(Get-Random)"
        university = "UIT"
        major = "CS"
        year_of_study = 3
        phone = "0123456789"
    } | ConvertTo-Json)).access_token

Write-Host "Token: $($token.Substring(0, 30))..."

# Upload via curl (better multipart handling)
Write-Host "`nUploading audio..."
curl -X POST http://localhost:8000/api/v1/voice-analysis/analyze `
    -H "Authorization: Bearer $token" `
    -F "audio_file=@test_audio.wav"
