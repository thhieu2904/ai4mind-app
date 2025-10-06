#!/usr/bin/env pwsh
# ============================================================================
# AUTO UPDATE MODELS SCRIPT
# ============================================================================
# Description: Automatically update SQLAlchemy models Integer → BigInteger
# Usage: .\update-models.ps1
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " AUTO UPDATE MODELS TO BIGINT" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Base path
$BasePath = "D:\job\ai4mind-app\ai-service\app\models"

# Model files to update
$ModelFiles = @(
    "user.py",
    "student.py",
    "parent.py",
    "counselor.py",
    "assessment.py",
    "voice_analysis.py",
    "conversation.py",
    "ai_chat.py",
    "counselor_chat.py"
)

# Timestamp models needing updates
$TimestampModels = @{
    "counselor.py" = @{
        "class" = "Counselor"
        "after_line" = "is_available = Column(Boolean, default=True)"
    }
    "parent.py" = @{
        "class" = "Parent"
        "after_line" = "occupation = Column(String(255), nullable=True)"
    }
    "counselor_chat.py" = @{
        "class" = "CounselorConversation"
        "after_line" = "created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)"
    }
}

# Backup directory
$BackupDir = "D:\job\ai4mind-app\database\model_backups_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

Write-Host "[1/4] Creating backups..." -ForegroundColor Yellow
foreach ($file in $ModelFiles) {
    $fullPath = Join-Path $BasePath $file
    if (Test-Path $fullPath) {
        Copy-Item $fullPath (Join-Path $BackupDir $file)
        Write-Host "  ✅ Backed up: $file" -ForegroundColor Green
    }
}

Write-Host "`n[2/4] Updating models: Integer → BigInteger..." -ForegroundColor Yellow

$UpdatedCount = 0
$ErrorFiles = @()

