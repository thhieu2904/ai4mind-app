# Simple registration test
Write-Host "Testing registration..." -ForegroundColor Yellow

$body = @{
    email = "test_$(Get-Random)@example.com"
    password = "TestPass123!"
    full_name = "Test User"
    role = "student"
} | ConvertTo-Json

Write-Host "Request body:" -ForegroundColor Gray
Write-Host $body -ForegroundColor Gray

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "`n✅ Success! Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Gray
    Write-Host $response.Content -ForegroundColor Gray
} catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    
    $result = $_.Exception.Response.GetResponseStream()
    $reader = New-Object System.IO.StreamReader($result)
    $responseBody = $reader.ReadToEnd()
    
    Write-Host "`nResponse body:" -ForegroundColor Red
    Write-Host $responseBody -ForegroundColor Red
}
