# Test registration with full student data
Write-Host "Testing registration with complete student data..." -ForegroundColor Yellow

$body = @{
    email = "student_test_$(Get-Random)@example.com"
    password = "TestPass123!"
    full_name = "Test Student"
    role = "student"
    student_code = "SV$(Get-Random -Minimum 1000 -Maximum 9999)"
    university = "UIT"
    major = "Computer Science"
    year_of_study = 3
    phone = "0123456789"
} | ConvertTo-Json

Write-Host "`nRequest body:" -ForegroundColor Gray
Write-Host $body -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body
    
    Write-Host "`n✅ Success!" -ForegroundColor Green
    Write-Host "User ID: $($response.user.id)" -ForegroundColor Green
    Write-Host "Email: $($response.user.email)" -ForegroundColor Green
    Write-Host "Role: $($response.user.role)" -ForegroundColor Green
    Write-Host "Token: $($response.access_token.Substring(0, 30))..." -ForegroundColor Gray
} catch {
    Write-Host "`n❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    
    if ($_.ErrorDetails) {
        Write-Host "`nError details:" -ForegroundColor Red
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
}
