#!/usr/bin/env pwsh
# ============================================================================
# MIGRATION RUNNER SCRIPT
# ============================================================================
# Description: Script to run database migrations safely
# Usage: .\run-migration.ps1 -MigrationNumber 001 -Environment staging
# ============================================================================

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("001", "002", "003", "004")]
    [string]$MigrationNumber,
    
    [Parameter(Mandatory=$true)]
    [ValidateSet("staging", "production")]
    [string]$Environment,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Rollback = $false
)

# ============================================================================
# CONFIGURATION
# ============================================================================

$ErrorActionPreference = "Stop"

# Database connection strings (replace with your actual values)
$DbConnections = @{
    staging = @{
        host = "staging-db.xxxx.supabase.co"
        port = "5432"
        database = "postgres"
        user = "postgres"
    }
    production = @{
        host = "db.xxxx.supabase.co"
        port = "5432"
        database = "postgres"
        user = "postgres"
    }
}

# Migration metadata
$Migrations = @{
    "001" = @{
        name = "Add Performance Indices"
        estimated_time = "5-10 minutes"
        requires_downtime = $false
        rollback_available = $true
    }
    "002" = @{
        name = "Add Timestamps"
        estimated_time = "1-2 minutes"
        requires_downtime = $false
        rollback_available = $true
    }
    "003" = @{
        name = "Migrate IDs to BIGINT"
        estimated_time = "30-60 minutes"
        requires_downtime = $true
        rollback_available = $false
    }
    "004" = @{
        name = "Add CHECK Constraints"
        estimated_time = "5-10 minutes"
        requires_downtime = $false
        rollback_available = $true
    }
}

# ============================================================================
# FUNCTIONS
# ============================================================================

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[✓] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[✗] $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "[i] $Message" -ForegroundColor Blue
}

function Test-PostgresConnection {
    param(
        [hashtable]$Connection
    )
    
    Write-Info "Testing database connection..."
    
    try {
        $env:PGPASSWORD = Read-Host "Enter database password" -AsSecureString | ConvertFrom-SecureString -AsPlainText
        
        $result = psql -h $Connection.host `
                      -p $Connection.port `
                      -U $Connection.user `
                      -d $Connection.database `
                      -c "SELECT 1;" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database connection successful"
            return $true
        } else {
            Write-Error "Database connection failed: $result"
            return $false
        }
    } catch {
        Write-Error "Error testing connection: $_"
        return $false
    }
}

function Backup-Database {
    param(
        [hashtable]$Connection,
        [string]$MigrationNumber
    )
    
    Write-Info "Creating database backup..."
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backup_before_migration_${MigrationNumber}_${timestamp}.sql"
    
    try {
        pg_dump -h $Connection.host `
                -p $Connection.port `
                -U $Connection.user `
                -d $Connection.database `
                -f $backupFile
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Backup created: $backupFile"
            $fileSize = (Get-Item $backupFile).Length / 1MB
            Write-Info "Backup size: $([math]::Round($fileSize, 2)) MB"
            return $backupFile
        } else {
            Write-Error "Backup failed"
            return $null
        }
    } catch {
        Write-Error "Error creating backup: $_"
        return $null
    }
}

function Get-MigrationFile {
    param(
        [string]$MigrationNumber,
        [bool]$IsRollback
    )
    
    if ($IsRollback) {
        $file = "migrations/${MigrationNumber}_*_rollback.sql"
    } else {
        $file = "migrations/${MigrationNumber}_*.sql"
    }
    
    $files = Get-ChildItem -Path $file -ErrorAction SilentlyContinue
    
    if ($files.Count -eq 0) {
        Write-Error "Migration file not found: $file"
        return $null
    }
    
    return $files[0].FullName
}

function Run-Migration {
    param(
        [hashtable]$Connection,
        [string]$MigrationFile
    )
    
    Write-Info "Running migration: $MigrationFile"
    
    try {
        $result = psql -h $Connection.host `
                      -p $Connection.port `
                      -U $Connection.user `
                      -d $Connection.database `
                      -f $MigrationFile 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Migration completed successfully"
            Write-Host $result
            return $true
        } else {
            Write-Error "Migration failed"
            Write-Host $result
            return $false
        }
    } catch {
        Write-Error "Error running migration: $_"
        return $false
    }
}

