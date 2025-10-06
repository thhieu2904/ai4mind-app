# Switch Render Config Script
# Usage: 
#   .\switch-render-config.ps1 ai-only    # AI service only
#   .\switch-render-config.ps1 full       # Both services

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("ai-only", "full")]
    [string]$Mode
)

$rootPath = Split-Path -Parent $PSCommandPath

Write-Host "🔄 Switching Render config to: $Mode" -ForegroundColor Cyan

# Backup current render.yaml if exists
if (Test-Path "$rootPath\render.yaml") {
    Copy-Item "$rootPath\render.yaml" "$rootPath\render.yaml.backup" -Force
    Write-Host "✅ Backed up current render.yaml" -ForegroundColor Green
}

# Switch config
switch ($Mode) {
    "ai-only" {
        if (Test-Path "$rootPath\render.ai-only.yaml") {
            Copy-Item "$rootPath\render.ai-only.yaml" "$rootPath\render.yaml" -Force
            Write-Host "✅ Switched to AI-only config (no voice service)" -ForegroundColor Green
            Write-Host "📝 This config deploys only AI service to avoid 512MB memory limit" -ForegroundColor Yellow
        } else {
            Write-Host "❌ render.ai-only.yaml not found!" -ForegroundColor Red
            exit 1
        }
    }
    "full" {
        if (Test-Path "$rootPath\render.full.yaml") {
            Copy-Item "$rootPath\render.full.yaml" "$rootPath\render.yaml" -Force
            Write-Host "✅ Switched to full config (both services)" -ForegroundColor Green
            Write-Host "⚠️  WARNING: Voice service requires 512MB+ RAM and may fail on free tier!" -ForegroundColor Yellow
        } else {
            Write-Host "❌ render.full.yaml not found!" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Review render.yaml" -ForegroundColor White
Write-Host "2. git add render.yaml" -ForegroundColor White
Write-Host "3. git commit -m 'config: Switch to $Mode render config'" -ForegroundColor White
Write-Host "4. git push origin main" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Deploy will use the new config!" -ForegroundColor Green