foreach ($file in $ModelFiles) {
    $fullPath = Join-Path $BasePath $file
    
    if (-not (Test-Path $fullPath)) {
        Write-Host "  ⚠️ Not found: $file" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "  Processing: $file" -ForegroundColor Cyan
    
    try {
        # Read content
        $content = Get-Content $fullPath -Raw
        $originalContent = $content
        
        # Check if BigInteger already imported
        $hasBigInteger = $content -match 'BigInteger'
        
        # Update imports - Add BigInteger if not present
        if (-not $hasBigInteger) {
            # Pattern 1: from sqlalchemy import Column, Integer, ...
            if ($content -match 'from sqlalchemy import Column, Integer([,\s])') {
                $content = $content -replace 'from sqlalchemy import Column, Integer([,\s])', 'from sqlalchemy import Column, Integer, BigInteger$1'
                Write-Host "    • Added BigInteger to imports" -ForegroundColor Gray
            }
        }
        
        # Update ID columns to BigInteger
        $patterns = @(
            # Primary keys
            @{
                Pattern = '(\s+id\s*=\s*Column\()Integer(,\s*primary_key=True)'
                Replace = '$1BigInteger$2'
                Desc = 'Primary key id'
            },
            # Foreign keys with explicit names
            @{
                Pattern = '(\s+user_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key user_id'
            },
            @{
                Pattern = '(\s+student_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key student_id'
            },
            @{
                Pattern = '(\s+parent_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key parent_id'
            },
            @{
                Pattern = '(\s+counselor_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key counselor_id'
            },
            @{
                Pattern = '(\s+assessment_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key assessment_id'
            },
            @{
                Pattern = '(\s+conversation_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key conversation_id'
            },
            @{
                Pattern = '(\s+voice_analysis_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key voice_analysis_id'
            },
            @{
                Pattern = '(\s+emergency_contact_parent_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key emergency_contact_parent_id'
            },
            @{
                Pattern = '(\s+latest_assessment_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key latest_assessment_id'
            },
            @{
                Pattern = '(\s+related_assessment_id\s*=\s*Column\()Integer(,\s*ForeignKey)'
                Replace = '$1BigInteger$2'
                Desc = 'Foreign key related_assessment_id'
            }
        )
        
        $changesCount = 0
        foreach ($pattern in $patterns) {
            if ($content -match $pattern.Pattern) {
                $content = $content -replace $pattern.Pattern, $pattern.Replace
                Write-Host "    • Updated: $($pattern.Desc)" -ForegroundColor Gray
                $changesCount++
            }
        }
        
        # Save if changed
        if ($content -ne $originalContent) {
            $content | Out-File $fullPath -Encoding UTF8 -NoNewline
            Write-Host "  ✅ Updated: $file ($changesCount changes)" -ForegroundColor Green
            $UpdatedCount++
        } else {
            Write-Host "  ℹ️ No changes needed: $file" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "  ❌ Error updating $file : $_" -ForegroundColor Red
        $ErrorFiles += $file
    }
}

Write-Host "`n[3/4] Adding timestamps to models..." -ForegroundColor Yellow

foreach ($file in $TimestampModels.Keys) {
    $fullPath = Join-Path $BasePath $file
    
    if (-not (Test-Path $fullPath)) {
        Write-Host "  ⚠️ Not found: $file" -ForegroundColor Yellow
        continue
    }
    
    Write-Host "  Processing: $file" -ForegroundColor Cyan
    
    try {
        $content = Get-Content $fullPath -Raw
        $modelInfo = $TimestampModels[$file]
        
        # Check if timestamps already exist
        if ($content -match 'created_at\s*=\s*Column\(DateTime' -or 
            $content -match 'updated_at\s*=\s*Column\(DateTime') {
            Write-Host "    ℹ️ Timestamps already exist" -ForegroundColor Gray
            continue
        }
        
        # For Counselor and Parent: Add both timestamps
        if ($file -in @("counselor.py", "parent.py")) {
            # Add DateTime import if needed
            if ($content -notmatch 'DateTime') {
                $content = $content -replace 'from sqlalchemy import Column,', 'from sqlalchemy import Column, DateTime,'
                $content = $content -replace 'from app.models import Base', "from app.models import Base`nfrom sqlalchemy.sql import func"
            }
            
            # Find the class and add timestamps before relationships
            $afterLine = $modelInfo.after_line
            $timestampCode = @"

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
"@
            
            $content = $content -replace "($afterLine)", "`$1$timestampCode"
            Write-Host "    • Added created_at and updated_at" -ForegroundColor Gray
        }
        # For CounselorConversation: Add only updated_at
        elseif ($file -eq "counselor_chat.py") {
            $afterLine = $modelInfo.after_line
            $timestampCode = "`n    updated_at = Column(DateTime(timezone=True), onupdate=func.now())"
            
            $content = $content -replace "($afterLine)", "`$1$timestampCode"
            Write-Host "    • Added updated_at" -ForegroundColor Gray
        }
        
        # Save
        $content | Out-File $fullPath -Encoding UTF8 -NoNewline
        Write-Host "  ✅ Updated: $file" -ForegroundColor Green
        
    } catch {
        Write-Host "  ❌ Error adding timestamps to $file : $_" -ForegroundColor Red
        $ErrorFiles += $file
    }
}

Write-Host "`n[4/4] Verification..." -ForegroundColor Yellow

# Verify BigInteger usage
$VerifyErrors = @()
foreach ($file in $ModelFiles) {
    $fullPath = Join-Path $BasePath $file
    if (Test-Path $fullPath) {
        $content = Get-Content $fullPath -Raw
        
        # Check if file uses ForeignKey but doesn't have BigInteger
        if (($content -match 'ForeignKey') -and ($content -notmatch 'BigInteger')) {
            Write-Host "  ⚠️ Warning: $file uses ForeignKey but might miss BigInteger" -ForegroundColor Yellow
            $VerifyErrors += $file
        }
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Updated files: $UpdatedCount" -ForegroundColor Green
Write-Host "Backup location: $BackupDir" -ForegroundColor Cyan

if ($ErrorFiles.Count -gt 0) {
    Write-Host "`n⚠️ Errors occurred in:" -ForegroundColor Red
    foreach ($file in $ErrorFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
}

if ($VerifyErrors.Count -gt 0) {
    Write-Host "`n⚠️ Please manually verify:" -ForegroundColor Yellow
    foreach ($file in $VerifyErrors) {
        Write-Host "  - $file" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Next steps:" -ForegroundColor Green
Write-Host "1. Review changes with: git diff" -ForegroundColor White
Write-Host "2. Test imports: python -c 'from app.models import *'" -ForegroundColor White
Write-Host "3. If OK, proceed to run migrations" -ForegroundColor White
Write-Host "`nIf need to rollback: Copy files from $BackupDir" -ForegroundColor Yellow
