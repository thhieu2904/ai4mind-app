# Warm up voice service by sending a dummy request
Write-Host "🔥 Warming up voice service..." -ForegroundColor Yellow

curl -X POST http://localhost:8001/api/v1/voice/analyze `
    -F "file=@test_audio.wav" `
    -F "user_id=999" `
    -F "gender=male" `
    -o nul 2>$null

Write-Host "✅ Voice service warmed up!" -ForegroundColor Green
Write-Host ""
