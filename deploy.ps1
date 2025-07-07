# PowerShell Deployment Script for Social Media Stats Dashboard
# Usage: .\deploy.ps1 [staging|production] [deploy|rollback|logs|status]

param(
    [Parameter(Position=0)]
    [ValidateSet("staging", "production")]
    [string]$Environment = "staging",
    
    [Parameter(Position=1)]
    [ValidateSet("deploy", "rollback", "logs", "status")]
    [string]$Action = "deploy"
)

# Configuration
$AppName = "social-stats"
$DeployPath = "C:\opt\$AppName-$Environment"
$BackupPath = "C:\opt\backups\$AppName-$Environment"

# Function to write colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to backup current deployment
function Backup-Current {
    if (Test-Path $DeployPath) {
        Write-Status "Creating backup of current deployment..."
        $BackupFile = "$BackupPath\backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip"
        New-Item -ItemType Directory -Force -Path $BackupPath | Out-Null
        Compress-Archive -Path "$DeployPath\*" -DestinationPath $BackupFile
        Write-Status "Backup created successfully: $BackupFile"
    }
}

# Function to check prerequisites
function Test-Prerequisites {
    Write-Status "Checking prerequisites..."
    
    if (-not (Test-Command "docker")) {
        Write-Error "Docker is not installed"
        exit 1
    }
    
    if (-not (Test-Command "docker-compose")) {
        Write-Error "Docker Compose is not installed"
        exit 1
    }
    
    if (-not (Test-Command "git")) {
        Write-Error "Git is not installed"
        exit 1
    }
    
    Write-Status "All prerequisites are satisfied"
}

# Function to setup environment
function Setup-Environment {
    Write-Status "Setting up environment for $Environment..."
    
    # Create deployment directory
    New-Item -ItemType Directory -Force -Path $DeployPath | Out-Null
    Set-Location $DeployPath
    
    # Clone or pull repository
    if (Test-Path ".git") {
        Write-Status "Pulling latest changes..."
        git pull origin main
    }
    else {
        Write-Status "Cloning repository..."
        git clone https://github.com/your-username/social-media-stats-dashboard.git .
    }
    
    # Create .env file if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Warning "Creating .env file from template..."
        Copy-Item "env.example" ".env"
        Write-Warning "Please update .env file with your configuration"
        exit 1
    }
    
    Write-Status "Environment setup completed"
}

# Function to build and deploy
function Deploy-Application {
    Write-Status "Building and deploying application..."
    
    Set-Location $DeployPath
    
    # Stop existing containers
    Write-Status "Stopping existing containers..."
    docker-compose down 2>$null
    
    # Build new images
    Write-Status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    Write-Status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    Write-Status "Waiting for services to be ready..."
    Start-Sleep -Seconds 30
    
    # Run database migrations
    Write-Status "Running database migrations..."
    docker-compose exec -T backend alembic upgrade head
    
    # Health check
    Write-Status "Performing health check..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Status "Health check passed"
        }
        else {
            throw "Health check failed with status: $($response.StatusCode)"
        }
    }
    catch {
        Write-Error "Health check failed: $_"
        docker-compose logs
        exit 1
    }
    
    Write-Status "Deployment completed successfully"
}

# Function to rollback
function Rollback-Deployment {
    Write-Warning "Rolling back deployment..."
    
    Set-Location $DeployPath
    
    # Stop current containers
    docker-compose down
    
    # Find latest backup
    $LatestBackup = Get-ChildItem -Path $BackupPath -Filter "backup-*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($LatestBackup) {
        Write-Status "Restoring from backup: $($LatestBackup.Name)"
        Expand-Archive -Path $LatestBackup.FullName -DestinationPath $DeployPath -Force
        docker-compose up -d
        Write-Status "Rollback completed"
    }
    else {
        Write-Error "No backup found for rollback"
        exit 1
    }
}

# Function to show logs
function Show-Logs {
    Write-Status "Showing application logs..."
    Set-Location $DeployPath
    docker-compose logs -f
}

# Function to show status
function Show-Status {
    Write-Status "Showing application status..."
    Set-Location $DeployPath
    docker-compose ps
}

# Function to cleanup old backups
function Cleanup-Backups {
    Write-Status "Cleaning up old backups (keeping last 5)..."
    $Backups = Get-ChildItem -Path $BackupPath -Filter "backup-*.zip" | Sort-Object LastWriteTime -Descending
    if ($Backups.Count -gt 5) {
        $Backups | Select-Object -Skip 5 | Remove-Item -Force
    }
}

# Main script logic
try {
    Write-Status "Starting deployment to $Environment environment"
    
    # Check if running as administrator
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Warning "Consider running as Administrator for full functionality"
    }
    
    switch ($Action) {
        "deploy" {
            Test-Prerequisites
            Backup-Current
            Setup-Environment
            Deploy-Application
            Cleanup-Backups
        }
        "rollback" {
            Rollback-Deployment
        }
        "logs" {
            Show-Logs
        }
        "status" {
            Show-Status
        }
        default {
            Write-Host "Usage: .\deploy.ps1 [staging|production] [deploy|rollback|logs|status]"
            Write-Host "  deploy   - Deploy the application (default)"
            Write-Host "  rollback - Rollback to previous version"
            Write-Host "  logs     - Show application logs"
            Write-Host "  status   - Show application status"
            exit 1
        }
    }
}
catch {
    Write-Error "Deployment failed: $_"
    exit 1
} 