# Test login với cURL - Windows PowerShell

# Counselor 1
$body = @{
    email = "counselor1@ai4mind.com"
    password = "Counselor123!"
} | ConvertTo-Json

Write-Host "Testing login for counselor1@ai4mind.com..." -ForegroundColor Cyan
Write-Host "Password: Counselor123!" -ForegroundColor Yellow

$response = Invoke-RestMethod `
    -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body $body `
    -ErrorAction SilentlyContinue

if ($response) {
    Write-Host "`n✅ LOGIN SUCCESS!" -ForegroundColor Green
    Write-Host "Access Token: $($response.access_token.Substring(0, 50))..." -ForegroundColor Green
    Write-Host "User: $($response.user.full_name) ($($response.user.role))" -ForegroundColor Green
} else {
    Write-Host "`n❌ LOGIN FAILED!" -ForegroundColor Red
    Write-Host "Check backend logs for details" -ForegroundColor Yellow
}