function Confirm-Action {
    param(
        [string]$Message,
        [bool]$RequiresDowntime
    )
    
    Write-Warning $Message
    
    if ($RequiresDowntime) {
        Write-Warning "⚠️ THIS MIGRATION REQUIRES DOWNTIME ⚠️"
        Write-Host ""
    }
    
    $response = Read-Host "Type 'YES' to continue, anything else to abort"
    
    return ($response -eq "YES")
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

Write-Header "DATABASE MIGRATION RUNNER"

# Get migration metadata
$migrationMeta = $Migrations[$MigrationNumber]
$dbConnection = $DbConnections[$Environment]

Write-Info "Migration: $MigrationNumber - $($migrationMeta.name)"
Write-Info "Environment: $Environment"
Write-Info "Estimated time: $($migrationMeta.estimated_time)"
Write-Info "Requires downtime: $($migrationMeta.requires_downtime)"
Write-Info "Dry run: $DryRun"
Write-Info "Rollback: $Rollback"

# Pre-flight checks
Write-Header "PRE-FLIGHT CHECKS"

# Check if psql is available
if (-not (Get-Command psql -ErrorAction SilentlyContinue)) {
    Write-Error "psql command not found. Please install PostgreSQL client tools."
    exit 1
}

# Check if pg_dump is available
if (-not (Get-Command pg_dump -ErrorAction SilentlyContinue)) {
    Write-Error "pg_dump command not found. Please install PostgreSQL client tools."
    exit 1
}

# Get migration file
$migrationFile = Get-MigrationFile -MigrationNumber $MigrationNumber -IsRollback $Rollback

if (-not $migrationFile) {
    exit 1
}

Write-Success "Migration file found: $migrationFile"

# Test database connection
if (-not (Test-PostgresConnection -Connection $dbConnection)) {
    exit 1
}

# Dry run mode
if ($DryRun) {
    Write-Header "DRY RUN MODE"
    Write-Info "Would run: $migrationFile"
    Write-Info "On: $($dbConnection.host)"
    Write-Info "Database: $($dbConnection.database)"
    Write-Warning "No changes will be made (dry run mode)"
    exit 0
}

# Confirm action
Write-Header "CONFIRMATION"

$confirmMessage = "Are you sure you want to run this migration on $Environment?"

if (-not (Confirm-Action -Message $confirmMessage -RequiresDowntime $migrationMeta.requires_downtime)) {
    Write-Warning "Migration aborted by user"
    exit 0
}

# Create backup
Write-Header "BACKUP"

$backupFile = Backup-Database -Connection $dbConnection -MigrationNumber $MigrationNumber

if (-not $backupFile) {
    Write-Error "Backup failed. Aborting migration."
    exit 1
}

# Run migration
Write-Header "RUNNING MIGRATION"

$startTime = Get-Date

$success = Run-Migration -Connection $dbConnection -MigrationFile $migrationFile

$endTime = Get-Date
$duration = $endTime - $startTime

# Results
Write-Header "MIGRATION RESULTS"

if ($success) {
    Write-Success "Migration completed successfully!"
    Write-Info "Duration: $($duration.ToString('mm\:ss'))"
    Write-Info "Backup saved: $backupFile"
    
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Verify database state"
    Write-Host "2. Test application"
    Write-Host "3. Monitor for errors"
    
    if ($migrationMeta.requires_downtime) {
        Write-Host "4. Update application code (see CODE_UPDATE_GUIDE.md)"
        Write-Host "5. Deploy new application code"
    }
} else {
    Write-Error "Migration failed!"
    Write-Warning "Duration: $($duration.ToString('mm\:ss'))"
    Write-Warning "Backup saved: $backupFile"
    
    Write-Host "`nRollback options:" -ForegroundColor Yellow
    Write-Host "1. Restore from backup: pg_restore $backupFile"
    
    if ($migrationMeta.rollback_available) {
        Write-Host "2. Run rollback script: .\run-migration.ps1 -MigrationNumber $MigrationNumber -Environment $Environment -Rollback"
    } else {
        Write-Warning "No rollback script available for this migration"
    }
    
    exit 1
}

# ============================================================================
# END OF SCRIPT
# ============================================================================
